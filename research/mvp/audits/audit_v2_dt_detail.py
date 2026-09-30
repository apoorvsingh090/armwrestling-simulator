import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from biomech.simulation import ElbowSimulation, SimConfig
DEG = 180.0 / math.pi
cfgs = {"2ms": SimConfig(dt=0.002, duration_s=3.0), "1ms": SimConfig(dt=0.001, duration_s=3.0),
        "0.5ms": SimConfig(dt=0.0005, duration_s=3.0), "0.25ms": SimConfig(dt=0.00025, duration_s=3.0)}
traces = {k: ElbowSimulation(c).run() for k, c in cfgs.items()}
ref = traces["0.25ms"]
for k in ("2ms", "1ms", "0.5ms"):
    dt = cfgs[k].dt; tr = traces[k]
    worst = (0, 0, 0, 0)  # t, dth, dom, dtau at max dtau
    dth_e = dom_e = 0.0  # max diffs while both below 129deg (pre-restraint)
    for t in ref.t:
        j = int(round(t / 0.00025)); i = int(round(t / dt))
        dta = abs(tr.tau_net[i] - ref.tau_net[j])
        if dta > worst[3]:
            worst = (t, abs(tr.theta[i]-ref.theta[j]), abs(tr.omega[i]-ref.omega[j]), dta)
        if tr.theta[i] < math.radians(129) and ref.theta[j] < math.radians(129):
            dth_e = max(dth_e, abs(tr.theta[i]-ref.theta[j]))
            dom_e = max(dom_e, abs(tr.omega[i]-ref.omega[j]))
    print(f"{k}: max|dtau|={worst[3]:.3f}Nm at t={worst[0]:.4f}s "
          f"(dth={worst[1]*DEG:.3f}deg dom={worst[2]:.4f}rad/s); "
          f"pre-restraint max|dth|={dth_e*DEG:.4f}deg max|dom|={dom_e:.5f}rad/s")
# restraint engagement time at baseline
tr = traces["1ms"]
for i, th in enumerate(tr.theta):
    if th >= math.radians(130):
        print("baseline crosses 130deg at t=", round(tr.t[i], 4), "s"); break
