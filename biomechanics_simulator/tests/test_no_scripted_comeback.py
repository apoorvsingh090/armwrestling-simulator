"""test_no_scripted_comeback (CRITICAL): the ODE is the ONLY capacity mechanism."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from actuators.hill_muscle import HillMuscle


def test_fmax_only_mechanism():
    kw = dict(name="t", Fmax_N=500.0, Lopt_m=0.1, kf=0.1, kr=0.01)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rested, tired = HillMuscle(**kw), HillMuscle(**kw)
    for _ in range(1000):
        tired.update_fatigue(0.7, 0.0, 0.001)
    ratio = tired.F_avail / rested.F_avail
    assert tired.force(0.7, 0.1, 0.0) == pytest.approx(rested.force(0.7, 0.1, 0.0) * ratio)


def test_no_hidden_drain_or_boost():
    kw = dict(name="t", Fmax_N=500.0, Lopt_m=0.1, kf=0.1, kr=0.01)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = HillMuscle(**kw)
    for _ in range(1000):
        m.update_fatigue(1.0, 0.0, 0.001)
    prev = m.F_avail
    for _ in range(1000):
        m.update_fatigue(0.0, 0.0, 0.001)
        assert m.F_avail >= prev  # rest never drains
        prev = m.F_avail


def test_no_game_logic_tokens():
    import pathlib
    base = pathlib.Path(__file__).resolve().parent.parent
    for fn in ("actuators/hill_muscle.py", "core/simulation.py", "core/match.py"):
        src = (base / fn).read_text(encoding="utf-8").lower()
        for tok in ("comeback", "stamina", "boost", "scripted", "trigger"):
            assert tok not in src, f"{fn} contains '{tok}'"
