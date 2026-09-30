"""test_consistency: all internal checks PASS on live objects."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from validation.consistency import ConsistencyChecker
from helpers_validation import consistency_ctx


def test_all_consistency_checks():
    out = ConsistencyChecker().run_all(consistency_ctx())
    assert set(out) == {"qp_balance", "fatigue_equilibrium", "passive_conservatism",
                        "newton_unit", "dissipative_bound"}
    for name, r in out.items():
        assert r["status"] == "PASS", (name, r["detail"])
