"""Shared M9 builders: recruitment inputs + live MA resolver (no sim imports
in controllers/ — resolution happens here, test-side)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

DOFS = ("elbow", "forearm", "wrist_fe", "wrist_rud")
KP = {"elbow": 50.0, "forearm": 2.0, "wrist_fe": 1.0, "wrist_rud": 1.0}
KD = {"elbow": 5.0, "forearm": 0.2, "wrist_fe": 0.1, "wrist_rud": 0.1}


def elbow_only_inputs():
    muscles = {"biceps_long": {"Fmax": 485.8, "roles": {"elbow": 1}},
               "triceps_long": {"Fmax": 1580.6, "roles": {"elbow": -1}},
               "brachioradialis": {"Fmax": 60.0, "roles": {"elbow": 1}},
               "pronator_teres": {"Fmax": 55.0, "roles": {"elbow": 1}}}
    ma = {"biceps_long": {"elbow": 0.046}, "triceps_long": {"elbow": 0.023},
          "brachioradialis": {"elbow": 0.072}, "pronator_teres": {"elbow": 0.010}}
    return muscles, ma


def live_ma_resolver(sim):
    def resolve(joints):
        th = joints["elbow"][0]
        ph = joints["forearm"][0]
        out = {}
        for name in sim.muscles:
            e = sim.mt[name]
            d = {}
            if e["elbow"] is not None:
                d["elbow"] = e["elbow"](th)
            if e["forearm"] is not None:
                d["forearm"] = e["forearm"](th, ph)
            if e["wfe"] is not None:
                d["wrist_fe"] = e["wfe"]()
            if e["wrud"] is not None:
                d["wrist_rud"] = e["wrud"]()
            out[name] = d
        return out
    return resolve


def muscle_roles(sim):
    return {n: {"Fmax": m.Fmax_N,
                "roles": {"elbow": sim.roles.get(n, 0.0),
                          "forearm": sim.f_roles.get(n, 0.0),
                          "wrist_fe": sim.wfe_roles.get(n, 0.0),
                          "wrist_rud": sim.wrud_roles.get(n, 0.0)}}
            for n, m in sim.muscles.items()}


def neutral_sensory(**kw):
    from controllers.sensory import SensoryState
    base = {"hand_position": 0.0, "hand_velocity": 0.0, "contact_force": 0.0,
            "opponent_hand_velocity": 0.0,
            "own_joint_angles": {"elbow": (1.5708, 0.0), "forearm": (0.0, 0.0),
                                 "wrist_fe": (0.0, 0.0), "wrist_rud": (0.0, 0.0)},
            "own_fatigue_fraction": 0.0, "pin": None}
    base.update(kw)
    return SensoryState(**base)
