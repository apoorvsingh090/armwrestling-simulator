"""Shared validation fixtures: consistency context, cross-val rows, demo match."""
import math
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

warnings.simplefilter("ignore")

from controllers.recruitment import MuscleRecruitment
from actuators.hill_muscle import HillMuscle
from core.hand_to_hand import HandToHandContact
from helpers_4dof import build_4dof_sim
from helpers_match import build_match

DEG = math.pi / 180.0


def consistency_ctx():
    muscles = {"biceps_long": {"Fmax": 485.8, "roles": {"elbow": 1}},
               "triceps_long": {"Fmax": 1580.6, "roles": {"elbow": -1}},
               "brachioradialis": {"Fmax": 60.0, "roles": {"elbow": 1}},
               "pronator_teres": {"Fmax": 55.0, "roles": {"elbow": 1}}}
    ma = {"biceps_long": {"elbow": 0.046}, "triceps_long": {"elbow": 0.023},
          "brachioradialis": {"elbow": 0.072}, "pronator_teres": {"elbow": 0.010}}
    sim, _ = build_4dof_sim()
    return {"recruitment": MuscleRecruitment(muscles, ["elbow"]),
            "torque_req": {"elbow": 5.0}, "ma_state": ma,
            "muscle_factory": lambda kf, kr: HillMuscle(
                name="t", Fmax_N=500.0, Lopt_m=0.1, kf=kf, kr=kr),
            "passive_curve": sim.wp_fe, "angles_deg": [40.0, -50.0, -20.0],
            "contact_obj": HandToHandContact(0.5, 2000.0, 5.0, 0.08),
            "match_factory": build_match}


def ma_rows(sim):
    th = lambda d: d * DEG
    return {
        "biceps_peak": {"get": sim.ma["biceps_long"], "at": th(110), "pub": 0.047,
                        "note": "E:P038 anchor; pipeline-fidelity (circular), not independent validation"},
        "triceps_peak": {"get": sim.ma["triceps_long"], "at": th(90), "pub": 0.023,
                         "note": "E:P041 anchor; circular (see above)"},
        "brd_peak": {"get": sim.mt["brachioradialis"]["elbow"], "at": th(110), "pub": 0.077,
                     "note": "E:P039 anchor; circular"},
        # PT rotation has NO published magnitude (0.5/0.75/1.2 dispute): no row manufactured.
    }


def rom_rows(sim):
    return {
        "elbow": ((0.0, sim.joint.anat_max), (0.0, 145 * DEG), "E:P006; circular (stops built from it)"),
        "forearm": ((sim.f_joint.anat_min, sim.f_joint.anat_max), (-87 * DEG, 80 * DEG),
                    "E:P010/P011 upper ends; circular"),
        "wrist_fe": ((sim.wfe_joint.anat_min, sim.wfe_joint.anat_max), (-70 * DEG, 80 * DEG),
                     "E:P013/P014; circular"),
        "wrist_rud": ((sim.wrud_joint.anat_min, sim.wrud_joint.anat_max), (-30 * DEG, 20 * DEG),
                      "E:P015; circular"),
    }


def force_rows():
    return {
        "biceps_long": (485.8, 4.6, 50.0, "FAIL exposes R2 bundle-map conflict (Seth vs PCSA x PROV-01)"),
        "brachioradialis": (60.0, 1.2, 50.0, "PASS is circular (derived the same way)"),
        "pronator_teres": (55.0, 1.1, 50.0, "PASS is circular (derived the same way)"),
        "triceps_long": (1580.6, 10.3, 50.0, "FAIL exposes R2 bundle-map conflict"),
    }
