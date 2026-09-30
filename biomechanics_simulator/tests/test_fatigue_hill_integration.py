"""test_fatigue_hill_integration: fatigue scales Fmax ONLY (fL/fV/passive immune)."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from actuators.hill_muscle import HillMuscle


def pair():
    kw = dict(name="t", Fmax_N=500.0, Lopt_m=0.1, kf=0.1, kr=0.01)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return HillMuscle(**kw), HillMuscle(**kw)


def test_fatigued_weaker_same_inputs():
    rested, tired = pair()
    for _ in range(2000):
        tired.update_fatigue(1.0, 0.0, 0.001)
    L, v = 0.1, 0.0
    assert tired.force(0.5, L, v) < rested.force(0.5, L, v)
    assert tired.Fmax_N == rested.Fmax_N == 500.0  # baseline never mutated


def test_curves_and_passive_immune():
    rested, tired = pair()
    for _ in range(2000):
        tired.update_fatigue(1.0, 0.5, 0.001)
    for L in (0.08, 0.1, 0.13):
        assert tired.fL(L) == rested.fL(L)
    for v in (-1.0, 0.0, 1.0):
        assert tired.fV(v) == rested.fV(v)
    assert tired.fPE(0.13) == rested.fPE(0.13)
    assert tired.force(0.0, 0.13, 0.0) == rested.force(0.0, 0.13, 0.0)  # passive equal
