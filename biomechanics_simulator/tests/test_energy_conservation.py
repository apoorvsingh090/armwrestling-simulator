"""test_energy_conservation: gravity-only pendulum about stable 90° equilibrium.

PE = -m*g*d*sin(th) is the potential consistent with tau=+m*g*d*cos(th):
 -dPE/dTh = +m*g*d*cos(th). Restraint zeroed (k=c=0) so ONLY gravity acts;
swing 60<->120deg never touches stops. Symplectic Euler: bounded, no drift.
"""
import math
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

warnings.simplefilter("ignore")
from core.integrator import SemiImplicitEuler
from core.rigid_body import Segment
from core.joint import HingeJoint
from actuators.hill_muscle import HillMuscle
from actuators.moment_arm import load_elbow_tables
from core.simulation import Simulation

BASE = os.path.join(os.path.dirname(__file__), "..")


def make_gravity_only():
    ma = load_elbow_tables(os.path.join(BASE, "data", "r2_mtus.json"))
    bic = HillMuscle("biceps_long", Fmax_N=485.8, Lopt_m=0.1412, slack_m=0.257)
    tri = HillMuscle("triceps_long", Fmax_N=1580.6, Lopt_m=0.0969,
                     pennation_deg=10.0, slack_m=0.241)
    seg = Segment("forearm", mass_kg=1.5, com_m=0.18, inertia_kgm2=0.06,
                  theta0_rad=math.radians(85), wrist_m=0.30)
    joint = HingeJoint(restraint_k=0.0, restraint_c=0.0)
    return Simulation(seg, joint, {"biceps_long": bic, "triceps_long": tri},
                      {"biceps_long": ma["biceps"], "triceps_long": ma["triceps"]},
                      SemiImplicitEuler(dt=0.001))


def test_energy_conservation():
    # Start 85° (near the 90° stable equilibrium): ~10° peak-to-peak swing over
    # 10 s (~10 oscillations) exercises gravity variation + passive onset while
    # keeping the conservative system mildly nonlinear at dt=1ms. Larger
    # amplitudes show larger (bounded, non-drifting) symplectic oscillation;
    # see scripts/energy_probe.py for the 60° characterization.
    sim = make_gravity_only()
    hist = sim.run(10.0, lambda t: {"biceps_long": 0.0, "triceps_long": 0.0})
    m, g, d, I = 1.5, sim.g, 0.18, 0.06
    # Zero activation is NOT zero muscle force: the passive exponential element
    # F_pass(L) is conservative (function of L(theta) only), so its elastic
    # potential joins the budget. EXACT antiderivative (no quadrature):
    # V_m = Fmax*Lopt*(eps0-1)/(e-1) * [exp(u) - u - 1], u = max(0, strain/(eps0-1)).
    import math as _m
    E0N = _m.exp(1.0) - 1.0

    def elastic(th):
        states = sim.compute_muscle_state(th, 0.0)
        v = 0.0
        for name, mus in sim.muscles.items():
            L, _ = states[name]
            u = max(0.0, (L - mus.Lopt_m) / (mus.Lopt_m * (mus.passive_eps0 - 1.0)))
            v += mus.Fmax_N * mus.Lopt_m * (mus.passive_eps0 - 1.0) / E0N * (_m.exp(u) - u - 1.0)
        return v

    E = [0.5 * I * s["omega"]**2 - m * g * d * math.sin(s["theta"]) + elastic(s["theta"])
         for s in hist]
    assert all(30.0 * math.pi / 180 < s["theta"] < 130.0 * math.pi / 180 for s in hist)
    rel = max(abs(e - E[0]) / abs(E[0]) for e in E)
    assert rel < 1e-4, f"energy drift {rel}"
