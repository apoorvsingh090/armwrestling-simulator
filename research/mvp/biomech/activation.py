"""Zajac first-order activation dynamics (E-08, C-10 branch A, default).

dq/dt = (u - q)/tau + beta*(q0 - q)
  u    : neural excitation in [0,1] (dimensionless)
  q    : activation in [0,1] (dimensionless)
  tau  : tau_a when u > q else tau_d (s)
  beta : deactivation-boost gain (dimensionless)
  q0   : basal activation (dimensionless)

Evidence:
  tau_a P052 EMPIRICAL 0.01..0.05 s (default 0.03)
  tau_d P053 EMPIRICAL 0.04 s
  beta  P054 MODEL_DERIVED 0.1..1.0 (default 0.5)
  q0    P055 MODEL_DERIVED 0.001..0.05 (default 0.01)
"""
from dataclasses import dataclass


@dataclass
class ActivationState:
    activation: float  # q in [0,1]


class ZajacActivation:
    def __init__(self, tau_a: float = 0.03, tau_d: float = 0.04,
                 beta: float = 0.5, q0: float = 0.01):
        if not (0.001 <= tau_a <= 0.2):
            raise ValueError("tau_a out of plausible range")
        if not (0.001 <= tau_d <= 0.2):
            raise ValueError("tau_d out of plausible range")
        self.tau_a = float(tau_a)
        self.tau_d = float(tau_d)
        self.beta = float(beta)
        self.q0 = float(q0)

    def derivative(self, q: float, u: float) -> float:
        tau = self.tau_a if u > q else self.tau_d
        return (u - q) / tau + self.beta * (self.q0 - q)

    def step(self, q: float, u: float, dt: float) -> float:
        u_c = min(1.0, max(0.0, u))
        dq = self.derivative(q, u_c)
        q_new = q + dq * dt
        return min(1.0, max(0.0, q_new))
