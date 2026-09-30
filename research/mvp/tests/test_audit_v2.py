"""Audit V2 regression tests: hard-stop velocity projection (AUDIT 6 fix)
and moment-arm interface substitutability (AUDIT 2 recommendation).
Behavior of the baseline scenario is unchanged (pinned by existing tests).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from biomech.moment_arm import MomentArmModel, MomentArmProvisional
from biomech.simulation import ElbowSimulation, SimConfig


def test_hard_stop_velocity_projection_extension():
    tr = ElbowSimulation(SimConfig(dt=0.001, duration_s=1.0,
                                   theta0_rad=math.radians(10),
                                   u_biceps=0.0, u_triceps=1.0,
                                   gravity_on=False)).run()
    assert min(tr.theta) >= 0.0
    for th, om in zip(tr.theta, tr.omega):
        if th <= 0.0:
            assert om <= 0.0 + 1e-12 and om == 0.0, \
                f"pinned at extension stop with outward velocity {om}"
    assert tr.omega[-1] == 0.0


def test_hard_stop_velocity_projection_flexion():
    tr = ElbowSimulation(SimConfig(dt=0.001, duration_s=2.0,
                                   theta0_rad=math.radians(140),
                                   u_biceps=1.0, u_triceps=0.0,
                                   gravity_on=False)).run()
    assert max(tr.theta) <= math.radians(145) + 1e-12
    for th, om in zip(tr.theta, tr.omega):
        if th >= math.radians(145):
            assert om == 0.0, \
                f"pinned at flexion stop with outward velocity {om}"


def test_moment_arm_interface_substitution():
    class TableStub(MomentArmModel):
        def biceps(self, theta_rad: float) -> float:
            return 0.04
        def triceps(self, theta_rad: float) -> float:
            return 0.02
        def is_extrapolated(self, theta_rad: float) -> bool:
            return False

    assert isinstance(MomentArmProvisional(), MomentArmModel)
    tr = ElbowSimulation(SimConfig(dt=0.001, duration_s=0.2),
                         moment_arm=TableStub()).run()
    assert len(tr.theta) == 201
    assert all(m == 0.04 for m in tr.ma_bic)
    assert all(m == 0.02 for m in tr.ma_tri)
