"""test_table_constraints: WAF geometry loads; unilateral plane logic on
synthetic probes; sim-level pad state is degenerate-by-construction
(fixed base) and reported as such."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.contact_detection import ContactPoint, ContactDetector, PlaneSurface, load_table_planes

R3 = os.path.join(os.path.dirname(__file__), "..", "data", "r3_hand_contact_spec.json")


def test_table_geometry_loads():
    planes = load_table_planes(R3)
    assert planes["elbow_pad"].c == pytest.approx(-(1.016 + 0.0508))  # stand + 2in pad
    assert planes["table_top"].c == pytest.approx(-1.016)


def test_unilateral_plane():
    pad = load_table_planes(R3)["elbow_pad"]
    top = -pad.c
    below = pad.query([0, 0, top - 0.01], [0, 0, -0.5])   # penetrating downward
    assert below["contact"] is True
    assert below["penetration"] == pytest.approx(0.01)
    assert below["rate"] == pytest.approx(0.5)  # penetrating speed
    above = pad.query([0, 0, top + 0.05], [0, 0, 0.5])    # separated, lifting off
    assert above["contact"] is False  # unilateral: free to leave
    leaving = pad.query([0, 0, top - 0.005], [0, 0, 1.0])
    assert leaving["contact"] is True and leaving["rate"] == pytest.approx(-1.0)


def test_detector_and_peg():
    planes = load_table_planes(R3)
    pts = [ContactPoint("a", lambda: [0, 0, 2.0], lambda: [0, 0, 0]),
           ContactPoint("b", lambda: [-1.0, 0, 0.5], lambda: [-0.2, 0, 0])]
    hits = ContactDetector.detect(pts, [planes["peg"]])
    assert len(hits) == 1 and hits[0]["point"] == "b"  # x + 0.33 < 0
    assert hits[0]["penetration"] == pytest.approx(1.0 - 0.33)


def test_sim_pad_state_degenerate():
    from helpers_4dof import build_4dof_sim
    sim, _ = build_4dof_sim()
    sim.table = load_table_planes(R3)
    sim.elbow_rest_z = -load_table_planes(R3)["elbow_pad"].c  # rest exactly on pad
    q = sim.pad_state()
    assert q["degenerate_fixed_base"] is True
    assert q["contact"] is False and q["penetration"] == 0.0  # touching, not penetrating
