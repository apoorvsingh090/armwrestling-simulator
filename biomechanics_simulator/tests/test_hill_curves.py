"""Stage-1 tests: Hill force-length / force-velocity / passive curves.

Parameters mirror data/r2_mtus.json (Seth model set, calibration-flagged).
"""
import math
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from actuators.hill_muscle import HillMuscle


def make_biceps(**kw):
    args = dict(name="biceps_long", Fmax_N=485.8, Lopt_m=0.1412,
                pennation_deg=0.0, slack_m=0.257,
                fl_width_frac=0.30, vmax_lopt_per_s=10.0)
    args.update(kw)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return HillMuscle(**args)


def test_hill_force_length():
    m = make_biceps()
    assert m.fL(m.Lopt_m) == pytest.approx(1.0)
    assert m.fL(m.Lopt_m * 0.7) < 1.0
    assert m.fL(m.Lopt_m * 1.3) < 1.0
    assert m.fL(m.Lopt_m + 5 * m.sigma_fl_m) < 0.05
    assert m.fL(m.Lopt_m - 0.02) == pytest.approx(m.fL(m.Lopt_m + 0.02))  # symmetric


def test_hill_force_velocity():
    m = make_biceps()
    assert m.fV(0.0) == pytest.approx(1.0)
    assert 0.0 < m.fV(0.5 * m.vmax_m_s) < 1.0          # concentric reduces
    assert m.fV(5 * m.vmax_m_s) == pytest.approx(0.0)  # clamped at vmax
    assert m.fV(-m.vmax_m_s) > 1.0                     # eccentric exceeds, capped


def test_hill_passive():
    m = make_biceps()
    assert m.fPE(m.Lopt_m) == 0.0
    assert m.fPE(m.Lopt_m * 0.9) == 0.0
    assert m.fPE(1.8 * m.Lopt_m) == pytest.approx(1.0)  # eps0 normalization
    assert 0.0 < m.fPE(1.3 * m.Lopt_m) < 1.0


def test_hill_total_force_SI():
    m = make_biceps()
    F = m.force(1.0, m.Lopt_m, 0.0)
    assert F == pytest.approx(485.8)  # N: Fmax*a*1*1*cos0 + 0
    assert m.force(0.0, m.Lopt_m, 0.0) == pytest.approx(0.0)
    tri_args = dict(name="triceps_long", Fmax_N=1580.6, Lopt_m=0.0969,
                    pennation_deg=10.0, slack_m=0.241)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tri = HillMuscle(**tri_args)
    assert tri.force(1.0, tri.Lopt_m, 0.0) == pytest.approx(1580.6 * math.cos(math.radians(10.0)))
    assert m.force(2.0, m.Lopt_m, 0.0) == pytest.approx(485.8)  # activation clamped


def test_hill_placeholders_warn():
    with pytest.warns(UserWarning):
        HillMuscle(name="x", Fmax_N=100.0, Lopt_m=0.1)  # fl-width, vmax, slack unset
    with pytest.raises(ValueError):
        HillMuscle(name="x", Lopt_m=0.1)  # Fmax refused, no default
    with pytest.raises(ValueError):
        HillMuscle(name="x", Fmax_N=100.0)  # Lopt refused, no default
