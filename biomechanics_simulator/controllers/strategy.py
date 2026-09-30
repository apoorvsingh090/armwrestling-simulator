"""Strategy layer: technique selection + PD execution.

Two alternatives live here:
- StrategyController: EXPLICIT technique control (caller picks the technique).
- AIOpponent (ai_opponent.py, re-exported below): AUTONOMOUS behavior from
  sensory state only. Use explicit for scripted scenarios, autonomous opponents
  for fair matches.
"""
import warnings

from controllers.technique_controllers import TECHNIQUES
from controllers.ai_opponent import AIOpponent  # noqa: F401 (re-export: autonomous alternative)


class StrategyController:
    BASELINE = 0.5

    def __init__(self, technique_name, pd_controller, mode="OFFENSIVE"):
        if technique_name not in TECHNIQUES:
            raise ValueError(f"unknown technique {technique_name}")
        self.pd = pd_controller
        self.mode = mode
        self.switch_technique(technique_name)

    def switch_technique(self, new_technique):
        if new_technique not in TECHNIQUES:
            raise ValueError(f"unknown technique {new_technique}")
        self.technique = TECHNIQUES[new_technique]

    def decide_strategy(self, match_state):
        # MVP: hold the configured mode. Real opponent modeling: Milestone 9.
        warnings.warn("[Strategy] MVP state machine: mode held; no opponent modeling.",
                      UserWarning, stacklevel=2)
        return self.mode

    def compute_activations(self, match_state, dt):
        """match_state: {"joints": {dof: (q, w)}, "ma_args": {...}} for ONE athlete.
        Returns {registry_muscle: activation in [0,1]}. NOTHING else leaves."""
        targets = self.technique.targets_rad()
        if targets is None or self.mode == "DEFENSIVE":
            joints = match_state["joints"]
            targets = {d: (joints[d][0], 0.0) for d in joints}
        emph = self.technique.emphasis_mapped
        jt = {d: (targets[d][0], targets[d][1], emph) for d in targets if d in self.pd.joints}
        acts = self.pd.compute_activations(jt, {**match_state["joints"],
                                                "ma_args": match_state.get("ma_args", {})})
        if self.mode == "DEFENSIVE":
            for name in self.technique.emphasis_mapped:
                if name in acts:
                    acts[name] = min(1.0, max(acts[name], self.BASELINE))
        self._check_schema(acts)
        return acts

    @staticmethod
    def _check_schema(acts):
        for name, a in acts.items():
            if not isinstance(a, float) or not (0.0 <= a <= 1.0):
                raise ValueError(f"controller leaked non-activation for {name}: {a!r}")
