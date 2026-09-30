"""test_wrist_passive: Delp-anchored curves — neutral zero, end-range growth,
conservative (finite-difference potential check)."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_4dof import build_4dof_sim


def test_passive_zero_at_neutral():
    sim, _ = build_4dof_sim()
    assert sim.wp_fe(0.0) == pytest.approx(0.0, abs=1e-12)
    assert sim.wp_rud(0.0) == pytest.approx(0.0, abs=1e-12)


def test_passive_grows_to_limits():
    sim, _ = build_4dof_sim()
    fe = [abs(sim.wp_fe(math.radians(d))) for d in (0, 40, 80)]
    assert fe[0] < fe[1] < fe[2]  # flexion restoring grows
    ex = [abs(sim.wp_fe(math.radians(d))) for d in (0, -35, -70)]
    assert ex[0] < ex[1] < ex[2]  # extension restoring grows
    assert abs(sim.wp_fe(math.radians(-70))) > abs(sim.wp_fe(math.radians(80)))  # asymmetry 1.2>0.5
    ru = [abs(sim.wp_rud(math.radians(d))) for d in (0, -15, -30)]
    assert ru[0] < ru[1] < ru[2]


def test_passive_conservative():
    sim, _ = build_4dof_sim()
    for wp, deg in ((sim.wp_fe, 40.0), (sim.wp_fe, -50.0), (sim.wp_rud, -20.0)):
        th = math.radians(deg)
        h = 1e-6
        dV = wp.potential(th + h) - wp.potential(th - h)
        assert dV / (2 * h) == pytest.approx(-wp(th), rel=1e-6)  # tau = -dV/dth
