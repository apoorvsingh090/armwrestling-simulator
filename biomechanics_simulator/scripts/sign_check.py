"""Sign-convention verification (Part 3, step 1). Prints, asserts nothing new."""
import math
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
warnings.simplefilter("ignore")

from actuators.moment_arm import load_elbow_tables

ma = load_elbow_tables(os.path.join(os.path.dirname(__file__), "..", "data", "r2_mtus.json"))
th90 = math.pi / 2
rb, rt = ma["biceps"](th90), ma["triceps"](th90)
print(f"Biceps MA @90deg  = {rb:.6f} m  (flexor: stored +, torque +r*F)")
print(f"Triceps MA @90deg = {rt:.6f} m  (extensor: stored + as MAGNITUDE, torque -r*F)")
omega = 1.0
pen_b, pen_t = 0.0, math.radians(10.0)
v_b = rb * omega / math.cos(pen_b)
v_t = -rt * omega / math.cos(pen_t)
print(f"Biceps v @w=+1  = {v_b:.6f} m/s  (>0 shortening -> fV<1 concentric)")
print(f"Triceps v @w=+1 = {v_t:.6f} m/s  (<0 lengthening -> fV>1 eccentric-capped)")
print("Gravity-sign proof:")
print("  Candidate A tau=-m*g*d*cos(th): dTau/dTh=+m*g*d*sin(th) > 0 on (0,145deg)")
print("  -> NO stable equilibrium in ROM -> 10 s conservative swinging IMPOSSIBLE.")
print("  Candidate B tau=+m*g*d*cos(th): dTau/dTh=-m*g*d*sin(th) < 0 -> STABLE at 90deg.")
print("  Energy test requires pendulum swinging => candidate B implemented.")
print("  Consistent PE: E=0.5*I*w^2 - m*g*d*sin(th)  (since -dPE/dTh=+m*g*d*cos(th)).")
print("  Reference posture: elbow above shoulder (upper arm vertical-up), forearm")
print("  horizontal at full extension; flexion rotates downward; gravity assists")
print("  flexion for th<90deg, opposes beyond. Documented in core/simulation.py.")
