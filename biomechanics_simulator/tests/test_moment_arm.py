"""test_moment_arm_continuity: finite, positive, C1 across 0-145°."""
import math
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

warnings.simplefilter("ignore")
from actuators.moment_arm import load_elbow_tables

TABLE = os.path.join(os.path.dirname(__file__), "..", "data", "r2_mtus.json")


def test_moment_arm_continuity():
    ma = load_elbow_tables(TABLE)
    thetas = [math.radians(d) for d in range(0, 146)]
    for name in ("biceps", "triceps"):
        vals = [ma[name](t) for t in thetas]
        assert all(math.isfinite(v) for v in vals)
        assert all(v > 0 for v in vals), f"{name} must stay positive on 0-145deg"
        diffs = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
        assert max(diffs) < 0.002, f"{name} jump discontinuity: {max(diffs)}"
    assert ma["biceps"](math.radians(110)) == pytest.approx(0.047, abs=1e-12)
    assert ma["triceps"](math.radians(90)) == pytest.approx(0.023, abs=1e-12)
    peak_bic = max(range(146), key=lambda d: ma["biceps"](math.radians(d)))
    assert 100 <= peak_bic <= 120, f"biceps peak at {peak_bic}deg, want 100-120 (Murray1995)"
    assert not ma["biceps"].is_extrapolated(math.radians(90))
    assert ma["biceps"].is_extrapolated(math.radians(150))
