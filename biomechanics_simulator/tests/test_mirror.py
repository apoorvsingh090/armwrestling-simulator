"""test_mirror: anatomical mirror conventions (labels, not pure geometry)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.mirror import MirrorTransform, lateral_hand_position


def test_position_roundtrip():
    m = MirrorTransform()
    assert m.to_global((1.0, 2.0, 3.0)) == (-1.0, 2.0, 3.0)
    assert m.to_local(m.to_global((1.0, 2.0, 3.0))) == (1.0, 2.0, 3.0)
    with pytest.raises(ValueError):
        MirrorTransform("y")


def test_angle_signs():
    m = MirrorTransform()
    assert m.angle_sign("forearm") == -1.0   # B pronation reads as A supination
    assert m.angle_sign("wrist_rud") == -1.0  # radial/ulnar opposite
    assert m.angle_sign("elbow") == 1.0
    assert m.angle_sign("wrist_fe") == 1.0
    assert m.global_angle("forearm", 0.5, +1) == 0.5
    assert m.global_angle("forearm", 0.5, -1) == -0.5
    with pytest.raises(ValueError):
        m.global_angle("forearm", 0.5, 0)


def test_lateral_map():
    assert lateral_hand_position(0.5, 0.08, +1) == 0.04
    assert lateral_hand_position(0.5, 0.08, -1) == -0.04
    with pytest.raises(ValueError):
        lateral_hand_position(0.5, 0.08, 0)
