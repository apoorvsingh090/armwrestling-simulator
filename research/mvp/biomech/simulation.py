"""Deterministic fixed-timestep elbow simulation.

Separates (req. 4):
  anatomical_angle (rad, clinical) | muscle-tendon state (L, v_CE)
  activation (q)                   | force (N)
  torque (Nm)                      | joint state (theta, omega, alpha)

Fixed-step semi-implicit Euler, no randomness, no wall-clock dependence.
Biceps/triceps are separate Muscle objects (req. 5).
Fiber velocities from MA coupling (rigid tendon, C-09 branch A):
  vCE_bic = +MA_bic(theta)*omega   (flexion velocity shortens biceps)
  vCE_tri = -MA_tri(theta)*omega   (flexion lengthens triceps)
"""
from dataclasses import dataclass, field

from .units import require_si_angle_rad
from .activation import ZajacActivation
from .muscle import Biceps, Triceps
from .moment_arm import MomentArmModel, MomentArmProvisional
from .joint import ElbowJoint
from .dynamics import ElbowDynamics


@dataclass
class SimConfig:
    dt: float = 0.001
    duration_s: float = 3.0
    theta0_rad: float = 1.396  # 80 deg
    omega0: float = 0.0
    u_biceps: float = 0.8
    u_triceps: float = 0.2
    gravity_on: bool = True


@dataclass
class SimTrace:
    t: list = field(default_factory=list)
    theta: list = field(default_factory=list)
    omega: list = field(default_factory=list)
    alpha: list = field(default_factory=list)
    a_bic: list = field(default_factory=list)
    a_tri: list = field(default_factory=list)
    f_bic: list = field(default_factory=list)
    f_tri: list = field(default_factory=list)
    ma_bic: list = field(default_factory=list)
    ma_tri: list = field(default_factory=list)
    tau_net: list = field(default_factory=list)


class ElbowSimulation:
    def __init__(self, cfg: SimConfig | None = None,
                 activation: ZajacActivation | None = None,
                 biceps: Biceps | None = None,
                 triceps: Triceps | None = None,
                 moment_arm: MomentArmModel | None = None,
                 joint: ElbowJoint | None = None,
                 dynamics: ElbowDynamics | None = None):
        self.cfg = cfg or SimConfig()
        self.act = activation or ZajacActivation()
        self.bic = biceps or Biceps()
        self.tri = triceps or Triceps()
        self.ma = moment_arm or MomentArmProvisional()
        self.joint = joint or ElbowJoint()
        self.dyn = dynamics or ElbowDynamics(
            gravity_on=self.cfg.gravity_on)

    def run(self, excitation_fn=None) -> SimTrace:
        cfg = self.cfg
        n = int(round(cfg.duration_s / cfg.dt))
        require_si_angle_rad(float(cfg.theta0_rad))  # reject degree input BEFORE clamp
        theta = self.joint.clamp_anatomical(float(cfg.theta0_rad))
        omega = float(cfg.omega0)
        q_bic, q_tri = 0.0, 0.0
        trace = SimTrace()
        for i in range(n + 1):
            t = i * cfg.dt
            if excitation_fn is not None:
                u_bic, u_tri = excitation_fn(t)
            else:
                u_bic, u_tri = cfg.u_biceps, cfg.u_triceps
            ma_b = self.ma.biceps(theta)
            ma_t = self.ma.triceps(theta)
            v_b = ma_b * omega
            v_t = -ma_t * omega
            f_b, _ = self.bic.force(q_bic, theta, v_b)
            f_t, _ = self.tri.force(q_tri, theta, v_t)
            rest = self.joint.restraint_torque(theta, omega)
            tor = self.dyn.net_torque(ma_b, f_b, ma_t, f_t,
                                      theta, omega, rest)
            alpha = self.dyn.acceleration(tor["net"])
            trace.t.append(t)
            trace.theta.append(theta)
            trace.omega.append(omega)
            trace.alpha.append(alpha)
            trace.a_bic.append(q_bic)
            trace.a_tri.append(q_tri)
            trace.f_bic.append(f_b)
            trace.f_tri.append(f_t)
            trace.ma_bic.append(ma_b)
            trace.ma_tri.append(ma_t)
            trace.tau_net.append(tor["net"])
            if i == n:
                break
            # integrate: activation + semi-implicit Euler joint state
            q_bic = self.act.step(q_bic, u_bic, cfg.dt)
            q_tri = self.act.step(q_tri, u_tri, cfg.dt)
            omega = omega + alpha * cfg.dt
            theta = theta + omega * cfg.dt
            theta = self.joint.clamp_anatomical(theta)
            # Rigid-stop velocity projection (inelastic, restitution 0):
            # a clamped position with retained outward velocity claims motion
            # into a rigid wall. Zero the outward normal component only.
            if theta <= self.joint.ANAT_MIN_RAD and omega < 0.0:
                omega = 0.0
            elif theta >= self.joint.ANAT_MAX_RAD and omega > 0.0:
                omega = 0.0
        return trace
