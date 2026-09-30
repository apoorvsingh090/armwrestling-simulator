"""test_2dof_equilibrium: (90°, neutral), biceps + PT active.

Verifies dual action per muscle: biceps flexes AND supinates; PT weakly
flexes AND pronates. Relative (ordering/sign) assertions — robust to the
placeholder magnitudes flagged in R2/data tags.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_2dof import build_2dof_sim

TH90, PH0 = math.pi / 2, 0.0


def test_2dof_equilibrium():
    sim, reg = build_2dof_sim()
    acts = {"biceps_long": 0.5, "pronator_teres": 0.5}
    rep = sim.compute_torques(TH90, 0.0, acts, 0.0, PH0, 0.0)
    F_b, F_pt = rep["forces"]["biceps_long"], rep["forces"]["pronator_teres"]
    assert F_b == pytest.approx(242.9, abs=1e-9)   # Lopt, rest, cos0
    assert F_pt == pytest.approx(27.5, abs=1e-9)   # 55*0.5 at Lopt
    r_bf = reg["biceps_long"]["forearm_table"](TH90, PH0)
    r_pf = reg["pronator_teres"]["forearm_table"](TH90, PH0)
    assert r_bf == pytest.approx(0.011, abs=1e-12)  # table node
    assert r_pf == pytest.approx(0.008, abs=1e-12)  # table node
    bic_sup = -r_bf * F_b                        # role_forearm = -1
    pt_pro = r_pf * F_pt                         # role_forearm = +1
    assert bic_sup < 0.0, "biceps must supinate"
    assert pt_pro > 0.0, "PT must pronate"
    bic_flex = 0.046 * F_b
    pt_flex = 0.010 * F_pt
    assert 0.0 < pt_flex < bic_flex, "PT flexion weak vs biceps"
    assert rep["tau_forearm"] == pytest.approx(bic_sup + pt_pro, abs=1e-12)
    assert rep["tau_gravity"] == pytest.approx(0.0, abs=1e-9)
    assert rep["tau_passive"] == pytest.approx(0.0, abs=1e-12)
    assert rep["tau_forearm_passive"] == pytest.approx(0.0, abs=1e-12)
