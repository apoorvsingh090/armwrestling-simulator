"""test_controller_match: closed-loop technique matches; outcomes emergent.

TOP_ROLL (honest objects: PT pronation is real) vs passive B.
HOOK vs DEFENSIVE: hook cupping torque is ~0 with Fmax=0 wrists (R2 gap,
asserted as limitation, NOT faked); biceps elbow/supination action verified.
PRESS (real triceps) vs TOP_ROLL: coupling both ways asserted.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from helpers_match import build_match
from helpers_ctrl import strategy_for


def _wire(m, techA, techB=None, modeB="OFFENSIVE"):
    import warnings
    warnings.simplefilter("ignore")
    sA = strategy_for(m.A, techA, "OFFENSIVE")
    sB = strategy_for(m.B, techB, modeB) if techB else None
    m.controller_A, m.controller_B = sA, sB
    return sA, sB


def _mstate(sim):
    return {"joints": {"elbow": (sim.seg.theta, sim.seg.omega),
                       "forearm": (sim.phi, sim.omega_f),
                       "wrist_fe": (sim.phi_wfe, sim.omega_wfe),
                       "wrist_rud": (sim.phi_rud, sim.omega_rud)},
            "ma_args": {"theta": sim.seg.theta, "theta_f": sim.phi}}


def test_toproll_drags_passive():
    m = build_match()
    _wire(m, "top_roll")
    hist = m.run_match(2.0, lambda t: m.controller_A.compute_activations(
        _mstate(m.A), 0.001), lambda t: {}, 1.0, 1.0)
    assert m.B.phi < -0.02, "PT pronation must drag B supination-ward"
    assert m.impulse_A != 0.0, "tangential force actually flowed"


def test_hook_gap_documented():
    m = build_match()
    sA, _ = _wire(m, "hook")
    acts = sA.compute_activations(_mstate(m.A), 0.001)
    assert acts["biceps_long"] > 0.0  # elbow flexion + supination drive exists
    rep = m.A.compute_torques(m.A.seg.theta, 0.0, acts, 0.0, m.A.phi, 0.0,
                              0.0, 0.0, 0.0, 0.0)
    assert rep["tau_wrist_fe_muscle"] == pytest.approx(0.0, abs=1e-12), \
        "hook cupping unavailable: wrist Fmax=0 (R2 gap, not faked)"


def test_hook_vs_defensive_baseline():
    m = build_match()
    _, sB = _wire(m, "hook", "defensive", modeB="DEFENSIVE")
    actsB = sB.compute_activations(_mstate(m.B), 0.001)
    for n in ("biceps_long", "triceps_long", "pronator_teres",
              "fcu_flexor_carpi_ulnaris", "fcr_flexor_carpi_radialis"):
        assert actsB[n] == pytest.approx(0.5)


def test_press_vs_toproll_emergent():
    def run(passive_B):
        m = build_match()
        if passive_B:
            _wire(m, "press")
            return m.run_match(1.5, lambda t: m.controller_A.compute_activations(
                _mstate(m.A), 0.001), lambda t: {}, 1.0, 1.0)
        _wire(m, "press", "top_roll")
        return m.run_match(1.5, lambda t: m.controller_A.compute_activations(
            _mstate(m.A), 0.001), lambda t: m.controller_B.compute_activations(
            _mstate(m.B), 0.001), 1.0, 1.0)
    h1, h2 = run(True), run(False)
    assert h1[-1]["A"]["theta"] < math.radians(90.0), "triceps extends A's elbow"
    b1 = [s["B"]["phi"] for s in h1]
    b2 = [s["B"]["phi"] for s in h2]
    assert any(abs(a - b) > 1e-6 for a, b in zip(b1, b2)), "B's behavior depends on B's control"
    a1 = [s["A"]["phi"] for s in h1]
    a2 = [s["A"]["phi"] for s in h2]
    assert any(abs(a - b) > 1e-9 for a, b in zip(a1, a2)), "coupling acts both ways"
