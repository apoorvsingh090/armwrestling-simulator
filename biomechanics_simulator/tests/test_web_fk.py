"""test_web_fk: visual FK invariants (NOT physics validation)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from web.fk import pose, ELBOW_X, PAD_TOP_Y, L_FOREARM, VISUAL_FLAGS


def test_elbow_fixed_and_mirror():
    a = pose(0.3, 0.5, 0.2, -0.1, +1)
    b = pose(0.3, 0.5, 0.2, -0.1, -1)
    assert a["elbow"] == (-ELBOW_X, PAD_TOP_Y, 0.0)
    # athletes face each other: mirror in x AND z, y equal
    for k in ("shoulder", "elbow", "wrist", "grip"):
        assert b[k][0] == -a[k][0] and b[k][1] == a[k][1] and b[k][2] == -a[k][2]


def test_neutral_grasp_and_flexion_sweep():
    a = pose(math.pi / 2, 0, 0, 0, +1)
    b = pose(math.pi / 2, 0, 0, 0, -1)
    assert math.dist(a["grip"], b["grip"]) < 0.15  # staged meet
    import math as _m
    assert abs(_m.dist(a["elbow"], a["wrist"]) - L_FOREARM) < 1e-9  # rigid segment
    z0 = pose(0.0, 0, 0, 0, +1)["wrist"][2]
    z1 = pose(math.pi / 2, 0, 0, 0, +1)["wrist"][2]
    assert z1 != z0  # flexion moves the wrist
    assert set(VISUAL_FLAGS) >= {"L_FOREARM", "L_HAND", "ELBOW_X"}
