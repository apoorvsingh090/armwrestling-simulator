import math, os, sys, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests"))
warnings.simplefilter("ignore")
from helpers_4dof import build_4dof_sim
from core.match import MatchSimulation
from core.contact_detection import load_table_planes

BASE = os.path.join(os.path.dirname(__file__), "..")
A, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.002)
B, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.002)
m = MatchSimulation(A, B, load_table_planes(os.path.join(BASE, "data", "r3_hand_contact_spec.json")),
                    friction_mu=0.5, tangential_k=2000.0, tangential_c=5.0,
                    lever_m=0.08, pin_x_m=0.05, max_grip_A=462.0, max_grip_B=462.0)
actsA = {"pronator_teres": 1.0}
actsB = {}
hist = m.run_match(5.0, lambda t: actsA, lambda t: actsB, 1.0, 0.3)
last = hist[-1]
print(f"steps={len(hist)} pin={last['pin']} xA={last['x_A']:.4f} xB={last['x_B']:.4f}")
print(f"phiA={A.phi*57.3:.1f} phiB={B.phi*57.3:.1f} slipped_end={last['contact']['slipped']}")
print(f"impulseA={m.impulse_A:.4f} impulseB={m.impulse_B:.4f} sum={m.impulse_A+m.impulse_B:.2e}")
slips = sum(1 for s in hist if s["contact"]["slipped"])
print(f"slipped steps: {slips}/{len(hist)}")
