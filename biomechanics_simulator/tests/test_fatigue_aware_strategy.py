"""test_fatigue_aware_strategy: threshold scaling (PROVISIONAL 0.3/0.7)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from controllers.ai_opponent import scale_for_fatigue


def test_below_threshold_unchanged():
    acts = {"biceps_long": 0.8, "triceps_long": 0.2}
    assert scale_for_fatigue(acts, 0.1) == acts
    assert scale_for_fatigue(acts, 0.3) == acts  # boundary inclusive


def test_above_threshold_scaled():
    acts = {"biceps_long": 0.8, "triceps_long": 0.2}
    out = scale_for_fatigue(acts, 0.5)
    assert out == {"biceps_long": pytest.approx(0.56), "triceps_long": pytest.approx(0.14)}


def test_scaled_accumulates_slower():
    import warnings
    warnings.simplefilter("ignore")
    from actuators.hill_muscle import HillMuscle
    kw = dict(name="t", Fmax_N=500.0, Lopt_m=0.1, kf=0.1, kr=0.01)
    hi, lo = HillMuscle(**kw), HillMuscle(**kw)
    scaled = scale_for_fatigue({"t": 1.0}, 0.5)["t"]
    for _ in range(1000):
        hi.update_fatigue(1.0, 0.0, 0.001)
        lo.update_fatigue(scaled, 0.0, 0.001)
    assert lo.F_avail > hi.F_avail  # reduced effort preserves capacity
