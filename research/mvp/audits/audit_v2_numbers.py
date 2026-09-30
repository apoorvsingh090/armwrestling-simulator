"""Audit V2 numerics: MA shape check, dt sweep, OAT sensitivity.
Prints tables for MVP_AUDIT_V2.md. No model changes here.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from biomech.moment_arm import MomentArmProvisional
from biomech.muscle import Biceps, Triceps
from biomech.simulation import ElbowSimulation, SimConfig
from biomech.activation import ZajacActivation
from biomech.joint import ElbowJoint
from biomech.dynamics import ElbowDynamics

DEG = 180.0 / math.pi

print("=== A2: moment-arm shape ===")
ma = MomentArmProvisional()
for deg in (0, 5, 30, 60, 72.8, 90, 130, 140, 145):
    th = math.radians(deg)
    print(f"th={deg:6.1f} bic={ma.biceps(th)*100:.4f}cm tri={ma.triceps(th)*100:.4f}cm "
          f"extrap={ma.is_extrapolated(th)}")
th90 = math.radians(90)
print("tri@90 vs peak:", (ma.peak_tri - ma.triceps(th90)) / ma.peak_tri * 100, "% below peak")
print("bic variation (max-min)/max over 0..145:",
      (ma.biceps(th90) - ma.biceps(0.0)) / ma.biceps(th90) * 100, "%")
# derivative smoothness: max |d2| via finite diff
import numpy as np
ths = np.linspace(0, math.radians(145), 2001)
b = np.array([ma.biceps(t) for t in ths])
d1 = np.gradient(b, ths)
d2 = np.gradient(d1, ths)
print("bic max|dMA/dth| =", np.max(np.abs(d1)), "m/rad; max|d2| =", np.max(np.abs(d2)))

print("\n=== A8: dt sweep (common grid 0.25ms) ===")
cfgs = {"2ms": SimConfig(dt=0.002, duration_s=3.0), "1ms": SimConfig(dt=0.001, duration_s=3.0),
        "0.5ms": SimConfig(dt=0.0005, duration_s=3.0), "0.25ms": SimConfig(dt=0.00025, duration_s=3.0)}
traces = {k: ElbowSimulation(c).run() for k, c in cfgs.items()}
ref = traces["0.25ms"]
# resample each trace onto ref time grid by nearest index (all grids divide 0.25ms evenly? 2ms/0.25=8 yes)
def on_grid(tr, dt, t):
    i = int(round(t / dt))
    return tr.theta[i], tr.omega[i], tr.tau_net[i]
for k in ("2ms", "1ms", "0.5ms"):
    dt = cfgs[k].dt
    tr = traces[k]
    dth = dom = dta = 0.0
    for t in ref.t:
        th_r, om_r, ta_r = ref.theta[int(round(t / 0.00025))], ref.omega[int(round(t / 0.00025))], ref.tau_net[int(round(t / 0.00025))]
        th, om, ta = on_grid(tr, dt, t)
        dth = max(dth, abs(th - th_r)); dom = max(dom, abs(om - om_r)); dta = max(dta, abs(ta - ta_r))
    print(f"{k} vs 0.25ms: max|dth|={dth*DEG:.4f}deg max|dom|={dom:.5f}rad/s max|dtau|={dta:.5f}Nm")
print("final angles:", {k: round(tr.theta[-1]*DEG, 3) for k, tr in traces.items()})

print("\n=== A9: OAT sensitivity (-20%/base/+20%), 3s scenario ===")
def metrics(tr):
    return tr.theta[-1]*DEG, max(abs(o) for o in tr.omega)
base = ElbowSimulation(SimConfig()).run()
b_ang, b_pk = metrics(base)
print(f"BASELINE: final={b_ang:.3f}deg peak|om|={b_pk:.4f}rad/s")
def run_variant(**kw):
    mode = kw.pop("mode")
    if mode == "fmax":
        f = kw["f"]
        sim = ElbowSimulation(SimConfig(),
                              biceps=Biceps(specific_tension_N_per_cm2=50*f),
                              triceps=Triceps(specific_tension_N_per_cm2=50*f))
    elif mode == "sigfl":
        f = kw["f"]
        sim = ElbowSimulation(SimConfig(), biceps=Biceps(fl_width_frac=0.30*f),
                              triceps=Triceps(fl_width_frac=0.30*f))
    elif mode == "vmax":
        f = kw["f"]
        sim = ElbowSimulation(SimConfig(), biceps=Biceps(vmax_lopt_per_s=10*f),
                              triceps=Triceps(vmax_lopt_per_s=10*f))
    elif mode == "ma_amp":
        f = kw["f"]
        sim = ElbowSimulation(SimConfig(), moment_arm=MomentArmProvisional(
            peak_biceps_m=0.047*f, peak_triceps_m=0.023*f))
    elif mode == "ma_shape":
        f = kw["f"]
        m = MomentArmProvisional()
        import types
        # scale variable part of shape: bic 0.35->0.35*f recentred to keep peak=1 at 90deg:
        # shape = 1 - A*(1-sin); A=0.35 base. tri: 1 - B*(1-sin(+0.3)); B=0.30 base.
        A, B = 0.35*f, 0.30*f
        m._bic_shape = staticmethod(lambda th, A=A: 1.0 - A*(1.0-math.sin(th)))
        m._tri_shape = staticmethod(lambda th, B=B: 1.0 - B*(1.0-math.sin(th+0.3)))
        sim = ElbowSimulation(SimConfig(), moment_arm=m)
    elif mode == "inertia":
        sim = ElbowSimulation(SimConfig(), dynamics=ElbowDynamics(inertia=0.06*kw["f"]))
    elif mode == "damping":
        sim = ElbowSimulation(SimConfig(), dynamics=ElbowDynamics(damping=0.3*kw["f"]))
    elif mode == "restr":
        sim = ElbowSimulation(SimConfig(), joint=ElbowJoint(restraint_k=15*kw["f"]))
    return metrics(sim.run())
for name, mode in (("Fmax","fmax"), ("sigma_FL","sigfl"), ("v_max","vmax"),
                   ("MA amplitude","ma_amp"), ("MA shape","ma_shape"),
                   ("inertia","inertia"), ("damping","damping"),
                   ("restraint k","restr")):
    row = []
    for f in (0.8, 1.0, 1.2):
        a, p = run_variant(mode=mode, f=f)
        row.append(f"({a:.2f}d,{p:.3f}r/s)")
    print(f"{name:12s} -20%: {row[0]}  base: {row[1]}  +20%: {row[2]}")
