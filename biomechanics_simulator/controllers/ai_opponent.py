"""Autonomous opponent: sense (delayed) -> transition -> PD targets ->
QP recruitment -> fatigue scaling -> activations. NOTHING else leaves.

wants_sensory=True lets MatchSimulation feed a SensoryState instead of raw
dicts. ma_resolver(state)->{name:{dof:r}} is caller-supplied (reads live
tables; no sim import here — dependency rule).
PROVISIONALS: reaction_time 0.2 s; fatigue threshold 0.3 / factor 0.7.
"""
import warnings

from controllers.base_controller import PDController
from controllers.sensory import SensoryState
from controllers.recruitment import MuscleRecruitment
from controllers.reaction import ReactionDelay
from controllers.transitions import TechniqueTransitioner
from controllers.technique_controllers import TECHNIQUES


def scale_for_fatigue(acts, fraction, threshold=0.3, factor=0.7):
    if fraction > threshold:
        return {n: a * factor for n, a in acts.items()}
    return dict(acts)


class AIOpponent:
    wants_sensory = True

    def __init__(self, muscles, ma_resolver, technique="top_roll", reaction_time=0.2,
                 Kp=None, Kd=None, dofs=("elbow", "forearm", "wrist_fe", "wrist_rud"),
                 side=+1, fatigue_threshold=0.3, fatigue_factor=0.7, baseline=0.1):
        self.muscles = dict(muscles)
        self.ma_resolver = ma_resolver
        self.pd = PDController({n: {} for n in muscles}, {},
                               dict(Kp or {}), dict(Kd or {}), dofs)
        for d in dofs:
            if d not in self.pd.Kp or d not in self.pd.Kd:
                raise ValueError(f"Kp/Kd required per DOF (missing {d})")
        self.recruit = MuscleRecruitment(
            {n: {"Fmax": m["Fmax"], "roles": m["roles"]} for n, m in muscles.items()}, list(dofs))
        self.delay = ReactionDelay(reaction_time)
        self.transitions = TechniqueTransitioner(side=side, initial=technique)
        self.fatigue_threshold = float(fatigue_threshold)
        self.fatigue_factor = float(fatigue_factor)
        self.baseline = float(baseline)
        self._t = 0.0
        self.last_technique = technique
        self.last_decision = {}
        warnings.warn("[AI] PROVISIONALS: reaction_time, fatigue threshold/factor, transition timings.",
                      UserWarning, stacklevel=2)

    def reset(self):
        self.delay.reset()
        self.transitions.reset()
        self._t = 0.0
        self.last_decision = {}

    def compute_activations(self, sensory_state, dt):
        if not isinstance(sensory_state, SensoryState):
            raise ValueError("AIOpponent consumes SensoryState only (no cheat path)")
        self._t += dt
        self.delay.buffer(sensory_state, self._t)
        delayed = self.delay.get_delayed(self._t)
        tech = self.transitions.decide(delayed, dt)
        self.last_technique = tech
        definition = TECHNIQUES[tech]
        joints = dict(delayed.own_joint_angles)
        targets = definition.targets_rad()
        if targets is None:
            targets = {d: (joints[d][0], 0.0) for d in joints}
        jt = {d: (targets[d][0], targets[d][1], {}) for d in targets if d in self.pd.joints}
        taus = self.pd.required_torques(jt, joints)
        r = self.ma_resolver(joints)
        acts = self.recruit.solve(taus, r, baseline=self.baseline)
        acts = scale_for_fatigue(acts, delayed.own_fatigue_fraction,
                                 self.fatigue_threshold, self.fatigue_factor)
        for n in acts:
            acts[n] = min(1.0, max(0.0, float(acts[n])))
        self.last_decision = {"technique": tech, "torques": dict(taus)}
        return acts
