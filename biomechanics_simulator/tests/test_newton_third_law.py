"""test_newton_third_law: exact force antisymmetry every step.

NOTE (fixed bases): total momentum is NOT conserved here — both athletes are
grounded through fixed elbows/shoulders, so ground reactions exist. The exact,
testable statement is impulse antisymmetry: sum(F_on_A) == -sum(F_on_B) to
machine precision. No momentum-conservation claim is made.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_match import build_match


def test_newton_third_law():
    m = build_match()
    hist = m.run_match(0.3, lambda t: {"pronator_teres": 1.0}, lambda t: {}, 1.0, 0.3)
    assert len(hist) > 10
    for s in hist:
        assert s["contact"]["Ft_on_A"] == -s["contact"]["Ft_on_B"]  # exact, not approx
    assert m.impulse_A == -m.impulse_B  # cumulative, exact
    assert m.impulse_A != 0.0  # nontrivial: forces actually flowed
