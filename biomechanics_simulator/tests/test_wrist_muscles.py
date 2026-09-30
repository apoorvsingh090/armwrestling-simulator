"""test_wrist_muscles: role routing with TEST-ONLY Fmax (NOT physics).

JSON Fmax=0 makes wrist muscles inert; direction logic is exercised here with
uniform TEST_FMAX so assertions test SIGNS/STRUCTURE only. MA node exactness
is asserted against the empirical P042-P047 anchors.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_4dof import build_4dof_sim, TEST_FMAX

TH90 = math.pi / 2


def _torques(name):
    sim, _ = build_4dof_sim(test_fmax=True)
    return sim.compute_torques(TH90, 0.0, {name: 1.0}, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_fcr_flexion_radial():
    rep = _torques("fcr_flexor_carpi_radialis")
    assert rep["tau_wrist_fe_muscle"] == pytest.approx(0.0122 * TEST_FMAX, abs=1e-9)
    assert rep["tau_wrist_rud_muscle"] == pytest.approx(0.0102 * TEST_FMAX, abs=1e-9)


def test_fcu_flexion_ulnar():
    rep = _torques("fcu_flexor_carpi_ulnaris")
    assert rep["tau_wrist_fe_muscle"] == pytest.approx(0.0113 * TEST_FMAX, abs=1e-9)
    assert rep["tau_wrist_rud_muscle"] == pytest.approx(-0.0117 * TEST_FMAX, abs=1e-9)


def test_ecr_extension_radial():
    rep = _torques("ecr_extensor_carpi_radialis")
    assert rep["tau_wrist_fe_muscle"] == pytest.approx(-0.0087 * TEST_FMAX, abs=1e-9)
    assert rep["tau_wrist_rud_muscle"] == pytest.approx(0.0136 * TEST_FMAX, abs=1e-9)


def test_ecu_extension_ulnar():
    rep = _torques("ecu_extensor_carpi_ulnaris")
    assert rep["tau_wrist_fe_muscle"] == pytest.approx(-0.0040 * TEST_FMAX, abs=1e-9)
    assert rep["tau_wrist_rud_muscle"] == pytest.approx(-0.0237 * TEST_FMAX, abs=1e-9)


def test_zero_torque_placeholders():
    sim, _ = build_4dof_sim()  # JSON-honest: PQ/supinator Fmax=0
    rep = sim.compute_torques(TH90, 0.0,
                              {"pronator_quadratus": 1.0, "supinator": 1.0,
                               "fcr_flexor_carpi_radialis": 1.0}, 0.0,
                              0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert rep["forces"]["pronator_quadratus"] == 0.0
    assert rep["forces"]["supinator"] == 0.0
    assert rep["forces"]["fcr_flexor_carpi_radialis"] == 0.0
    assert rep["tau_wrist_fe_muscle"] == pytest.approx(0.0, abs=1e-12)
    assert rep["tau_wrist_rud_muscle"] == pytest.approx(0.0, abs=1e-12)
