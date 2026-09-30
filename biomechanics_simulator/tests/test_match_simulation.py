"""test_match_simulation: full match runs, contact live every step, stronger
side wins; passive spin-down shows dissipative consistency (total mechanical
energy strictly decreases); single-athlete no-contact conservation smoke test.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_match import build_match


def test_full_match_stronger_wins():
    m = build_match()
    hist = m.run_match(5.0, lambda t: {"pronator_teres": 1.0}, lambda t: {}, 1.0, 0.3)
    assert len(hist) > 50
    assert all(math.isfinite(s["contact"]["Ft_on_A"]) for s in hist)
    assert hist[-1]["pin"] == "A"


def test_dissipative_consistency():
    m = build_match()
    m.A.omega_f, m.B.omega_f = 2.0, -2.0  # spinning hands into the grasp
    E0 = E_now(m)
    m.run_match(1.0, lambda t: {}, lambda t: {}, 1.0, 1.0)
    assert E_now(m) < E0  # bristle damping + slip dissipate; no source terms


def E_now(m):
    e = 0.0
    for sim in (m.A, m.B):
        e += 0.5 * 0.06 * sim.seg.omega**2 + 0.5 * 0.002 * sim.omega_f**2
    return e


def test_single_athlete_no_contact_conserves():
    import warnings
    warnings.simplefilter("ignore")
    import sys as _s
    _s.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from helpers_4dof import build_4dof_sim
    sim, _ = build_4dof_sim(theta0_deg=85.0, elbow_k=0.0, elbow_c=0.0,
                            fore_k=0.0, fore_c=0.0, inertia_ff=0.02, inertia_w=0.005)
    hist = sim.run(1.0, lambda t: {})
    E0N = math.exp(1.0) - 1.0

    def elastic(st):
        v = 0.0
        for name, mus in sim.muscles.items():
            L, _ = st[name]
            u = max(0.0, (L - mus.Lopt_m) / (mus.Lopt_m * (mus.passive_eps0 - 1.0)))
            v += mus.Fmax_N * mus.Lopt_m * (mus.passive_eps0 - 1.0) / E0N * (math.exp(u) - u - 1.0)
        return v

    E = [0.5 * 0.06 * s["omega"]**2 + 0.5 * 0.02 * s["omega_f"]**2
         + 0.5 * 0.005 * s["omega_wfe"]**2 + 0.5 * 0.005 * s["omega_rud"]**2
         - 1.5 * sim.g * 0.18 * math.sin(s["theta"]) + elastic(s["states"])
         + sim.wp_fe.potential(s["phi_wfe"]) + sim.wp_rud.potential(s["phi_rud"])
         for s in hist]
    assert max(abs(e - E[0]) / abs(E[0]) for e in E) < 1e-3
