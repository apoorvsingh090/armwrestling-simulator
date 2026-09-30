"""test_monte_carlo: N outcomes, full accounting, sane statistics (seeded)."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

warnings.simplefilter("ignore")

from validation.monte_carlo import MonteCarloRunner
from helpers_match import build_match


def test_mc_accounting_and_stats():
    mc = MonteCarloRunner(build_match, seed=0)
    outcomes = mc.run(10, duration_s=1.5)
    assert len(outcomes) == 10
    st = MonteCarloRunner.statistics(outcomes)
    assert st["P_A"] + st["P_B"] + st["P_draw"] == pytest.approx(1.0)
    assert st["n_pinned"] + round(st["P_draw"] * 10) == 10
    if st["pin_mean"] is not None:
        assert 0.0 < st["pin_mean"] <= 1.5 and st["pin_sd"] >= 0.0 and st["pin_ci95"] >= 0.0
