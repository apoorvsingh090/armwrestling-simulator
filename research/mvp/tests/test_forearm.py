"""Forearm rotation scaffold tests (10 required).

All torques come from test-local stub providers (interface only) — no
biomechanical values are asserted beyond corpus-traced limits/directions.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from biomech.forearm import (
    ForearmConfig, ForearmRotationDynamics, ForearmRotationJoint,
    ForearmRotationSim, RotationActuator,
)
from biomech.units import DEG2RAD


class ConstTorque(RotationActuator):
    def __init__(self, tau: float):
        self.tau = tau
    def torque(self, phi_rad, omega, activation, elbow_theta_rad=None):
        return self.tau * max(0.0, min(1.0, activation))


class ActivationScaled(RotationActuator):
    def __init__(self, per_act: float):
        self.per_act = per_act
    def torque(self, phi_rad, omega, activation, elbow_theta_rad=None):
        return self.per_act * activation


def make_sim(k=10.0, c=0.5, I=0.01, damp=0.05):
    return ForearmRotationSim(ForearmRotationJoint(k, c),
                              ForearmRotationDynamics(I, damp))


def test_zero_position_convention():
    j = ForearmRotationJoint(10.0, 0.5)
    assert j.clamp_anatomical(0.0) == 0.0
    assert j.restraint_torque(0.0, 0.0) == 0.0
    assert j.FEAS_SUP_RAD < 0.0 < j.FEAS_PRON_RAD


def test_positive_rotation_pronation():
    sim = make_sim()
    tr = sim.run(ForearmConfig(dt=0.001, duration_s=0.5),
                 pronator=ConstTorque(1.0), pro_act=1.0)
    assert tr.phi[-1] > 0.0, "pronator torque must drive +phi (pronation)"


def test_negative_rotation_supination():
    sim = make_sim()
    tr = sim.run(ForearmConfig(dt=0.001, duration_s=0.5),
                 supinator=ConstTorque(1.0), sup_act=1.0)
    assert tr.phi[-1] < 0.0, "supinator torque must drive -phi (supination)"


def test_anatomical_limits():
    j = ForearmRotationJoint(10.0, 0.5)
    assert j.clamp_anatomical(10.0) == j.ANAT_PRON_MAX_RAD
    assert j.clamp_anatomical(-10.0) == j.ANAT_SUP_MAX_RAD
    assert abs(j.ANAT_PRON_MAX_RAD - 80.0 * DEG2RAD) < 1e-12   # P010 upper end
    assert abs(j.ANAT_SUP_MAX_RAD + 87.0 * DEG2RAD) < 1e-12    # P011 upper end
    sim = make_sim()
    tr = sim.run(ForearmConfig(dt=0.001, duration_s=3.0),
                 pronator=ConstTorque(5.0), pro_act=1.0)
    assert max(tr.phi) <= j.ANAT_PRON_MAX_RAD + 1e-12


def test_torque_direction():
    d = ForearmRotationDynamics(0.01, 0.0)
    t = d.net_torque(2.0, 0.0, 0.0, 0.0, 0.0)
    assert t["tau_pronator"] > 0 and t["net"] > 0
    t2 = d.net_torque(0.0, 2.0, 0.0, 0.0, 0.0)
    assert t2["tau_supinator"] < 0 and t2["net"] < 0


def test_dimensional_consistency():
    d = ForearmRotationDynamics(inertia=0.01, damping=0.05)
    assert d.acceleration(0.1) == 0.1 / 0.01  # Nm/kg m^2 = rad/s^2
    t = d.net_torque(1.0, 0.5, 0.1, 0.0, 2.0)
    assert abs(t["net"] - (1.0 - 0.5 + 0.1 - 0.05 * 2.0)) < 1e-12
    try:
        ForearmRotationSim(ForearmRotationJoint(10.0, 0.5), d).run(
            ForearmConfig(phi0_rad=90.0))  # degrees as radians
        raise AssertionError("degree input not rejected")
    except ValueError:
        pass


def test_deterministic_repeatability():
    sim = make_sim()
    kw = dict(cfg=ForearmConfig(dt=0.001, duration_s=0.5),
              pronator=ConstTorque(1.0), pro_act=0.8)
    assert sim.run(**kw).phi == sim.run(**kw).phi


def test_timestep_sensitivity():
    outs = []
    for dt in (0.001, 0.0005):
        tr = make_sim().run(ForearmConfig(dt=dt, duration_s=1.0),
                            pronator=ConstTorque(1.0), pro_act=0.8)
        outs.append(tr.phi[-1])
    assert abs(outs[0] - outs[1]) < math.radians(1.0)


def test_zero_activation():
    sim = make_sim()
    tr = sim.run(ForearmConfig(dt=0.001, duration_s=0.5),
                 pronator=ActivationScaled(3.0), pro_act=0.0,
                 supinator=ActivationScaled(3.0), sup_act=0.0)
    assert all(abs(p) < 1e-12 for p in tr.phi), "zero activation must give zero motion"
    assert all(abs(t) < 1e-12 for t in tr.tau_net)


def test_opposing_torques_and_elbow_compat():
    sim = make_sim()
    tr = sim.run(ForearmConfig(dt=0.001, duration_s=0.5),
                 pronator=ConstTorque(2.0), pro_act=1.0,
                 supinator=ConstTorque(2.0), sup_act=1.0)
    assert all(abs(p) < 1e-9 for p in tr.phi), "equal oppose must cancel"
    # elbow subsystem unchanged: baseline scenario still settles identically
    from biomech.simulation import ElbowSimulation, SimConfig
    eth = ElbowSimulation(SimConfig()).run().theta[-1] * 57.29577951308232
    assert abs(eth - 140.212) < 0.01, f"elbow baseline moved: {eth}"
