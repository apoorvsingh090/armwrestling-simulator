"""test_strategy_controller: outputs, switching, defensive hold."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from helpers_4dof import build_4dof_sim
from helpers_ctrl import strategy_for
from controllers.strategy import StrategyController


def _wired(technique="top_roll", mode="OFFENSIVE"):
    import warnings
    warnings.simplefilter("ignore")
    sim, _ = build_4dof_sim(theta0_deg=90.0)
    return sim, strategy_for(sim, technique, mode)


def _mstate(sim):
    return {"joints": {"elbow": (sim.seg.theta, sim.seg.omega),
                       "forearm": (sim.phi, sim.omega_f),
                       "wrist_fe": (sim.phi_wfe, sim.omega_wfe),
                       "wrist_rud": (sim.phi_rud, sim.omega_rud)},
            "ma_args": {"theta": sim.seg.theta, "theta_f": sim.phi}}


def test_outputs_bounded_schema():
    sim, strat = _wired()
    acts = strat.compute_activations(_mstate(sim), 0.001)
    assert set(acts) == set(sim.muscles)
    assert all(isinstance(a, float) and 0.0 <= a <= 1.0 for a in acts.values())


def test_switch_changes_behavior():
    sim, strat = _wired("top_roll")
    a1 = strat.compute_activations(_mstate(sim), 0.001)
    strat.switch_technique("press")
    a2 = strat.compute_activations(_mstate(sim), 0.001)
    assert a1 != a2
    with pytest.raises(ValueError):
        strat.switch_technique("flying_mare")


def test_defensive_hold_baseline():
    sim, strat = _wired("defensive", mode="DEFENSIVE")
    acts = strat.compute_activations(_mstate(sim), 0.001)
    for n in ("biceps_long", "triceps_long", "pronator_teres",
              "fcu_flexor_carpi_ulnaris", "fcr_flexor_carpi_radialis"):
        assert acts[n] == pytest.approx(0.5)  # at rest: PD correction 0, baseline holds
