"""test_cross_validation: anchors PASS (circular, labeled); Seth-vs-PCSA
conflict FAILS as it should (R2 directive 5). Torque data: MISSING."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

warnings.simplefilter("ignore")

from validation.cross_validation import CrossValidator
from helpers_4dof import build_4dof_sim
from helpers_validation import ma_rows, rom_rows, force_rows


def test_ma_pipeline_fidelity():
    sim, _ = build_4dof_sim()
    out = CrossValidator().validate_moment_arms(ma_rows(sim))
    for name, r in out.items():
        assert r["grade"] == "PASS", (name, r)
        assert "circular" in r["note"]


def test_rom_pipeline_fidelity():
    sim, _ = build_4dof_sim()
    out = CrossValidator().validate_rom(rom_rows(sim))
    for name, r in out.items():
        assert r["grade"] == "PASS", (name, r)


def test_force_conflict_reported():
    out = CrossValidator().validate_forces(force_rows())
    assert out["biceps_long"]["grade"] == "FAIL"
    assert out["triceps_long"]["grade"] == "FAIL"
    assert out["brachioradialis"]["grade"] == "PASS"
    assert out["pronator_teres"]["grade"] == "PASS"
    assert out["biceps_long"]["rel_err"] > 0.5
