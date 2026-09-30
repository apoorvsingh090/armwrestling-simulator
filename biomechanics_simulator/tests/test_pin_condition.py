"""test_pin_condition: synthetic crossings (exact) + one dynamic pin."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_match import build_match


def test_pin_planes():
    m = build_match(pin_x=0.05)
    assert m.check_pin() is None  # neutral start
    m.B.phi = -(0.05 + 0.01) / 0.08  # B's hand past B's pad
    assert m.check_pin() == "A"
    m.B.phi = 0.0
    m.A.phi = -(0.05 + 0.01) / 0.08  # A's hand past A's pad
    assert m.check_pin() == "B"


def test_dynamic_pin():
    m = build_match()
    hist = m.run_match(3.0, lambda t: {"pronator_teres": 1.0}, lambda t: {}, 1.0, 0.3)
    assert hist[-1]["pin"] == "A"
