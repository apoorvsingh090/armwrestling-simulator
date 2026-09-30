import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from biomech.simulation import ElbowSimulation, SimConfig
DEG = 180.0 / math.pi
# drive hard into anatomical extension stop: start near 0, full triceps
tr = ElbowSimulation(SimConfig(dt=0.001, duration_s=1.0, theta0_rad=math.radians(10),
                               u_biceps=0.0, u_triceps=1.0, gravity_on=False)).run()
print("extension-stop probe: min theta=%.3fdeg omega-at-min=%.3f rad/s final th=%.3f om=%.3f" % (
    min(tr.theta)*DEG, tr.omega[tr.theta.index(min(tr.theta))], tr.theta[-1]*DEG, tr.omega[-1]))
# drive into flexion stop
tr2 = ElbowSimulation(SimConfig(dt=0.001, duration_s=2.0, theta0_rad=math.radians(140),
                                u_biceps=1.0, u_triceps=0.0, gravity_on=False)).run()
i = tr2.theta.index(max(tr2.theta))
print("flexion-stop probe: max theta=%.3fdeg omega-at-max=%.3f rad/s final th=%.3f om=%.3f" % (
    max(tr2.theta)*DEG, tr2.omega[i], tr2.theta[-1]*DEG, tr2.omega[-1]))
