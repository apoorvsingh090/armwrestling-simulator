"""test_contact_model: Hunt-Crossley, Coulomb (explicit params — all UNKNOWN
in r3), Serina regimes (E thresholds <1 N / >4 N)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.contact import HuntCrossley, CoulombFriction, SerinaPulpLaw


def test_hunt_crossley_basics():
    hc = HuntCrossley(k=2e5, d=50.0, n=1.5)
    assert hc.normal_force(0.0, 0.0) == 0.0
    assert hc.normal_force(-0.001, 1.0) == 0.0  # no contact, no tension
    assert hc.normal_force(0.001, 0.0) > 0.0
    f_in = hc.normal_force(0.001, 0.5)    # penetrating faster
    f_0 = hc.normal_force(0.001, 0.0)
    f_out = hc.normal_force(0.001, -0.5)  # separating
    assert f_in > f_0 > f_out  # damping opposes penetration velocity
    assert hc.normal_force(0.001, -100.0) >= 0.0  # never tension


def test_coulomb_cone_and_falloff():
    cf = CoulombFriction(k_mu=0.5, n_mu=0.66)
    assert cf.friction_coefficient(1.0) == pytest.approx(0.5)
    assert cf.friction_coefficient(8.0) < cf.friction_coefficient(1.0)  # load falloff
    assert cf.friction_coefficient(0.0) == 0.0
    f, stuck = cf.tangential_force(10.0, 0.1)  # sliding
    assert f == pytest.approx(-(0.5 * 10.0**(0.66 - 1.0)) * 10.0)
    assert stuck is False
    f2, stuck2 = cf.tangential_force(10.0, 0.0, required_N=1.0)
    assert f2 == pytest.approx(1.0) and stuck2 is True  # held
    f3, stuck3 = cf.tangential_force(10.0, 0.0, required_N=1000.0)
    assert stuck3 is False and abs(f3) <= (0.5 * 10.0**(0.66 - 1.0)) * 10.0 + 1e-12


def test_serina_regimes():
    assert SerinaPulpLaw.regime(0.5) == "compliant"
    assert SerinaPulpLaw.regime(2.5) == "transition"
    assert SerinaPulpLaw.regime(5.0) == "bottomed"
    assert SerinaPulpLaw.transition_weight(0.5) == 0.0
    assert SerinaPulpLaw.transition_weight(5.0) == 1.0
    w = SerinaPulpLaw.transition_weight(2.5)
    assert 0.0 < w < 1.0
    assert SerinaPulpLaw.transition_weight(2.0) < SerinaPulpLaw.transition_weight(3.0)
