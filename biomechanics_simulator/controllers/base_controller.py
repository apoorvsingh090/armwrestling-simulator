"""Low-level controllers: activations ONLY. No forces, no torques applied.

Dependency rule (enforced by test_no_technique_bonus): this package has zero
imports from the physics engine. Controllers output dicts {muscle: float}
and the physics engine alone turns them into motion.
"""
import warnings


class BaseController:
    def __init__(self, muscles, joints):
        self.muscles = dict(muscles)
        self.joints = list(joints)

    def compute_activations(self, match_state, dt):
        raise NotImplementedError


class PDController(BaseController):
    """Per-DOF PD tracking with emphasis-weight redundancy resolution.

    tau_req[d] = Kp[d]*(target[d]-q[d]) + Kd[d]*(w_target[d]-w[d]).
    Direction-matched muscles (role sign == sign(tau_req)) share the load;
    each gets a_i = |tau_req| * weight_i / (Fmax_i * r_i), clamped [0,1].
    Zero-Fmax or zero-MA muscles are SKIPPED (cannot produce torque) and
    reported in skipped_last. Heuristic allocation (M9-flagged); exact
    torque matching is NOT claimed. Kp/Kd are engineering choices (required,
    documented at call sites), not physiology.
    """

    def __init__(self, muscles, moment_arms, Kp, Kd, dofs=("elbow", "forearm", "wrist_fe", "wrist_rud")):
        super().__init__(muscles, dofs)
        self.ma = dict(moment_arms)
        self.Kp = dict(Kp)
        self.Kd = dict(Kd)
        self.skipped_last = {}

    def required_torques(self, joint_targets, current_state):
        """Per-DOF PD torque demand (no allocation). Shared by emphasis
        allocation (below) and QP recruitment (AIOpponent)."""
        out = {}
        for dof in self.joints:
            if dof not in joint_targets:
                continue
            tq, tw, _ = joint_targets[dof]
            q, w = current_state[dof]
            out[dof] = self.Kp[dof] * (tq - q) + self.Kd[dof] * (tw - w)
        return out

    def compute_activations(self, joint_targets, current_state):
        """joint_targets: {dof: (target_q, target_w, emphasis{name:weight})}.
        current_state: {dof: (q, w), "ma_args": {...}} for MA callables.
        Returns {muscle: activation in [0,1]}."""
        out = {n: 0.0 for n in self.muscles}
        self.skipped_last = {}
        ma_args = current_state.get("ma_args", {})
        taus = self.required_torques(joint_targets, current_state)
        for dof, tau in taus.items():
            if tau == 0.0:
                continue
            _, _, emph = joint_targets[dof]
            sgn = 1.0 if tau > 0 else -1.0
            mag = abs(tau)
            for name, info in self.muscles.items():
                if info["roles"].get(dof, 0) != sgn:
                    continue
                r = self.ma[name][dof](**ma_args)
                fmax = info["Fmax"]
                if fmax <= 0 or r == 0.0:
                    self.skipped_last[name] = dof  # cannot produce torque
                    continue
                a = mag * emph.get(name, 0.0) / (fmax * r)
                out[name] = min(1.0, max(0.0, out[name] + a))
        for name in out:
            out[name] = min(1.0, max(0.0, out[name]))
        return out
