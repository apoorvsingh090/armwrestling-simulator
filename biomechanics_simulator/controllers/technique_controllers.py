"""Technique definitions: joint targets (deg) + emphasis weights ONLY.

No forces, torques, multipliers, or scripts. Brief muscle names map to registry
names below; names with NO object in the model (brachialis, finger flexors,
pectoralis) are recorded in `unmapped` and ignored by the control layer with a
warning — never silently, never invented.
"""
import math
import warnings

REGISTRY_MAP = {
    "biceps_brachii": "biceps_long",
    "triceps_brachii": "triceps_long",
    "pronator_teres": "pronator_teres",
    "brachioradialis": "brachioradialis",
    "fcr": "fcr_flexor_carpi_radialis",
    "fcu": "fcu_flexor_carpi_ulnaris",
    "ecr": "ecr_extensor_carpi_radialis",
    "ecu": "ecu_extensor_carpi_ulnaris",
    "brachialis": None,       # no object in model (R2: brachialis fit exists but unwired)
    "finger_flexors": None,   # no objects in model (D-06)
    "pectoralis": None,       # no object in model (shoulder scope)
}


class TechniqueDefinition:
    def __init__(self, name, joint_targets_deg, muscle_emphasis):
        """joint_targets_deg: {dof: (target_deg, target_vel)} or None (hold).
        muscle_emphasis: {brief_name: weight}."""
        self.name = name
        self.targets_deg = dict(joint_targets_deg) if joint_targets_deg else None
        self.emphasis_brief = dict(muscle_emphasis)
        self.emphasis_mapped = {}
        self.unmapped = []
        for brief, w in muscle_emphasis.items():
            reg = REGISTRY_MAP.get(brief)
            if reg is None:
                self.unmapped.append(brief)
                warnings.warn(f"[Technique:{name}] '{brief}' has no model object: emphasis ignored.",
                              UserWarning, stacklevel=2)
            else:
                self.emphasis_mapped[reg] = float(w)

    def targets_rad(self):
        if self.targets_deg is None:
            return None
        return {d: (v[0] * math.pi / 180.0, v[1]) for d, v in self.targets_deg.items()}


TOP_ROLL = TechniqueDefinition(
    "top_roll",
    {"forearm": (45.0, 0.0), "wrist_fe": (-5.0, 0.0), "wrist_rud": (10.0, 0.0), "elbow": (90.0, 0.0)},
    {"pronator_teres": 1.0, "fcr": 0.6, "biceps_brachii": 0.3, "brachioradialis": 0.4})

HOOK = TechniqueDefinition(
    "hook",
    {"forearm": (0.0, 0.0), "wrist_fe": (60.0, 0.0), "wrist_rud": (-15.0, 0.0), "elbow": (100.0, 0.0)},
    {"fcu": 1.0, "biceps_brachii": 0.8, "brachialis": 0.7, "pronator_teres": 0.3})

PRESS = TechniqueDefinition(
    "press",
    {"forearm": (20.0, 0.0), "wrist_fe": (0.0, 0.0), "wrist_rud": (0.0, 0.0), "elbow": (60.0, 0.0)},
    {"triceps_brachii": 1.0, "brachioradialis": 0.5, "fcr": 0.3})

DEFENSIVE = TechniqueDefinition(
    "defensive", None,
    {"biceps_brachii": 0.5, "triceps_brachii": 0.5, "pronator_teres": 0.5,
     "fcu": 0.5, "fcr": 0.5})

TECHNIQUES = {"top_roll": TOP_ROLL, "hook": HOOK, "press": PRESS, "defensive": DEFENSIVE}
