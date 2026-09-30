"""test_fatigue_recovery: capacity returns toward baseline at kr rate."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from actuators.hill_muscle import HillMuscle


def test_recovery_matches_kr():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = HillMuscle(name="t", Fmax_N=500.0, Lopt_m=0.1, kf=0.4, kr=0.1)
    for _ in range(5000):
        m.update_fatigue(1.0, 0.0, 0.001)
    F0, f0 = m.F_avail, m.fatigue_fraction
    for _ in range(5000):
        m.update_fatigue(0.0, 0.0, 0.001)
    import math
    expected = m.Fmax_N - (m.Fmax_N - F0) * math.exp(-m.kr * 5.0)
    assert m.F_avail == pytest.approx(expected, rel=1e-2)
    assert m.fatigue_fraction < f0  # fraction decreased during recovery
