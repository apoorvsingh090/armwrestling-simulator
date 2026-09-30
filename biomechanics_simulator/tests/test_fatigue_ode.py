"""test_fatigue_ode: first-order capacity dynamics on isolated muscles.

Test-chosen rates (kf=0.5/kr=0.1, DOCUMENTED NOT physiological) compress
timescales so equilibria are reachable; production defaults stay PROVISIONAL.
"""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from actuators.hill_muscle import HillMuscle


def make(kf=0.5, kr=0.1, fmax=500.0):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return HillMuscle(name="t", Fmax_N=fmax, Lopt_m=0.1, kf=kf, kr=kr)


def test_monotonic_fatigue_at_max():
    m = make()
    prev = m.F_avail
    for _ in range(2000):
        m.update_fatigue(1.0, 0.0, 0.001)
        assert m.F_avail < prev
        prev = m.F_avail


def test_recovery_at_rest():
    m = make()
    for _ in range(2000):
        m.update_fatigue(1.0, 0.0, 0.001)
    low = m.F_avail
    for _ in range(2000):
        m.update_fatigue(0.0, 0.0, 0.001)
        assert m.F_avail >= low
        low = m.F_avail
    assert m.F_avail > m.Fmax_N * 0.5  # well on the way back (kr fast in test)


def test_equilibrium_formula():
    for a in (0.0, 0.3, 0.6, 1.0):
        m = make()
        for _ in range(40000):
            m.update_fatigue(a, 0.0, 0.001)
        expected = m.Fmax_N * m.kr / (m.kf * a * 0.8 + m.kr)
        assert m.F_avail == pytest.approx(expected, rel=1e-3)


def test_contraction_ordering():
    mc = make()
    mi = make()
    me = make()
    for _ in range(1000):
        mc.update_fatigue(0.8, 1.0, 0.001)    # concentric
        mi.update_fatigue(0.8, 0.0, 0.001)    # isometric
        me.update_fatigue(0.8, -1.0, 0.001)   # eccentric
    assert mc.F_avail < mi.F_avail < me.F_avail  # ecc < iso < conc fatigue


def test_fraction_and_unset_defaults():
    m = make()
    assert m.fatigue_fraction == 0.0
    m.update_fatigue(1.0, 0.0, 0.001)
    assert m.fatigue_fraction > 0.0
    with pytest.warns(UserWarning):
        m2 = HillMuscle(name="u", Fmax_N=100.0, Lopt_m=0.1)
    assert (m2.kf, m2.kr) == (0.005, 0.002)
