"""test_no_cheat_information (CRITICAL): fair-opponent boundary.

SensoryState schema is closed (TypeError on extras); AI consumes it or raw
joints only; no opponent internals anywhere on the path.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from controllers.sensory import SensoryState
from helpers_ai import neutral_sensory


def test_schema_closed_and_minimal():
    s = neutral_sensory()
    assert set(vars(s)) == SensoryState.ALLOWED
    assert "opponent" in [k for k in vars(s)][3]  # only opponent_HAND_velocity exists
    assert not hasattr(s, "opponent_activations")
    assert not hasattr(s, "opponent_fatigue_fraction")
    assert not hasattr(s, "intended_technique")


def test_ai_rejects_non_sensory():
    import warnings
    warnings.simplefilter("ignore")
    from helpers_4dof import build_4dof_sim
    from helpers_ai import live_ma_resolver, muscle_roles, KP, KD
    from controllers.ai_opponent import AIOpponent
    sim, _ = build_4dof_sim()
    ai = AIOpponent(muscles=muscle_roles(sim), ma_resolver=live_ma_resolver(sim),
                    Kp=dict(KP), Kd=dict(KD))
    with pytest.raises(ValueError):
        ai.compute_activations({"joints": {}}, 0.01)  # raw dict refused
