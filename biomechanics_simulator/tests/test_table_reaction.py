"""test_table_reaction: table-top plane primitives (PlaneSurface IS the model)
+ Coulomb horizontal composition. Enforcement needs arm vertical states
(absent in fixed-base MVP): detection-only, documented.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.contact_detection import load_table_planes
from core.contact import HuntCrossley, CoulombFriction

R3 = os.path.join(os.path.dirname(__file__), "..", "data", "r3_hand_contact_spec.json")


def test_table_vertical_reaction():
    top = load_table_planes(R3)["table_top"]
    hc = HuntCrossley(k=3e5, d=100.0)
    q = top.query([0, 0, 1.016 - 0.005], [0, 0, -0.2])  # 5 mm below surface
    assert q["contact"] is True and q["penetration"] == pytest.approx(0.005)
    assert hc.normal_force(q["penetration"], q["rate"]) > 0.0
    assert top.query([0, 0, 1.5], [0, 0, 0])["contact"] is False  # above: free


def test_table_horizontal_friction():
    cf = CoulombFriction(k_mu=0.5, n_mu=0.66)
    f, stuck = cf.tangential_force(50.0, 0.3)
    assert f < 0.0 and abs(f) <= 0.5 * 50.0**0.66 * 50.0 + 1e-9  # cone-respecting
    f2, stuck2 = cf.tangential_force(50.0, 0.0, required_N=2.0)
    assert stuck2 is True  # static hold within cone
