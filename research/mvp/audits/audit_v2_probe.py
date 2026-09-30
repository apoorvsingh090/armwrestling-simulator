import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from biomech.simulation import ElbowSimulation, SimConfig
DEG = 180.0 / math.pi
tr2 = ElbowSimulation(SimConfig(dt=0.002, duration_s=0.35)).run()
trr = ElbowSimulation(SimConfig(dt=0.00025, duration_s=0.35)).run()
print("coarse 2ms around engagement:")
for i in range(len(tr2.t)):
    if 0.265 <= tr2.t[i] <= 0.285:
        print(f"t={tr2.t[i]:.4f} th={tr2.theta[i]*DEG:.3f} om={tr2.omega[i]:.3f} "
              f"tau={tr2.tau_net[i]:.3f} fb={tr2.f_bic[i]:.1f} ft={tr2.f_tri[i]:.1f}")
print("fine 0.25ms around engagement:")
for j in range(len(trr.t)):
    if 0.265 <= trr.t[j] <= 0.285 and j % 4 == 0:
        print(f"t={trr.t[j]:.4f} th={trr.theta[j]*DEG:.3f} om={trr.omega[j]:.3f} "
              f"tau={trr.tau_net[j]:.3f} fb={trr.f_bic[j]:.1f} ft={trr.f_tri[j]:.1f}")
