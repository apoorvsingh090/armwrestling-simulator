"""test_elbow_pad: compliant unilateral pad on explicit kinematics + sim queries.

All k/d/n/mu caller-supplied (r3: pad stiffness + vinyl mu UNKNOWN)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.table import ElbowPad
from core.contact import HuntCrossley

TOP, HALF = 1.0668, 0.0889  # WAF stand height + 2in pad; 7in pad half-width


def make_pad():
    return ElbowPad(TOP, HALF, HuntCrossley(k=2e5, d=50.0, n=1.5), mu_pad=0.5)


def test_pad_supports_weight():
    pad = make_pad()
    q = pad.contact(TOP - 0.002, 0.0)  # 2 mm compression, rest
    assert q["contact"] is True and q["on_pad"] is True
    assert 5.0 < q["Fn"] < 50.0  # order of arm weight (~19 N), scale check only


def test_pad_friction_opposes_slide():
    pad = make_pad()
    f, stuck = pad.tangential(20.0, 0.3)
    assert f == pytest.approx(-0.5 * 20.0) and stuck is False
    f2, stuck2 = pad.tangential(20.0, -0.3)
    assert f2 == pytest.approx(0.5 * 20.0) and stuck2 is False
    f3, stuck3 = pad.tangential(20.0, 0.0)
    assert f3 == 0.0 and stuck3 is True


def test_pad_unilateral_and_lift():
    pad = make_pad()
    assert pad.contact(TOP + 0.01, 0.5)["Fn"] == 0.0  # above: no pull-down, ever
    assert pad.contact(TOP + 0.01, 0.5)["contact"] is False
    assert pad.check_lift(TOP + 0.01) is True   # lift detector input
    assert pad.check_lift(TOP - 0.001) is False
    off = pad.contact(TOP - 0.002, 0.0, elbow_xy=(0.5, 0.0))
    assert off["on_pad"] is False and off["Fn"] == 0.0  # slid off: no force


def test_sim_pad_queries():
    import warnings
    warnings.simplefilter("ignore")
    import sys as _s
    _s.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from helpers_4dof import build_4dof_sim
    sim, _ = build_4dof_sim()
    assert sim.pad_preload()["preload_N"] == pytest.approx(1.5 * sim.g)
    assert sim.pad_preload()["integrated"] is False
    assert sim.lift_state()["lift"] is False  # fixed base: vacuous, documented
    sim.elbow_rest_z = TOP
    assert sim.lift_state(TOP + 0.005)["lift"] is True
    assert sim.lift_state(TOP)["lift"] is False
