"""Contact constitutive models (forms STD; parameters caller-supplied).

No parameter below is measured for arm-wrestling interfaces (C-07/C-08/D-02):
every coefficient is constructor-REQUIRED (no defaults manufactured), except
Serina regime thresholds, which ARE empirical (<1 N compliant, >4 N bottomed).
"""
import math


class HuntCrossley:
    """F = k*d^n + d_c*d^n*ddot, d>=0; 0 (and >=0 always: no tension)."""

    def __init__(self, k, d, n=1.5):
        self.k, self.d, self.n = float(k), float(d), float(n)

    def normal_force(self, penetration_m, penetration_vel_m_s):
        if penetration_m <= 0:
            return 0.0
        f = self.k * penetration_m**self.n + self.d * penetration_m**self.n * penetration_vel_m_s
        return max(0.0, f)


class CoulombFriction:
    """mu = k_mu * N^(n_mu-1); |Ft| <= mu*Fn; opposes slip; isotropic MVP."""

    def __init__(self, k_mu, n_mu):
        self.k_mu, self.n_mu = float(k_mu), float(n_mu)

    def friction_coefficient(self, normal_force_N):
        if normal_force_N <= 0:
            return 0.0
        return self.k_mu * normal_force_N**(self.n_mu - 1.0)

    def tangential_force(self, normal_force_N, tangential_vel_m_s, required_N=0.0):
        """Returns (force, stuck). Dynamic (sliding): capped, opposed, stuck=False.
        Static: required clamped to cone; stuck True iff fully held."""
        mu = self.friction_coefficient(normal_force_N)
        cap = mu * normal_force_N
        if abs(tangential_vel_m_s) > 0.0:
            return -cap * (1.0 if tangential_vel_m_s > 0 else -1.0), False
        held = max(-cap, min(cap, required_N))
        return held, abs(required_N) <= cap


class SerinaPulpLaw:
    """Regime classification from E thresholds + transition weight.

    weight 0 below 1 N, 1 above 4 N, smoothstep between (documented FORM).
    Multiplies caller-supplied stiffness; no stiffness numbers live here.
    """

    @staticmethod
    def regime(force_N):
        if force_N < 1.0:
            return "compliant"
        if force_N > 4.0:
            return "bottomed"
        return "transition"

    @staticmethod
    def transition_weight(force_N):
        if force_N <= 1.0:
            return 0.0
        if force_N >= 4.0:
            return 1.0
        t = (force_N - 1.0) / 3.0
        return t * t * (3.0 - 2.0 * t)
