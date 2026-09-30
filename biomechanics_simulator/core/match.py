"""Two-athlete match (M5): grasp-coupled Simulations + pin detection.

Power consistency: contact torques use each sim's own grip lever; the grasp
lever MUST equal both (asserted) so F*v = tau*omega holds exactly.
Pin: plane crossing of lateral hand positions (FLAGGED proxy — real pin is
hand-wrist pad contact, M6 refinement). Default pin_x 0.15 m PROVISIONAL.
"""
import warnings

from core.hand_to_hand import HandToHandContact
from core.mirror import lateral_hand_position
from core.contact_detection import GripModel


class MatchSimulation:
    def __init__(self, athlete_A, athlete_B, table_planes=None,
                 friction_mu=None, tangential_k=None, tangential_c=None,
                 lever_m=None, pin_x_m=0.15,
                 max_grip_A=462.0, max_grip_B=462.0,
                 pin_pads=None, controller_A=None, controller_B=None):
        for label, v in (("friction_mu", friction_mu), ("tangential_k", tangential_k),
                         ("tangential_c", tangential_c), ("lever_m", lever_m)):
            if v is None:
                raise ValueError(f"{label} UNKNOWN for the grasp pair: pass explicit value")
        for sim, tag in ((athlete_A, "A"), (athlete_B, "B")):
            if abs(sim.lever_wg - lever_m) > 1e-15:
                raise ValueError(f"grasp lever must equal sim grip lever (power consistency), {tag}")
        self.A, self.B = athlete_A, athlete_B
        self.table = dict(table_planes) if table_planes else {}
        self.grasp = HandToHandContact(friction_mu, tangential_k, tangential_c, lever_m)
        self.grip_A = GripModel(max_grip_N=max_grip_A, mu=friction_mu)
        self.grip_B = GripModel(max_grip_N=max_grip_B, mu=friction_mu)
        self.lever = float(lever_m)
        self.pin_x = float(pin_x_m)
        warnings.warn("[Match] pin_x default 0.15m PROVISIONAL (elbow world position unmeasured).",
                      UserWarning, stacklevel=2)
        self.pin_pads = dict(pin_pads) if pin_pads else {}
        self.controller_A = controller_A
        self.controller_B = controller_B
        self.impulse_A = 0.0  # cumulative contact impulse bookkeeping (Newton audit)
        self.impulse_B = 0.0
        for label, v in (("friction_mu", friction_mu), ("tangential_k", tangential_k),
                         ("tangential_c", tangential_c), ("lever_m", lever_m)):
            if v is None:
                raise ValueError(f"{label} UNKNOWN for the grasp pair: pass explicit value")
        for sim, tag in ((athlete_A, "A"), (athlete_B, "B")):
            if abs(sim.lever_wg - lever_m) > 1e-15:
                raise ValueError(f"grasp lever must equal sim grip lever (power consistency), {tag}")
        self.A, self.B = athlete_A, athlete_B
        self.table = dict(table_planes) if table_planes else {}
        self.grasp = HandToHandContact(friction_mu, tangential_k, tangential_c, lever_m)
        self.grip_A = GripModel(max_grip_N=max_grip_A, mu=friction_mu)
        self.grip_B = GripModel(max_grip_N=max_grip_B, mu=friction_mu)
        self.lever = float(lever_m)
        self.pin_x = float(pin_x_m)
        warnings.warn("[Match] pin_x default 0.15m PROVISIONAL (elbow world position unmeasured).",
                      UserWarning, stacklevel=2)
        self.impulse_A = 0.0  # cumulative contact impulse bookkeeping (Newton audit)
        self.impulse_B = 0.0

    def hand_positions(self):
        return (lateral_hand_position(self.A.phi, self.lever, +1),
                lateral_hand_position(self.B.phi, self.lever, -1))

    def check_pin(self):
        x_A, x_B = self.hand_positions()
        if x_B > self.pin_x:
            return "A"  # B pinned at B's pad
        if x_A < -self.pin_x:
            return "B"  # A pinned at A's pad
        return None

    def pad_forces(self):
        """Pin-pad normal forces from lateral hand state (0.0 without pads).
        Hand lateral velocities: v_A = +L*wf_A, v_B = -L*wf_B (mirror)."""
        if not self.pin_pads:
            return {"A": 0.0, "B": 0.0}
        x_A, x_B = self.hand_positions()
        v_A = self.lever * self.A.omega_f
        v_B = -self.lever * self.B.omega_f
        return {"A": self.pin_pads["A"].contact(x_A, v_A)["Fn"] if "A" in self.pin_pads else 0.0,
                "B": self.pin_pads["B"].contact(x_B, v_B)["Fn"] if "B" in self.pin_pads else 0.0}

    def confirm_pin(self, side, force_N):
        """Force-gated pin confirmation (M6 refinement over plane crossing).
        side = the candidate PINNED hand ("B" = B's hand at B's pad).
        Returns the WINNER ("A" when B is pinned), or None.
        Threshold lives in that side's PinPad (caller policy, not physics)."""
        key = "A" if side == "A" else "B"
        if key not in self.pin_pads or self.pin_pads[key].threshold is None:
            return None  # no calibrated gate: geometric check_pin governs
        winner = "B" if side == "A" else "A"
        return winner if force_N > self.pin_pads[key].threshold else None

    def athlete_state(self, sim):        return {"joints": {"elbow": (sim.seg.theta, sim.seg.omega),
                           "forearm": (sim.phi, sim.omega_f),
                           "wrist_fe": (sim.phi_wfe, sim.omega_wfe),
                           "wrist_rud": (sim.phi_rud, sim.omega_rud)},
                "ma_args": {"theta": sim.seg.theta, "theta_f": sim.phi,
                            "theta_wfe": sim.phi_wfe, "theta_rud": sim.phi_rud}}

    def sensory_for(self, sim, opp_sim, side):
        """Build the sensory view for one athlete (values ONLY: positions,
        velocities, contact magnitude, own joints/fatigue, pin). No sim
        references escape — the anti-cheat boundary lives here."""
        from controllers.sensory import SensoryState
        x_self = self.lever * sim.phi * side
        v_self = self.lever * sim.omega_f * side
        v_opp = -self.lever * opp_sim.omega_f * side
        snap = sim.fatigue_snapshot()
        last = getattr(self, "_last_contact", None)
        return SensoryState(
            hand_position=x_self, hand_velocity=v_self,
            contact_force=abs(last["Ft_on_A"]) if last else 0.0,
            opponent_hand_velocity=v_opp,
            own_joint_angles=self.athlete_state(sim)["joints"],
            own_fatigue_fraction=max(snap.values()) if snap else 0.0,
            pin=self.check_pin())

    def _resolve_activations(self, which, explicit, dt):
        sim, opp, side = (self.A, self.B, +1) if which == "A" else (self.B, self.A, -1)
        ctrl = self.controller_A if which == "A" else self.controller_B
        if explicit is not None:
            return explicit, None
        if ctrl is None:
            raise ValueError(f"no activations and no controller_{which} (legacy explicit mode needs dicts)")
        if getattr(ctrl, "wants_sensory", False):
            acts = ctrl.compute_activations(self.sensory_for(sim, opp, side), dt)
        else:
            acts = ctrl.compute_activations(self.athlete_state(sim), dt)
        return acts, {"technique": getattr(ctrl, "last_technique", None)}

    def step(self, activations_A=None, activations_B=None, grip_A=1.0, grip_B=1.0,
             dt_check=True):
        dt = self.A.integrator.dt
        if dt_check and abs(self.B.integrator.dt - dt) > 0:
            raise ValueError("both athletes must share dt (deterministic lockstep)")
        activations_A, ai_A = self._resolve_activations("A", activations_A, dt)
        activations_B, ai_B = self._resolve_activations("B", activations_B, dt)
        Fn_A = self.grip_A.normal_force(grip_A)
        Fn_B = self.grip_B.normal_force(grip_B)
        v_rel = self.grasp.relative_velocity(self.A.omega_f, self.B.omega_f)
        con = self.grasp.compute(Fn_A, Fn_B, v_rel, dt)
        Ft_A, Ft_B = con["Ft_on_A"], con["Ft_on_B"]
        assert Ft_A == -Ft_B  # exact negation: Newton's third law to machine precision
        self.impulse_A += Ft_A * dt
        self.impulse_B += Ft_B * dt
        # Pin-pad reactions from PRE-step state (semi-implicit contact, documented).
        pad_F = {"A": 0.0, "B": 0.0}
        if self.pin_pads:
            x_A0, x_B0 = self.hand_positions()
            if "A" in self.pin_pads:
                pad_F["A"] = self.pin_pads["A"].contact(
                    x_A0, self.lever * self.A.omega_f)["Fn"]
            if "B" in self.pin_pads:
                pad_F["B"] = self.pin_pads["B"].contact(
                    x_B0, -self.lever * self.B.omega_f)["Fn"]
        # Local-frame roll torques: tau_roll,A = +F_A*L; tau_roll,B = -F_B*L
        # (B's minus = MirrorTransform forearm -1; power: tau_A*w_A + tau_B*w_B = Ft_A*v_rel).
        # Pad reactions mapped identically (pad force is global-signed like grasp force).
        pad_A_dict = pad_F["A"]  # pad pushes A's hand +x = A's pronation+ direction
        # Pad pushes B's hand -x; dict convention (M5) is Ft_roll = -F_on_B:
        pad_B_dict = pad_F["B"]  # = -(-pad_F): drives B pronation+ i.e. x_B back down
        st_A = self.A.step(activations_A, 0.0, grip_activation=grip_A,
                           tangential_demand_N=abs(Ft_A),
                           contact={"Ft_roll": Ft_A + pad_A_dict, "Ft_flex": 0.0, "Ft_lat": 0.0})
        st_B = self.B.step(activations_B, 0.0, grip_activation=grip_B,
                           tangential_demand_N=abs(Ft_B),
                           contact={"Ft_roll": -Ft_B + pad_B_dict, "Ft_flex": 0.0, "Ft_lat": 0.0})
        pin_geo = self.check_pin()
        pin = pin_geo
        if pin_geo is not None and self.pin_pads:
            side = "B" if pin_geo == "A" else "A"  # candidate PINNED hand
            force = pad_F[side]
            gated = self.confirm_pin(side, force)
            pin = gated if gated is not None or self._gate_active() else pin_geo
        self._last_contact = con
        return {"A": st_A, "B": st_B, "contact": con, "pin": pin,
                "pad_F_A": pad_F["A"], "pad_F_B": pad_F["B"],
                "lift_A": False, "lift_B": False,  # no vertical elbow state exists (M6 note)
                "ai_A": ai_A, "ai_B": ai_B,  # decision records (None for explicit/legacy)
                "x_A": lateral_hand_position(self.A.phi, self.lever, +1),
                "x_B": lateral_hand_position(self.B.phi, self.lever, -1)}

    def _gate_active(self):
        return (bool(self.pin_pads)
                and all(self.pin_pads[k].threshold is not None for k in self.pin_pads))

    def run_match(self, duration_s, schedule_A, schedule_B, grip_A=1.0, grip_B=1.0):
        n = int(round(duration_s / self.A.integrator.dt))
        hist = []
        for i in range(n + 1):
            t = i * self.A.integrator.dt
            gA = grip_A(t) if callable(grip_A) else grip_A
            gB = grip_B(t) if callable(grip_B) else grip_B
            st = self.step(schedule_A(t), schedule_B(t), gA, gB)
            hist.append({"t": t, **st})
            if st["pin"] is not None:
                break
        return hist

    def fatigue_report(self):
        """Per-athlete capacity report (REPORTING ONLY: no thresholds, no logic
        gates, no hidden recovery paths - a tired athlete simply produces less
        torque through the Hill equation, and the physics decides the rest)."""
        out = {}
        for tag, sim in (("A", self.A), ("B", self.B)):
            snap = sim.fatigue_snapshot()
            out[tag] = {"fraction": dict(snap),
                        "max_fraction": max(snap.values()) if snap else 0.0,
                        "mean_fraction": (sum(snap.values()) / len(snap)) if snap else 0.0}
        return out
