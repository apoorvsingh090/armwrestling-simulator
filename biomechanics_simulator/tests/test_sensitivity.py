"""test_sensitivity: OAT ranking is finite, ordered, and physically legible
(muscle/MA drivers above rigging parameters that provably do nothing here)."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

warnings.simplefilter("ignore")

from validation.sensitivity import SensitivityAnalyzer
from helpers_match import build_match

SPECS = [
    {"name": "Fmax:pronator_teres", "kind": "Fmax", "muscles": ["pronator_teres"]},
    {"name": "Fmax:biceps_long", "kind": "Fmax", "muscles": ["biceps_long"]},
    {"name": "Fmax:triceps_long", "kind": "Fmax", "muscles": ["triceps_long"]},
    {"name": "Fmax:brachioradialis", "kind": "Fmax", "muscles": ["brachioradialis"]},
    {"name": "MA:pronator_teres:forearm", "kind": "ma_table",
     "entries": [("pronator_teres", "forearm")]},
    {"name": "MA:biceps_long:elbow", "kind": "ma_table",
     "entries": [("biceps_long", "elbow")]},
    {"name": "kf:pronator_teres", "kind": "muscle_attr",
     "muscles": ["pronator_teres"], "attr": "kf"},
    {"name": "kr:pronator_teres", "kind": "muscle_attr",
     "muscles": ["pronator_teres"], "attr": "kr"},
    {"name": "grasp_mu", "kind": "grasp_mu"},
    {"name": "grip_max", "kind": "grip_max"},
]


def test_oat_ranking():
    rows = SensitivityAnalyzer(build_match, SPECS, duration_s=0.25).run_oat(0.2)
    assert len(rows) == len(SPECS)
    for r in rows:
        assert r["sensitivity_index"] >= 0.0
        assert r["sensitivity_index"] < float("inf")
    by_name = {r["parameter"]: r["sensitivity_index"] for r in rows}
    assert by_name["Fmax:pronator_teres"] > by_name["grip_max"]  # driver beats rigging
    assert by_name["grip_max"] == 0.0  # stuck grasp: cone never binds (documented)
    assert rows[0]["parameter"] in {"Fmax:pronator_teres", "MA:pronator_teres:forearm"}
