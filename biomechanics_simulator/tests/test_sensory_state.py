"""test_sensory_state: values in, cheat out (schema IS the boundary)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from controllers.sensory import SensoryState
from helpers_ai import neutral_sensory


def test_values_roundtrip():
    s = neutral_sensory(hand_position=0.03, hand_velocity=-0.1, contact_force=12.0,
                        opponent_hand_velocity=0.2,
                        own_fatigue_fraction=0.4, pin=None)
    assert (s.hand_position, s.hand_velocity, s.contact_force) == (0.03, -0.1, 12.0)
    assert s.opponent_hand_velocity == 0.2 and s.own_fatigue_fraction == 0.4
    assert set(vars(s)) == SensoryState.ALLOWED


def test_no_cheat_attributes():
    s = neutral_sensory()
    for forbidden in ("opponent_activations", "opponent_fatigue", "opponent_technique",
                      "intended_technique", "future_state", "sim", "match"):
        assert not hasattr(s, forbidden), forbidden
    assert [k for k in vars(s) if "fatigue" in k] == ["own_fatigue_fraction"]


def test_schema_rejects_extras():
    with pytest.raises(TypeError):
        SensoryState(hand_position=0.0, hand_velocity=0.0, contact_force=0.0,
                     opponent_hand_velocity=0.0, own_joint_angles={},
                     own_fatigue_fraction=0.0, opponent_activations={})
