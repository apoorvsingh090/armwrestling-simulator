"""test_slip_resolution: stuck (bounded relative displacement) vs slip
(cone-saturated, growing separation, weak side loses position)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_match import build_match


def _rel(history):
    return [abs(s["x_A"] - s["x_B"]) for s in history]


def test_no_slip_moves_together():
    m = build_match()
    hist = m.run_match(1.0, lambda t: {"pronator_teres": 0.2}, lambda t: {}, 1.0, 1.0)
    assert not any(s["contact"]["slipped"] for s in hist)
    assert max(_rel(hist)) < 0.01  # grasp holds hands together (mm-scale)


def test_slip_onset_and_weak_side_loss():
    m = build_match()
    hist = m.run_match(3.0, lambda t: {"pronator_teres": 1.0},
                       lambda t: {"biceps_long": 0.3}, 1.0, 0.02)
    slips = [i for i, s in enumerate(hist) if s["contact"]["slipped"]]
    assert slips, "resisted weak grasp must saturate the cone"
    assert slips[0] > 0, "demand starts at zero: onset is detected, not initial"
    assert max(_rel(hist)) > 0.01, "slip separates hands beyond the stuck bound"


def test_weaker_grip_pins():
    m = build_match()
    hist = m.run_match(3.0, lambda t: {"pronator_teres": 1.0}, lambda t: {}, 1.0, 0.02)
    assert hist[-1]["pin"] == "A", "dragged weak-grip hand reaches B's pad"
