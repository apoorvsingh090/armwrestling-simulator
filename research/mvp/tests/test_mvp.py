"""MVP automated tests — one function per requirement (req. 12).

Covers: activation dynamics, force-length, force-velocity, moment-arm
interpolation, torque direction, elbow limits, deterministic repeatability,
timestep sensitivity, dimensional/unit consistency.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from biomech.activation import ZajacActivation
from biomech.muscle import Biceps, Triceps
from biomech.moment_arm import MomentArmProvisional
from biomech.joint import ElbowJoint
from biomech.dynamics import ElbowDynamics
from biomech.simulation import ElbowSimulation, SimConfig
from biomech.units import DEG2RAD


def test_activation_dynamics():
    act = ZajacActivation(tau_a=0.03, tau_d=0.04, beta=0.5, q0=0.01)
    q, dt = 0.0, 0.001
    for _ in range(30):  # 30 ms = tau_a
        q = act.step(q, 1.0, dt)
    assert 0.45 < q < 0.75, f"step response at tau_a should be ~63%, got {q}"
    for _ in range(4000):
        q = act.step(q, 1.0, dt)
    assert q > 0.95, f"activation should saturate near 1, got {q}"
    for _ in range(40):  # 40 ms = tau_d
        q = act.step(q, 0.0, dt)
    assert q < 0.6, f"deactivation should decay, got {q}"
    q_rest = 0.0
    for _ in range(2000):
        q_rest = act.step(q_rest, 0.0, dt)
    assert 0.0 <= q_rest <= 0.05, f"rest should settle near q0 band, got {q_rest}"


def test_force_length_behaviour():
    bic = Biceps()
    th_opt = bic.theta_opt
    f_opt, _ = bic.force(1.0, th_opt, 0.0)
    f_ext, _ = bic.force(1.0, 0.0, 0.0)
    f_flex, _ = bic.force(1.0, 145.0 * DEG2RAD, 0.0)
    assert f_opt > 0
    assert f_ext < f_opt and f_flex < f_opt, "FL must peak at Lopt"
    assert abs(bic.force_length(bic.lopt_m) - 1.0) < 1e-12
    far = bic.force_length(bic.lopt_m + 5 * bic.sigma_fl_m)
    assert far < 0.05, f"far-from-optimum FL should be ~0, got {far}"


def test_force_velocity_behaviour():
    bic = Biceps()
    th = bic.theta_opt
    f_iso, _ = bic.force(1.0, th, 0.0)
    f_con, _ = bic.force(1.0, th, 0.5 * bic.vmax_m_s)
    assert 0.4 * f_iso < f_con < f_iso, "concentric shortening must reduce force"
    f_fast, _ = bic.force(1.0, th, 5 * bic.vmax_m_s)
    assert f_fast == 0.0, "beyond vmax concentric force clamps to 0"
    f_ecc, _ = bic.force(1.0, th, -bic.vmax_m_s)
    assert f_ecc > f_iso, "linear model lengthening gives > isometric (clamped 1.5x)"


def test_moment_arm_interpolation():
    ma = MomentArmProvisional()
    th90 = 90.0 * DEG2RAD
    assert abs(ma.biceps(th90) - 0.047) < 1e-9, "biceps anchor 4.7 cm at 90 deg"
    assert abs(ma.triceps(th90) - 0.023 * (0.70 + 0.30 * math.sin(th90 + 0.3))) < 1e-12
    for deg in (0, 30, 60, 90, 120, 145):
        assert ma.biceps(deg * DEG2RAD) > 0
        assert ma.triceps(deg * DEG2RAD) > 0
    # C1 check via finite differences (no kinks)
    eps = 1e-5
    for deg in (20, 80, 130):
        th = deg * DEG2RAD
        d1 = (ma.biceps(th + eps) - ma.biceps(th - eps)) / (2 * eps)
        d2 = (ma.biceps(th + 2 * eps) - ma.biceps(th - 2 * eps)) / (4 * eps)
        assert abs(d1 - d2) < 1e-4, f"C1 fail at {deg} deg"
    var = (ma.biceps(th90) - ma.biceps(0.0)) / ma.biceps(th90)
    assert 0.25 < var < 0.45, f"variation should be ~35%, got {var}"
    assert ma.is_extrapolated(2.0 * DEG2RAD)
    assert not ma.is_extrapolated(th90)


def test_torque_direction():
    dyn = ElbowDynamics(gravity_on=False, damping=0.0)
    ma = MomentArmProvisional()
    th = 90.0 * DEG2RAD
    t = dyn.net_torque(ma.biceps(th), 200.0, ma.triceps(th), 0.0, th, 0.0, 0.0)
    assert t["tau_biceps"] > 0 and t["net"] > 0, "biceps must flex (+)"
    t2 = dyn.net_torque(ma.biceps(th), 0.0, ma.triceps(th), 200.0, th, 0.0, 0.0)
    assert t2["tau_triceps"] < 0 and t2["net"] < 0, "triceps must extend (-)"


def test_elbow_limits():
    joint = ElbowJoint()
    assert joint.clamp_anatomical(-0.5) == 0.0
    assert joint.clamp_anatomical(10.0) == joint.ANAT_MAX_RAD
    lo = joint.FEAS_MIN_RAD - 0.2
    assert joint.restraint_torque(lo, 0.0) > 0, "below feasible must push +"
    hi = joint.FEAS_MAX_RAD + 0.2
    assert joint.restraint_torque(hi, 0.0) < 0, "above feasible must push -"
    mid = 90.0 * DEG2RAD
    assert joint.restraint_torque(mid, 1.0) == 0.0


def test_deterministic_repeatability():
    cfg = SimConfig(dt=0.001, duration_s=1.0)
    r1 = ElbowSimulation(cfg).run().theta
    r2 = ElbowSimulation(cfg).run().theta
    assert r1 == r2, "identical configs must give bit-identical traces"


def test_timestep_sensitivity():
    c1 = SimConfig(dt=0.001, duration_s=2.0)
    c2 = SimConfig(dt=0.0005, duration_s=2.0)
    r1 = ElbowSimulation(c1).run().theta[-1]
    r2 = ElbowSimulation(c2).run().theta[-1]
    assert abs(r1 - r2) < math.radians(2.0), f"dt convergence fail: {r1} vs {r2}"


def test_dimensional_unit_consistency():
    bic, tri = Biceps(), Triceps()
    # Fmax units: cm^2 * N/cm^2 = N
    assert bic.fmax_N == 4.6 * 50.0 and tri.fmax_N == 10.3 * 50.0
    th = 90.0 * DEG2RAD
    ma = MomentArmProvisional()
    F, _ = bic.force(0.5, th, 0.0)
    tau = ma.biceps(th) * F  # m * N = Nm
    assert 0 < tau < 50, f"elbow torque implausible: {tau} Nm"
    dyn = ElbowDynamics()
    assert dyn.acceleration(6.0) == 6.0 / 0.06  # Nm / kg m^2 = rad/s^2
    try:
        bic.fiber_length(90.0)  # degrees passed as radians -> must raise
        raise AssertionError("degree input not rejected")
    except ValueError:
        pass
