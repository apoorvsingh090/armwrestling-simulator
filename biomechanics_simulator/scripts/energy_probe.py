import math, os, sys, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
warnings.simplefilter("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests"))
from test_energy_conservation import make_gravity_only
import math as _m
sim = make_gravity_only()
hist = sim.run(10.0, lambda t: {"biceps_long": 0.0, "triceps_long": 0.0})
E0N = _m.exp(1.0) - 1.0
def elastic(th):
    states = sim.compute_muscle_state(th, 0.0)
    v = 0.0
    for name, mus in sim.muscles.items():
        L, _ = states[name]
        u = max(0.0, (L - mus.Lopt_m) / (mus.Lopt_m * (mus.passive_eps0 - 1.0)))
        v += mus.Fmax_N * mus.Lopt_m * (mus.passive_eps0 - 1.0) / E0N * (_m.exp(u) - u - 1.0)
    return v
m, g, d, I = 1.5, sim.g, 0.18, 0.06
E = [0.5*I*s["omega"]**2 - m*g*d*_m.sin(s["theta"]) + elastic(s["theta"]) for s in hist]
ths = [s["theta"]*57.2958 for s in hist]
print(f"theta range: {min(ths):.2f}..{max(ths):.2f} deg")
for t in (0, 1, 2, 5, 9, 10):
    i = int(t/0.001)
    print(f"t={t:2d}s E-E0={E[i]-E[0]:+.6f} J  th={ths[i]:.2f}")
print(f"max|dE|={max(abs(e-E[0]) for e in E):.6f} J  E0={E[0]:.4f} J")
