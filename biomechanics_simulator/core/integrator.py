"""Fixed-step deterministic integrators (SI units). MVP: semi-implicit Euler."""


class SemiImplicitEuler:
    """Symplectic Euler: v += a*dt THEN x += v*dt. Stable for stiff restraints."""

    def __init__(self, dt=0.001):
        self.dt = float(dt)

    def step_theta(self, theta, omega, alpha):
        omega_new = omega + alpha * self.dt
        theta_new = theta + omega_new * self.dt
        return theta_new, omega_new
