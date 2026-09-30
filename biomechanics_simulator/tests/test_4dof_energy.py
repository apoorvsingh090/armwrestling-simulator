"""test_4dof_energy: zero activation; KE + gravity PE + muscle elastic PE +
wrist passive potentials. Hand gravity is OMITTED by documented design, so it
is excluded from the budget (the sim never computes it). 10 s, rel < 1e-4.
Inertias I_wfe/I_rud are TEST-ONLY (UNKNOWN in corpus).
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_4dof import build_4dof_sim


def test_4dof_energy():
    # Start 87° (near equilibrium; drift 4.5e-5). Slow supination-ward forearm
    # drift is physical (biceps passive outweighs PT passive), conservative,
    # and stays clear of stops.
    sim, _ = build_4dof_sim(theta0_deg=87.0, elbow_k=0.0, elbow_c=0.0,
                            fore_k=0.0, fore_c=0.0, inertia_ff=0.02,
                            inertia_w=0.005)
    hist = sim.run(10.0, lambda t: {})
    m, g, d = 1.5, sim.g, 0.18
    E0N = math.exp(1.0) - 1.0

    def elastic(states_dict):
        v = 0.0
        for name, mus in sim.muscles.items():
            L, _ = states_dict[name]
            u = max(0.0, (L - mus.Lopt_m) / (mus.Lopt_m * (mus.passive_eps0 - 1.0)))
            v += mus.Fmax_N * mus.Lopt_m * (mus.passive_eps0 - 1.0) / E0N * (math.exp(u) - u - 1.0)
        return v

    for s in hist:
        assert -87.0 * math.pi / 180 < s["phi"] < 80.0 * math.pi / 180
        assert -70.0 * math.pi / 180 < s["phi_wfe"] < 80.0 * math.pi / 180
        assert -30.0 * math.pi / 180 < s["phi_rud"] < 20.0 * math.pi / 180
    E = [0.5 * 0.06 * s["omega"]**2 + 0.5 * 0.02 * s["omega_f"]**2
         + 0.5 * 0.005 * s["omega_wfe"]**2 + 0.5 * 0.005 * s["omega_rud"]**2
         - m * g * d * math.sin(s["theta"]) + elastic(s["states"])
         + sim.wp_fe.potential(s["phi_wfe"]) + sim.wp_rud.potential(s["phi_rud"])
         for s in hist]
    rel = max(abs(e - E[0]) / abs(E[0]) for e in E)
    assert rel < 1e-4, f"4DOF energy drift {rel}"
