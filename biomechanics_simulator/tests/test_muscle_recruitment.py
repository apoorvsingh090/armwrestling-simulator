"""test_muscle_recruitment: exact min-norm QP (balance, bounds, co-contraction)."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from controllers.recruitment import MuscleRecruitment
from helpers_ai import elbow_only_inputs


def test_hold_balanced_cocontraction():
    muscles, ma = elbow_only_inputs()
    rec = MuscleRecruitment(muscles, ["elbow"])
    a = rec.solve({"elbow": 0.0}, ma, baseline=0.1)
    assert all(v > 0.05 for v in a.values()), "both sides co-contract at hold"
    net = sum(muscles[n]["Fmax"] * ma[n]["elbow"] * (1 if "triceps" not in n else -1)
              * a[n] for n in a)
    assert abs(net) < 1e-6, "balanced: Fmax asymmetry canceled"


def test_no_drift_vs_naive():
    import warnings
    warnings.simplefilter("ignore")
    from helpers_4dof import build_4dof_sim
    muscles, ma = elbow_only_inputs()
    rec = MuscleRecruitment(muscles, ["elbow"])
    a_qp = rec.solve({"elbow": 0.0}, ma, baseline=0.1)
    sim, _ = build_4dof_sim(theta0_deg=90.0, g=0.0)
    th0 = sim.seg.theta
    for _ in range(50):
        sim.step({"biceps_long": a_qp["biceps_long"], "triceps_long": a_qp["triceps_long"],
                  "brachioradialis": a_qp["brachioradialis"], "pronator_teres": a_qp["pronator_teres"]})
    qp_drift = abs(sim.seg.theta - th0)
    sim2, _ = build_4dof_sim(theta0_deg=90.0, g=0.0)
    for _ in range(50):
        sim2.step({"biceps_long": 0.5, "triceps_long": 0.5,
                   "brachioradialis": 0.5, "pronator_teres": 0.5})
    naive_drift = abs(sim2.seg.theta - th0)
    assert qp_drift < naive_drift / 10, f"qp={qp_drift} naive={naive_drift}"


def test_torque_balance_and_clamp():
    muscles, ma = elbow_only_inputs()
    rec = MuscleRecruitment(muscles, ["elbow"])
    a = rec.solve({"elbow": 5.0}, ma)
    assert all(0.0 <= v <= 1.0 for v in a.values())
    assert rec.last_residual < 1e-3
    a2 = rec.solve({"elbow": 1000.0}, ma)  # infeasible: saturate, best effort
    assert all(0.0 <= v <= 1.0 for v in a2.values())
    assert rec.last_residual > 0.0


def test_zero_fmax_skipped():
    muscles, ma = elbow_only_inputs()
    muscles["ghost"] = {"Fmax": 0.0, "roles": {"elbow": 1}}
    ma["ghost"] = {"elbow": 0.05}
    rec = MuscleRecruitment(muscles, ["elbow"])
    a = rec.solve({"elbow": 5.0}, ma)
    assert a["ghost"] == 0.0 and "ghost" in rec.skipped
