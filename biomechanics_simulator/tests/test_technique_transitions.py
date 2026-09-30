"""test_technique_transitions: heuristic state machine timing."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from controllers.transitions import TechniqueTransitioner
from helpers_ai import neutral_sensory

warnings.simplefilter("ignore")


def test_losing_switches_defensive():
    tr = TechniqueTransitioner(side=+1)
    s = neutral_sensory(hand_velocity=-0.5)  # A-side hand driven toward own pad
    for _ in range(12):  # 0.6 s > 0.5 s rule
        tech = tr.decide(s, 0.05)
    assert tech == "defensive"


def test_winning_holds_offensive():
    tr = TechniqueTransitioner(side=+1)
    # Opponent drifting toward their pad, BELOW the fast-threat threshold:
    s = neutral_sensory(hand_velocity=0.0, opponent_hand_velocity=0.05)
    for _ in range(12):
        tech = tr.decide(s, 0.05)
    assert tech == "top_roll"


def test_stalemate_alternates():
    tr = TechniqueTransitioner(side=+1)
    s = neutral_sensory()  # all still
    tech = tr.current
    for _ in range(45):  # 2.25 s > 2 s rule
        tech = tr.decide(s, 0.05)
    assert tech == "hook"  # next offensive in cycle


def test_fast_opponent_defends():
    tr = TechniqueTransitioner(side=+1)
    s = neutral_sensory(opponent_hand_velocity=0.5)  # above 0.1 threshold
    assert tr.decide(s, 0.05) == "defensive"  # immediate
