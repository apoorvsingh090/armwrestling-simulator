import math, os, sys, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests"))
warnings.simplefilter("ignore")
from helpers_4dof import build_4dof_sim
from core.match import MatchSimulation
from core.contact_detection import load_table_planes

BASE = os.path.join(os.path.dirname(__file__), "..")


def run(gA, gB, actsA, actsB, T=2.0):
    A, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.002)
    B, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.002)
    m = MatchSimulation(A, B, load_table_planes(os.path.join(BASE, "data", "r3_hand_contact_spec.json")),
                        friction_mu=0.5, tangential_k=2000.0, tangential_c=5.0,
                        lever_m=0.08, pin_x_m=0.05)
    h = m.run_match(T, lambda t: actsA, lambda t: actsB, gA, gB)
    last = h[-1]
    slips = sum(1 for s in h if s["contact"]["slipped"])
    print("gA=%s gB=%s actsA=%s steps=%d pin=%s xB=%.4f slipped=%d/%d Fn=%.1f" % (
        gA, gB, actsA, len(h), last["pin"], last["x_B"], slips, len(h), last["contact"]["Fn"]))


run(1.0, 1.0, {"pronator_teres": 0.2}, {}, 2.0)
run(1.0, 0.02, {"pronator_teres": 1.0}, {}, 2.0)
run(1.0, 1.0, {}, {}, 1.0)
run(1.0, 0.02, {"pronator_teres": 1.0}, {"biceps_long": 0.15}, 2.0)
run(1.0, 1.0, {"pronator_teres": 1.0}, {"biceps_long": 0.15}, 2.0)
run(1.0, 0.02, {"pronator_teres": 1.0}, {"biceps_long": 0.3}, 3.0)
run(1.0, 0.02, {"pronator_teres": 1.0}, {"biceps_long": 1.0}, 3.0)
