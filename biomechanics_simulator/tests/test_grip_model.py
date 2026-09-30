"""test_grip_model: scalar grip (max 462 N E male-mean default) + slip logic."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.contact_detection import GripModel


def test_grip_zero():
    g = GripModel(mu=0.5)
    assert g.normal_force(0.0) == 0.0
    s = g.slip_state(0.0, 10.0)
    assert s["cap"] == 0.0 and s["slipped"] is True


def test_grip_max():
    g = GripModel(mu=0.5)
    assert g.normal_force(1.0) == pytest.approx(462.0)
    s = g.slip_state(1.0, 100.0)  # cap = 231
    assert s["slipped"] is False and s["held"] == pytest.approx(100.0)
    s2 = g.slip_state(1.0, 300.0)
    assert s2["slipped"] is True and s2["held"] == pytest.approx(231.0)


def test_grip_mu_required():
    with pytest.raises(ValueError):
        GripModel()  # pair UNKNOWN: no default manufactured
