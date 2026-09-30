"""test_5body_dynamics: hand dynamics opt-in (PROVISIONAL mass/COM) with
gravity + parallel-axis inertia; energy budget extended by the hand terms;
contact-force application wiring. Hand gravity is OMITTED unless opted in.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_4dof import build_4dof_sim


def _sim5():
    sim, _ = build_4dof_sim(theta0_deg=87.0, elbow_k=0.0, elbow_c=0.0,
                            fore_k=0.0, fore_c=0.0, inertia_ff=0.02,
                            inertia_w=0.005,
                            sim_kwargs={"include_hand_dynamics": True})
    return sim


def test_hand_gravity_wiring():
    sim = _sim5()
    th = math.radians(87.0)
    rep = sim.compute_torques(th, 0.0, {}, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    m, g, lew, lwg = 0.4, sim.g, sim.lever_ew, sim.lever_wg
    assert rep["tau_hand_gravity_elbow"] == pytest.approx(
        m * g * (lew * math.cos(th) + lwg * math.cos(th)), abs=1e-12)
    assert rep["tau_hand_gravity_wrist"] == pytest.approx(
        m * g * lwg * math.cos(th), abs=1e-12)
    assert rep["tau_hand_gravity_elbow"] > 0.0


def test_contact_application_wiring():
    sim = _sim5()
    rep = sim.compute_torques(math.pi / 2, 0.0, {}, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                              contact={"Ft_flex": 10.0, "Ft_lat": 4.0})
    assert rep["tau_contact_wrist"] == pytest.approx(10.0 * sim.lever_wg, abs=1e-12)
    assert rep["tau_contact_elbow"] == pytest.approx(10.0 * (sim.lever_ew + sim.lever_wg), abs=1e-12)
    assert rep["tau_contact_rud"] == pytest.approx(4.0 * sim.lever_wg, abs=1e-12)


def test_5body_energy():
    sim = _sim5()
    hist = sim.run(10.0, lambda t: {})
    m, g, d = 1.5, sim.g, 0.18
    mh, lew, lwg = sim.hand.mass_kg, sim.lever_ew, sim.lever_wg
    Iw_eff = 0.005 + sim.hand.inertia_kgm2 + mh * lwg**2
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
         + 0.5 * Iw_eff * s["omega_wfe"]**2 + 0.5 * 0.005 * s["omega_rud"]**2
         - m * g * d * math.sin(s["theta"])
         - mh * g * (lew * math.sin(s["theta"]) + lwg * math.sin(s["theta"] + s["phi_wfe"]))
         + elastic(s["states"])
         + sim.wp_fe.potential(s["phi_wfe"]) + sim.wp_rud.potential(s["phi_rud"])
         for s in hist]
    rel = max(abs(e - E[0]) / abs(E[0]) for e in E)
    assert rel < 1e-4, f"5-body energy drift {rel}"
