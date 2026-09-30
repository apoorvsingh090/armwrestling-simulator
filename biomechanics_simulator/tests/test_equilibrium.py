"""test_equilibrium: 90° elbow, a_bic=0.5, a_tri=0, 50 N wrist load.

Analytical expectation (independent hand calc):
  F_bic = 485.8 * 0.5 * fL(=1 at Lopt) * fV(=1 at rest) * cos(0°) = 242.9 N
  r_bic(90°) = 0.0460 m exactly (PCHIP control point)
  tau_muscle = 242.9 * 0.0460 = 11.1734 Nm
  tau_gravity = 0 (cos90°), tau_passive = 0 (mid-feasible)
  tau_external = -50 * 0.30 = -15.0 Nm
  net = 11.1734 - 15.0 = -3.8266 Nm
"""
import math
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

warnings.simplefilter("ignore")
from main import build_system, torques


def test_static_equilibrium():
    sys = build_system()
    rep = torques(sys, math.pi / 2, 0.0, 0.5, 0.0, f_ext=50.0)
    assert rep["F_bic"] == pytest.approx(242.9, abs=1e-9)
    assert rep["F_tri"] == pytest.approx(0.0, abs=1e-12)
    assert rep["r_bic"] == pytest.approx(0.0460, abs=1e-12)
    assert rep["tau_gravity"] == pytest.approx(0.0, abs=1e-9)
    assert rep["tau_passive"] == pytest.approx(0.0, abs=1e-12)
    assert rep["tau_external"] == pytest.approx(-15.0, abs=1e-12)
    assert rep["net"] == pytest.approx(-3.8266, abs=1e-6)
    # spec formula: tau_net = F_biceps*r_biceps(90) - F_external*d_wrist
    assert rep["net"] == pytest.approx(rep["F_bic"] * rep["r_bic"] - 50.0 * 0.30, abs=1e-12)
