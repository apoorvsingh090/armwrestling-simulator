"""test_dynamic_response: biceps flexion, triceps eccentric braking, hard stop."""
import math
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

warnings.simplefilter("ignore")
from core.integrator import SemiImplicitEuler
from core.rigid_body import Segment
from core.joint import HingeJoint
from actuators.hill_muscle import HillMuscle
from actuators.moment_arm import load_elbow_tables
from core.simulation import Simulation

BASE = os.path.join(os.path.dirname(__file__), "..")


def make_sim(theta0_deg, omega0=0.0, g=0.0, k=15.0, c=1.0):
    ma = load_elbow_tables(os.path.join(BASE, "data", "r2_mtus.json"))
    bic = HillMuscle("biceps_long", Fmax_N=485.8, Lopt_m=0.1412, slack_m=0.257)
    tri = HillMuscle("triceps_long", Fmax_N=1580.6, Lopt_m=0.0969,
                     pennation_deg=10.0, slack_m=0.241)
    seg = Segment("forearm", mass_kg=1.5, com_m=0.18, inertia_kgm2=0.06,
                  theta0_rad=math.radians(theta0_deg), omega0=omega0, wrist_m=0.30)
    sim = Simulation(seg, HingeJoint(restraint_k=k, restraint_c=c),
                     {"biceps_long": bic, "triceps_long": tri},
                     {"biceps_long": ma["biceps"], "triceps_long": ma["triceps"]},
                     SemiImplicitEuler(dt=0.001), gravity_m_s2=g)
    return sim, bic, tri


def test_biceps_contraction():
    sim, bic, _ = make_sim(90.0)
    rep0 = sim.compute_torques(sim.seg.theta, 0.0, {"biceps_long": 1.0, "triceps_long": 0.0})
    alpha0 = rep0["net"] / 0.06
    st = sim.step({"biceps_long": 1.0, "triceps_long": 0.0})
    assert st["omega"] == pytest.approx(alpha0 * 0.001)
    assert st["omega"] > 0.0
    assert st["theta"] > math.pi / 2  # flexion advances
    assert rep0["forces"]["biceps_long"] == pytest.approx(485.8)  # Lopt, rest


def test_triceps_eccentric_braking():
    sim, _, tri = make_sim(45.0, omega0=2.0)
    states = sim.compute_muscle_state(math.radians(45.0), 2.0)
    L_t, v_t = states["triceps_long"]
    assert v_t < 0.0  # flexion lengthens triceps
    assert tri.fV(v_t) > 1.0  # eccentric enhancement
    om0 = sim.seg.omega
    sim.step({"biceps_long": 0.0, "triceps_long": 1.0})
    assert sim.seg.omega < om0  # triceps brakes flexion


def test_joint_stop_behavior():
    # Start 1° from the stop with 2 rad/s: triceps passive (~5 Nm brake) cannot
    # absorb the kinetic energy before 145°, so the hard stop is genuinely hit.
    sim, _, _ = make_sim(144.0, omega0=2.0, k=0.0, c=0.0)
    Jn = sim.joint.anat_max
    states = []
    for _ in range(2000):
        st = sim.step({"biceps_long": 0.0, "triceps_long": 0.0})
        states.append((st["theta"], st["omega"]))
    assert all(t <= Jn + 1e-12 for t, _ in states)
    hits = [(t, w) for t, w in states if t >= Jn - 1e-12]
    assert hits, "must reach the stop"
    # projection invariant: pinned AT the stop carries no outward velocity
    # (passive forces may legitimately pull the joint off the stop later)
    assert all(w == 0.0 for _, w in hits), "no retained outward velocity, no bounce"
