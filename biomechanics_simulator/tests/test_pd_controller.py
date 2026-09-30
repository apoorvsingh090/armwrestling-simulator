"""test_pd_controller: tracking, allocation, redundancy, clamping, zero-gain."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from helpers_4dof import build_4dof_sim
from helpers_ctrl import pd_wiring, KP, KD
from controllers.base_controller import PDController


def _pd(sim):
    muscles, ma = pd_wiring(sim)
    return PDController(muscles, ma, dict(KP), dict(KD))


def _state(sim):
    return {"elbow": (sim.seg.theta, sim.seg.omega),
            "forearm": (sim.phi, sim.omega_f),
            "wrist_fe": (sim.phi_wfe, sim.omega_wfe),
            "wrist_rud": (sim.phi_rud, sim.omega_rud),
            "ma_args": {"theta": sim.seg.theta, "theta_f": sim.phi}}


def test_tracking_reduces_error():
    import warnings
    warnings.simplefilter("ignore")
    sim, _ = build_4dof_sim(theta0_deg=90.0)
    pd = _pd(sim)
    tgt = {"elbow": (math.radians(100.0), 0.0, {"biceps_long": 1.0})}
    e0 = abs(math.radians(100.0) - sim.seg.theta)
    for _ in range(500):
        st = {"elbow": (sim.seg.theta, sim.seg.omega),
              "forearm": (sim.phi, sim.omega_f),
              "wrist_fe": (sim.phi_wfe, sim.omega_wfe),
              "wrist_rud": (sim.phi_rud, sim.omega_rud),
              "ma_args": {"theta": sim.seg.theta, "theta_f": sim.phi}}
        sim.step(pd.compute_activations(tgt, st))
    assert abs(math.radians(100.0) - sim.seg.theta) < e0


def test_allocation_signs_and_redundancy():
    import warnings
    warnings.simplefilter("ignore")
    sim, _ = build_4dof_sim(theta0_deg=90.0)
    pd = _pd(sim)
    st = _state(sim)
    acts = pd.compute_activations(
        {"elbow": (math.radians(120.0), 0.0,
                   {"biceps_long": 1.0, "brachioradialis": 1.0, "pronator_teres": 1.0})}, st)
    assert acts["biceps_long"] > 0 and acts["brachioradialis"] > 0  # redundancy shared
    assert acts["pronator_teres"] > 0 and acts["triceps_long"] == 0.0  # extensors off


def test_clamp_and_zero_gain():
    import warnings
    warnings.simplefilter("ignore")
    sim, _ = build_4dof_sim(theta0_deg=90.0)
    pd = _pd(sim)
    st = _state(sim)
    acts = pd.compute_activations(
        {"elbow": (math.radians(145.0), 0.0, {"biceps_long": 1.0})}, st)
    assert all(0.0 <= a <= 1.0 for a in acts.values())
    muscles, ma = pd_wiring(sim)
    pd0 = PDController(muscles, ma, {d: 0.0 for d in KP}, {d: 0.0 for d in KD})
    acts0 = pd0.compute_activations(
        {"elbow": (math.radians(145.0), 0.0, {"biceps_long": 1.0})}, st)
    assert all(a == 0.0 for a in acts0.values())
