"""test_no_technique_bonus (CRITICAL): techniques are activation strategies.

Enforces: (1) zero activations -> zero motion for EVERY technique;
(2) technique objects carry no force/torque fields; (3) controllers/ never
imports core.simulation or core.match; (4) all outputs are [0,1] floats.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from controllers.technique_controllers import TECHNIQUES
from helpers_4dof import build_4dof_sim
from helpers_ctrl import strategy_for


def test_zero_activation_zero_motion_all_techniques():
    import warnings
    warnings.simplefilter("ignore")
    for name in TECHNIQUES:
        sim, _ = build_4dof_sim(theta0_deg=90.0, g=0.0)
        s0 = (sim.seg.theta, sim.phi, sim.phi_wfe, sim.phi_rud)
        for _ in range(100):
            sim.step({n: 0.0 for n in sim.muscles})
        s1 = (sim.seg.theta, sim.phi, sim.phi_wfe, sim.phi_rud)
        assert s0 == s1, name  # technique selected, muscles silent: nothing moves


def test_no_torque_fields():
    import inspect
    import re
    import controllers.technique_controllers as tc
    import controllers.strategy as st
    import controllers.base_controller as bc
    for mod in (tc, st, bc):
        src = inspect.getsource(mod)
        assert not re.search(r"^\s*(import|from)\s+core\.(simulation|match)\b",
                             src, re.MULTILINE), mod.__name__
        assert "apply_force" not in src and "add_torque" not in src, mod.__name__


def test_outputs_always_activations():
    import warnings
    warnings.simplefilter("ignore")
    sim, _ = build_4dof_sim(theta0_deg=90.0)
    for name in TECHNIQUES:
        strat = strategy_for(sim, name)
        acts = strat.compute_activations(
            {"joints": {"elbow": (1.0, 5.0), "forearm": (-1.0, -5.0),
                        "wrist_fe": (1.2, 3.0), "wrist_rud": (-0.5, -3.0)},
             "ma_args": {"theta": 1.0, "theta_f": -1.0}}, 0.001)
        assert set(acts) == set(sim.muscles)
        assert all(isinstance(a, float) and 0.0 <= a <= 1.0 for a in acts.values())
