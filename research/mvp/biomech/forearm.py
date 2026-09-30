"""Forearm pronation/supination scaffold — interface + kinematics ONLY.

DECISION (FOREARM_ROTATION_SPEC.md §12): evidence is insufficient for numerical
rotation muscles, so this module manufactures NO muscle parameters, NO
moment-arm shape, NO length law, and NO dynamics defaults. It provides:

  RotationActuator (ABC)  — torque provider interface; a future Hill-based PT /
      supinator (or fitted 2-D MA) implements this without touching joint code.
      Optional elbow_theta channel carries the QUALITATIVELY-supported coupling
      (§8); no coupling coefficients exist, default None = uncoupled.
  ForearmRotationJoint    — neutral-zero (+pronation/−supination, SI radians),
      anatomical hard stops +80°/−87° (P010/P011 upper ends), soft restraint
      from feasible ±50° (P018 ASSUMPTION). Stiffness/damping are
      constructor-REQUIRED (no corpus values → no defaults).
  ForearmRotationDynamics — 1-DOF Euler hinge; inertia + damping REQUIRED
      (UNKNOWN in corpus → no defaults). Gravity about the longitudinal axis
      is 0 under the symmetric-mass assumption (hand-offset gravity deferred).
  ForearmRotationSim      — deterministic fixed-step semi-implicit Euler with
      inelastic hard-stop velocity projection (same pattern as elbow MVP).

SI units throughout. No contact, no hand, no techniques.
"""
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .units import DEG2RAD, require_si_angle_rad


class RotationActuator(ABC):
    """Torque provider for one rotation direction.

    Implementations return signed-or-unsigned torque in Nm; the dynamics layer
    assigns direction (pronator +, supinator −). Activation in [0,1].
    elbow_theta_rad carries elbow coupling for future 2-D MA use (None = off).
    """

    @abstractmethod
    def torque(self, phi_rad: float, omega: float, activation: float,
               elbow_theta_rad: float | None = None) -> float:
        ...


class ForearmRotationJoint:
    ANAT_PRON_MAX_RAD = 80.0 * DEG2RAD   # P010 upper end (ACTIVE_ROM)
    ANAT_SUP_MAX_RAD = -87.0 * DEG2RAD   # P011 upper end (ACTIVE_ROM)
    FEAS_PRON_RAD = 50.0 * DEG2RAD       # P018 ASSUMPTION placeholder
    FEAS_SUP_RAD = -50.0 * DEG2RAD       # P018 ASSUMPTION placeholder
    PASSIVE_ADDER_DEG = (3.0, 5.0)       # P012 margin (documented, no curve)

    def __init__(self, restraint_k: float, restraint_c: float):
        # REQUIRED: no corpus-supported defaults exist (UNKNOWN).
        self.k = float(restraint_k)
        self.c = float(restraint_c)

    def clamp_anatomical(self, phi: float) -> float:
        return min(self.ANAT_PRON_MAX_RAD,
                   max(self.ANAT_SUP_MAX_RAD, phi))

    def restraint_torque(self, phi: float, omega: float) -> float:
        if phi < self.FEAS_SUP_RAD:
            return self.k * (self.FEAS_SUP_RAD - phi) - self.c * min(0.0, omega)
        elif phi > self.FEAS_PRON_RAD:
            return -self.k * (phi - self.FEAS_PRON_RAD) - self.c * max(0.0, omega)
        return 0.0


class ForearmRotationDynamics:
    def __init__(self, inertia: float, damping: float):
        # REQUIRED: rotational inertia UNKNOWN in corpus → no default.
        self.I = float(inertia)
        self.c = float(damping)

    def gravity_torque(self, phi_rad: float) -> float:
        # Longitudinal rotation axis: symmetric-mass assumption → 0.
        # Hand-COM-offset gravity is UNKNOWN/deferred (spec §6).
        return 0.0

    def net_torque(self, tau_pronator: float, tau_supinator: float,
                   tau_passive: float, phi: float, omega: float) -> dict:
        tau_p = tau_pronator
        tau_s = -tau_supinator
        tau_d = -self.c * omega
        net = tau_p + tau_s + tau_passive + tau_d
        return {"tau_pronator": tau_p, "tau_supinator": tau_s,
                "tau_passive": tau_passive, "tau_damping": tau_d,
                "net": net}

    def acceleration(self, net_torque: float) -> float:
        return net_torque / self.I


@dataclass
class ForearmConfig:
    dt: float = 0.001
    duration_s: float = 1.0
    phi0_rad: float = 0.0
    omega0: float = 0.0


@dataclass
class ForearmTrace:
    t: list = field(default_factory=list)
    phi: list = field(default_factory=list)
    omega: list = field(default_factory=list)
    alpha: list = field(default_factory=list)
    tau_net: list = field(default_factory=list)


class ForearmRotationSim:
    def __init__(self, joint: ForearmRotationJoint,
                 dynamics: ForearmRotationDynamics):
        self.joint = joint
        self.dyn = dynamics

    def run(self, cfg: ForearmConfig | None = None,
            pronator: RotationActuator | None = None, pro_act: float = 0.0,
            supinator: RotationActuator | None = None, sup_act: float = 0.0,
            passive: RotationActuator | None = None,
            elbow_theta_fn=None) -> ForearmTrace:
        cfg = cfg or ForearmConfig()
        require_si_angle_rad(float(cfg.phi0_rad))  # reject degree input BEFORE clamp
        phi = self.joint.clamp_anatomical(float(cfg.phi0_rad))
        omega = float(cfg.omega0)
        n = int(round(cfg.duration_s / cfg.dt))
        trace = ForearmTrace()
        for i in range(n + 1):
            t = i * cfg.dt
            eth = elbow_theta_fn(t) if elbow_theta_fn is not None else None
            t_p = pronator.torque(phi, omega, pro_act, eth) if pronator else 0.0
            t_s = supinator.torque(phi, omega, sup_act, eth) if supinator else 0.0
            t_pas = passive.torque(phi, omega, 0.0, eth) if passive else 0.0
            rest = self.joint.restraint_torque(phi, omega)
            tor = self.dyn.net_torque(t_p, t_s, t_pas + rest, phi, omega)
            alpha = self.dyn.acceleration(tor["net"])
            trace.t.append(t)
            trace.phi.append(phi)
            trace.omega.append(omega)
            trace.alpha.append(alpha)
            trace.tau_net.append(tor["net"])
            if i == n:
                break
            omega = omega + alpha * cfg.dt
            phi = phi + omega * cfg.dt
            phi = self.joint.clamp_anatomical(phi)
            if phi <= self.joint.ANAT_SUP_MAX_RAD and omega < 0.0:
                omega = 0.0
            elif phi >= self.joint.ANAT_PRON_MAX_RAD and omega > 0.0:
                omega = 0.0
        return trace
