"""test_4dof_equilibrium: all-neutral + external hand load; per-DOF balance.

JSON-honest objects (wrist Fmax=0): verifies balance STRUCTURE. External 20 N
at hand: elbow -20*(0.28+0.08), wrist_fe -20*0.08, rud 0 (offset 0).
Biceps 0.5 gives 11.1734 Nm elbow flexion; gravity/passives vanish at neutral.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_4dof import build_4dof_sim


def test_4dof_equilibrium():
    sim, _ = build_4dof_sim()
    rep = sim.compute_torques(math.pi / 2, 0.0, {"biceps_long": 0.5}, 20.0,
                              0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    F_b = rep["forces"]["biceps_long"]
    assert F_b == pytest.approx(242.9, abs=1e-9)
    # biceps supination drag at neutral (role_f=-1, table node 0.011):
    bic_sup = -0.011 * F_b
    assert rep["tau_forearm"] == pytest.approx(bic_sup, abs=1e-12)
    for n in ("fcr_flexor_carpi_radialis", "fcu_flexor_carpi_ulnaris",
              "ecr_extensor_carpi_radialis", "ecu_extensor_carpi_ulnaris",
              "pronator_quadratus", "supinator"):
        assert rep["forces"][n] == pytest.approx(0.0, abs=1e-12)
    assert rep["tau_muscle"] == pytest.approx(11.1734, abs=1e-6)
    assert rep["tau_external"] == pytest.approx(-20.0 * 0.36, abs=1e-12)
    assert rep["net"] == pytest.approx(11.1734 - 7.2, abs=1e-6)
    assert rep["tau_wrist_fe_external"] == pytest.approx(-20.0 * 0.08, abs=1e-12)
    assert rep["tau_wrist_fe"] == pytest.approx(-1.6, abs=1e-12)  # passive 0 at neutral
    assert rep["tau_wrist_rud"] == pytest.approx(0.0, abs=1e-12)
    assert rep["tau_gravity"] == pytest.approx(0.0, abs=1e-9)
    assert rep["tau_forearm"] == pytest.approx(bic_sup, abs=1e-12)
