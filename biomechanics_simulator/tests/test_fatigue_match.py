"""test_fatigue_match: capacity divergence between high/low activation athletes.

3 s at 1 kHz with PROVISIONAL global rates: A (PT 1.0) vs B (PT 0.1) separate
~10x in fatigue fraction — mechanism check, not outcome prediction (pin
timescales need calibrated rates; no outcome asserted here).
Legacy mode (default builders): fractions stay 0, capacities constant.
"""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core.match import MatchSimulation
from core.contact_detection import load_table_planes
from helpers_4dof import build_4dof_sim

R3 = os.path.join(os.path.dirname(__file__), "..", "data", "r3_hand_contact_spec.json")


def _fatigued_match():
    warnings.simplefilter("ignore")
    A, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.005,
                          sim_kwargs={"fatigue_enabled": True})
    B, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.005,
                          sim_kwargs={"fatigue_enabled": True})
    m = MatchSimulation(A, B, load_table_planes(R3), friction_mu=0.5,
                        tangential_k=2000.0, tangential_c=5.0, lever_m=0.08,
                        pin_x_m=0.05)
    hist = m.run_match(3.0, lambda t: {"pronator_teres": 1.0},
                       lambda t: {"pronator_teres": 0.1}, 1.0, 1.0)
    return m, hist


def test_high_activation_fatigues_faster():
    m, hist = _fatigued_match()
    assert "fatigue" in hist[0]["A"] and "fatigue" in hist[0]["B"]
    fa = hist[-1]["A"]["fatigue"]["pronator_teres"]
    fb = hist[-1]["B"]["fatigue"]["pronator_teres"]
    assert fa > fb > 0.0
    assert m.A.muscles["pronator_teres"].F_avail < 55.0  # capacity decreased
    # NOTE: the pin ends this match in ~0.1 s, so absolute fractions stay small
    # at provisional rates (honest timescale finding, not a model failure).


def test_capacity_divergence_fixed_duration():
    # No pin termination: 3 s of sustained schedules isolates the mechanism.
    warnings.simplefilter("ignore")
    A, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.005,
                          sim_kwargs={"fatigue_enabled": True})
    B, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.005,
                          sim_kwargs={"fatigue_enabled": True})
    A.run(3.0, lambda t: {"pronator_teres": 1.0})
    B.run(3.0, lambda t: {"pronator_teres": 0.1})
    fa = A.muscles["pronator_teres"].fatigue_fraction
    fb = B.muscles["pronator_teres"].fatigue_fraction
    assert fa > 0.01 > fb  # ~10x separation at provisional rates


def test_legacy_mode_no_fatigue():
    warnings.simplefilter("ignore")
    A, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.005)
    B, _ = build_4dof_sim(theta0_deg=90.0, inertia_ff=0.005)
    m = MatchSimulation(A, B, load_table_planes(R3), friction_mu=0.5,
                        tangential_k=2000.0, tangential_c=5.0, lever_m=0.08,
                        pin_x_m=0.05)
    hist = m.run_match(1.0, lambda t: {"pronator_teres": 1.0},
                       lambda t: {"pronator_teres": 1.0}, 1.0, 1.0)
    for s in hist:
        assert all(v == 0.0 for v in s["A"]["fatigue"].values())
        assert all(v == 0.0 for v in s["B"]["fatigue"].values())
    assert A.muscles["pronator_teres"].F_avail == 55.0
    rep = m.fatigue_report()
    assert rep["A"]["max_fraction"] == 0.0 and rep["B"]["mean_fraction"] == 0.0
