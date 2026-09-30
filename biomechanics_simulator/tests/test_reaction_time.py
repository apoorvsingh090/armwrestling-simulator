"""test_reaction_time: delayed-state semantics."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controllers.reaction import ReactionDelay


def test_delayed_recall():
    rd = ReactionDelay(0.25)
    for i, t in enumerate((0.0, 0.1, 0.2, 0.3)):
        rd.buffer(f"s{i}", t)
    # s0 pruned past the horizon; oldest available is the honest fallback.
    assert rd.get_delayed(0.3) == "s1"
    assert rd.get_delayed(0.55) == "s3"  # exact delayed recall
    with pytest.raises(ValueError):
        ReactionDelay().get_delayed(0.0)  # empty buffer


def test_zero_delay_passthrough():
    rd = ReactionDelay(0.0)
    rd.buffer("a", 0.0)
    rd.buffer("b", 0.1)
    assert rd.get_delayed(0.1) == "b"
    rd.reset()
    assert rd.buf == []
