"""test_2dof_dynamic: rotation-toward-neutral, 2DOF energy, stop behavior."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_2dof import build_2dof_sim


def test_biceps_supinates_from_pronation():
    sim, _ = build_2dof_sim(theta0_deg=90.0, phi0_deg=45.0, g=0.0)
    acts = {"biceps_long": 1.0}
    for _ in range(20):
        sim.step(acts)
    assert sim.phi < math.radians(45.0), "supination torque must drive phi toward neutral"


def test_pt_pronates_from_supination():
    sim, _ = build_2dof_sim(theta0_deg=90.0, phi0_deg=-45.0, g=0.0)
    acts = {"pronator_teres": 1.0}
    for _ in range(50):
        sim.step(acts)
    assert sim.phi > math.radians(-45.0), "pronation torque must drive phi toward neutral"


def test_energy_conservation_2dof():
    # Full 6-muscle set (PQ/supinator inert at Fmax=0), restraints zeroed so ONLY
    # gravity + conservative passive elasticity act. I_ff=0.02 is TEST-ONLY
    # (UNKNOWN in corpus): slows forearm drift so no stop is touched in 10 s.
    # Start 87° (near equilibrium): drift 5e-5 < 1e-4 over 10 s. Note the slow
    # supination-ward forearm drift is physical, not error: biceps passive
    # (stretched below 90° elbow) outweighs PT passive and supinates.
    sim, _ = build_2dof_sim(theta0_deg=87.0, phi0_deg=0.0, g=9.81,
                            elbow_k=0.0, elbow_c=0.0, fore_k=0.0, fore_c=0.0,
                            inertia_ff=0.02)
    hist = sim.run(10.0, lambda t: {})
    m, g, d, Iee, Iff = 1.5, sim.g, 0.18, 0.06, 0.02
    E0N = math.exp(1.0) - 1.0

    def elastic(th, ph):
        v = 0.0
        for name, mus in sim.muscles.items():
            L, _ = sim.compute_muscle_state(th, 0.0, ph, 0.0)[name]
            u = max(0.0, (L - mus.Lopt_m) / (mus.Lopt_m * (mus.passive_eps0 - 1.0)))
            v += mus.Fmax_N * mus.Lopt_m * (mus.passive_eps0 - 1.0) / E0N * (math.exp(u) - u - 1.0)
        return v

    assert all(-87.0 * math.pi / 180 < s["phi"] < 80.0 * math.pi / 180 for s in hist)
    E = [0.5 * Iee * s["omega"]**2 + 0.5 * Iff * s["omega_f"]**2
         - m * g * d * math.sin(s["theta"]) + elastic(s["theta"], s["phi"]) for s in hist]
    rel = max(abs(e - E[0]) / abs(E[0]) for e in E)
    assert rel < 1e-4, f"2DOF energy drift {rel}"


def test_forearm_stop_projection():
    sim, _ = build_2dof_sim(theta0_deg=90.0, phi0_deg=79.0, g=0.0,
                            fore_k=0.0, fore_c=0.0)
    from helpers_2dof import build_2dof_sim as _b  # noqa
    Jn = sim.f_joint.anat_max
    sim.omega_f = 3.0
    states = []
    for _ in range(500):
        st = sim.step({})
        states.append((st["phi"], st["omega_f"]))
    assert all(p <= Jn + 1e-12 for p, _ in states)
    hits = [(p, w) for p, w in states if p >= Jn - 1e-12]
    assert hits, "must reach the pronation stop"
    assert all(w == 0.0 for _, w in hits), "no retained outward velocity"
