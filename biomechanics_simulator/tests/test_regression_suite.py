"""test_regression_suite: guards for the recurring M3/M4/M5 bug class —
silently dropped tables/paths and drifting legacy values.

(a) every wrist muscle's tables reach the sim (M5 builder-drop bug);
(b) every multi-joint muscle's per-DOF torques sum exactly to the reported
    totals (M4 equilibrium-blind-spot bug);
(c) legacy analytic values pinned (Part-2/M2 silent-drift guard);
(d) every sim muscle has >=1 wired table; only Fmax=0 muscles are torqueless.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TH90 = math.pi / 2


def _sim():
    import warnings
    warnings.simplefilter("ignore")
    import sys as _s
    _s.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from helpers_4dof import build_4dof_sim
    sim, _ = build_4dof_sim()
    return sim


def test_wrist_tables_wired():
    sim = _sim()
    for n in ("fcr_flexor_carpi_radialis", "fcu_flexor_carpi_ulnaris",
              "ecr_extensor_carpi_radialis", "ecu_extensor_carpi_ulnaris"):
        assert sim.mt[n]["wfe"] is not None, n
        assert sim.mt[n]["wrud"] is not None, n


def test_multijoint_torque_accounting():
    sim = _sim()
    acts = {"biceps_long": 0.5, "pronator_teres": 0.5, "brachioradialis": 0.3}
    rep = sim.compute_torques(TH90, 0.0, acts, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    exp_e = exp_f = 0.0
    for name, F in rep["forces"].items():
        e = sim.mt[name]
        exp_e += sim.roles.get(name, 0.0) * (e["elbow"](TH90) if e["elbow"] else 0.0) * F
        ft = e["forearm"]
        exp_f += sim.f_roles.get(name, 0.0) * (ft(TH90, 0.0) if ft else 0.0) * F
    assert rep["tau_muscle"] == pytest.approx(exp_e, abs=1e-12)
    assert rep["tau_forearm_muscle"] == pytest.approx(exp_f, abs=1e-12)
    assert rep["forces"]["brachioradialis"] > 0.0  # BRD table loaded, not dropped


def test_legacy_values_pinned():
    sim = _sim()
    assert sim.ma["biceps_long"](TH90) == pytest.approx(0.0460, abs=1e-12)
    assert sim.ma["triceps_long"](TH90) == pytest.approx(0.0230, abs=1e-12)
    import sys as _s
    _s.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import torques, build_system
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rep = torques(build_system(), TH90, 0.0, 0.5, 0.0, f_ext=50.0)
    assert rep["net"] == pytest.approx(-3.8266, abs=1e-6)  # Part-2 analytic


def test_every_muscle_wired_exact_zero_set():
    sim = _sim()
    rep = sim.compute_torques(TH90, 0.0,
                              {n: 1.0 for n in sim.muscles}, 0.0,
                              0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    for name in sim.muscles:
        wired = [k for k in ("elbow", "forearm", "wfe", "wrud")
                 if sim.mt[name][k] is not None]
        assert wired, name
        if rep["forces"][name] == 0.0:
            assert sim.muscles[name].Fmax_N == 0.0, name  # only zero-Fmax may be torqueless
