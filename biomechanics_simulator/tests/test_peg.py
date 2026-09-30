"""test_peg: plane-simplified peg reactions on explicit hand kinematics.

Free hand is UNMODELED: no sim state drives the peg; pure-function tests +
documented non-wiring. mu/HC caller-supplied (UNKNOWN in r3).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.table import Peg
from core.contact import HuntCrossley


def test_peg_reaction_opposes_push():
    with pytest.warns(UserWarning):  # plane-simplification flag
        peg = Peg(0.33, mu_peg=0.4, hc=HuntCrossley(k=1e5, d=20.0))
    q = peg.contact(0.32, -0.5)  # hand left of plane, pushing -x into it
    assert q["contact"] is True and q["F_react"] > 0.0
    q2 = peg.contact(0.40, 0.0)  # clear of the plane
    assert q2["contact"] is False and q2["F_react"] == 0.0


def test_peg_friction_vertical():
    with pytest.warns(UserWarning):
        peg = Peg(0.33, mu_peg=0.4, hc=HuntCrossley(k=1e5, d=20.0))
    q = peg.contact(0.32, 0.0, hand_vz=0.3)
    assert q["F_friction"] == pytest.approx(-0.4 * q["F_react"])
    q2 = peg.contact(0.32, 0.0, hand_vz=0.0)
    assert q2["F_friction"] == 0.0


def test_peg_params_required():
    with pytest.raises(ValueError):  # no warning path: refuses before flagging
        Peg(0.33, mu_peg=None, hc=HuntCrossley(k=1e5, d=20.0))
    with pytest.warns(UserWarning):
        peg = Peg(0.33, mu_peg=0.4)
    with pytest.raises(ValueError):
        peg.contact(0.32, -0.5)  # normal needs explicit HC
