"""Hand-to-hand grasp contact (M5): compliant bristle + Coulomb cone.

Normal force: Fn = min(Fn_A, Fn_B) — weaker grip governs (spec §2).
Tangential: Ft_raw = -(kt*dt + ct*v_rel), clamped to mu*Fn (spec §4).
Newton's third law is EXACT: F_on_B = -F_on_A by single negation.
k/ct/mu are constructor-REQUIRED (all UNKNOWN in r3 for this pair).
No-slip emerges (bounded dt); slip emerges (cone-saturated, dt grows).
"""

class HandToHandContact:
    def __init__(self, friction_mu, tangential_k, tangential_c, lever_m):
        self.mu = float(friction_mu)
        self.kt = float(tangential_k)
        self.ct = float(tangential_c)
        self.lever = float(lever_m)
        self.delta_t = 0.0

    def reset(self):
        self.delta_t = 0.0

    def relative_velocity(self, omega_f_A, omega_f_B):
        return self.lever * (omega_f_A + omega_f_B)  # d/dt(x_A - x_B)

    def compute(self, Fn_A, Fn_B, v_rel, dt):
        fn = min(Fn_A, Fn_B)
        self.delta_t += v_rel * dt
        raw = -(self.kt * self.delta_t + self.ct * v_rel)
        cap = self.mu * fn
        if abs(raw) <= cap:
            ft_A, slipped = raw, False
        else:
            ft_A = cap * (1.0 if raw > 0 else -1.0)
            slipped = True
        return {"Fn": fn, "Ft_on_A": ft_A, "Ft_on_B": -ft_A,
                "slipped": slipped, "delta_t": self.delta_t, "cap": cap}

