"""Elbow rigid-body angular dynamics (E-02/E-03, single hinge).

I * alpha = tau_muscle + tau_gravity + tau_restraint - c*omega
  tau_muscle = MA_bic*F_bic - MA_tri*F_tri (flexion positive, E-03)
  tau_gravity PROVISIONAL: -m*g*d*sin(theta), upper arm fixed vertical down,
      forearm COM distance d. m, d, I are NOT from corpus (UNKNOWN there).
  c joint viscous damping PROVISIONAL (NOT P059: that is 2.5 Ns/m linear
      tendon damping, different quantity/units — documented, not reused).

Defaults (all PROVISIONAL/ASSUMPTION, see parameters.py):
  I = 0.06 kg*m^2, m = 1.5 kg, d = 0.18 m, c = 0.3 Nms/rad.
"""
from .units import GRAVITY


class ElbowDynamics:
    def __init__(self, inertia: float = 0.06, forearm_mass: float = 1.5,
                 com_distance: float = 0.18, damping: float = 0.3,
                 gravity_on: bool = True):
        self.I = float(inertia)
        self.m = float(forearm_mass)
        self.d = float(com_distance)
        self.c = float(damping)
        self.gravity_on = bool(gravity_on)

    def gravity_torque(self, theta_rad: float) -> float:
        if not self.gravity_on:
            return 0.0
        import math
        return -self.m * GRAVITY * self.d * math.sin(theta_rad)

    def net_torque(self, ma_bic: float, f_bic: float, ma_tri: float,
                   f_tri: float, theta: float, omega: float,
                   restraint: float) -> dict:
        tau_bic = ma_bic * f_bic
        tau_tri = -ma_tri * f_tri
        tau_g = self.gravity_torque(theta)
        tau_damp = -self.c * omega
        net = tau_bic + tau_tri + tau_g + restraint + tau_damp
        return {"tau_biceps": tau_bic, "tau_triceps": tau_tri,
                "tau_gravity": tau_g, "tau_restraint": restraint,
                "tau_damping": tau_damp, "net": net}

    def acceleration(self, net_torque: float) -> float:
        return net_torque / self.I
