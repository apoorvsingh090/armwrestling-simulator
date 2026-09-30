"""3-element Hill-type muscle actuator (rigid-tendon branch, C-09).

F = Fmax * a * fL(l) * fV(v) * cos(pennation) + Fpassive(l)

Constitution rule 4: every non-empirical default is a tagged placeholder that
raises a console warning at construction. Empirical values (PCSA) warn nothing.
MODEL rows (Seth bundle values) warn as calibration-flagged.
Tendon slack is stored for the future compliant branch; the rigid branch does
not consume it (warned, not silent).

Sources: R2_MUSCLE_TENDON_SPEC.md (Zajac1989 STD; E-11 linear FV corpus branch;
passive exponential, eps0 1.8). NO coefficients invented: FL width defaults to
the MVP's documented provisional (0.30*Lopt) WITH warning; vmax defaults to
10*Lopt/s WITH warning.

Fatigue (M8): F_avail state with first-order ODE
  dF_avail/dt = -kf*a*F_avail*ctype(v) + kr*(Fmax - F_avail).
Active force uses F_avail; passive uses Fmax_baseline (unaffected). kf/kr and
contraction factors are PROVISIONAL (general exercise physiology; arm-wrestling
rates UNKNOWN). Fmax_N itself is NEVER mutated (baseline preserved).
"""
import math
import warnings

UNSET = object()

# Global fatigue defaults (PROVISIONAL): kf 0.001-0.01, kr 0.0005-0.005 (slower).
FATIGUE_KF_DEFAULT = 0.005
FATIGUE_KR_DEFAULT = 0.002
# Contraction-type factors (PROVISIONAL; eccentric < isometric < concentric).
FATIGUE_CONCENTRIC = 1.0
FATIGUE_ISOMETRIC = 0.8
FATIGUE_ECCENTRIC = 0.6
FATIGUE_V_DEADBAND_FRAC = 1e-3  # |v| < 0.1% vmax counts as isometric (numerical zero)


def _warn(tag, msg):
    warnings.warn(f"[HillMuscle:{tag}] {msg}", UserWarning, stacklevel=3)


class HillMuscle:
    def __init__(self, name, Fmax_N=UNSET, Lopt_m=UNSET, pennation_deg=0.0,
                 slack_m=UNSET, fl_width_frac=UNSET, vmax_lopt_per_s=UNSET,
                 passive_eps0=1.8, kf=UNSET, kr=UNSET):
        self.name = name
        if Fmax_N is UNSET:
            raise ValueError("Fmax_N is UNKNOWN: pass an explicit value (no default manufactured)")
        self.Fmax_N = float(Fmax_N)
        if Lopt_m is UNSET:
            raise ValueError("Lopt_m is UNKNOWN: pass an explicit value (no default manufactured)")
        self.Lopt_m = float(Lopt_m)
        self.pennation_rad = math.radians(float(pennation_deg))
        if slack_m is UNSET:
            self.slack_m = None
            _warn("slack", "tendon slack UNKNOWN: stored as None; rigid branch proceeds, compliant branch blocked")
        else:
            self.slack_m = float(slack_m)
            _warn("slack", "rigid-tendon branch: slack stored but NOT consumed (C-09 branch A)")
        if fl_width_frac is UNSET:
            self.fl_width_frac = 0.30
            _warn("fl-width", "PROVISIONAL default 0.30*Lopt (no corpus value): sensitivity-sweep before credibility claims")
        else:
            self.fl_width_frac = float(fl_width_frac)
        if vmax_lopt_per_s is UNSET:
            self.vmax_lopt_per_s = 10.0
            _warn("vmax", "PROVISIONAL default 10*Lopt/s (no arm-muscle value): sensitivity-sweep before credibility claims")
        else:
            self.vmax_lopt_per_s = float(vmax_lopt_per_s)
        self.passive_eps0 = float(passive_eps0)  # STD:Zajac1989 suggested 1.8 (range 1.1-1.8)
        if kf is UNSET:
            self.kf = FATIGUE_KF_DEFAULT
            _warn("kf", "PROVISIONAL global kf=0.005/s (no arm-muscle rates): calibrate from sustained-contraction data")
        else:
            self.kf = float(kf)
        if kr is UNSET:
            self.kr = FATIGUE_KR_DEFAULT
            _warn("kr", "PROVISIONAL global kr=0.002/s (no arm-muscle rates): calibrate from recovery data")
        else:
            self.kr = float(kr)
        self.F_avail = float(self.Fmax_N)  # fully rested; reset_fatigue() restores

    @property
    def sigma_fl_m(self):
        return self.fl_width_frac * self.Lopt_m

    @property
    def vmax_m_s(self):
        return self.vmax_lopt_per_s * self.Lopt_m

    def fL(self, length_m):
        """Active force-length, Gaussian (Zajac form class). Dimensionless."""
        x = (length_m - self.Lopt_m) / self.sigma_fl_m
        return math.exp(-0.5 * x * x)

    def fV(self, velocity_m_s):
        """Force-velocity, linear E-11 corpus branch, clamped. Dimensionless.

        Convention: velocity > 0 = fiber SHORTENING (concentric).
        Lengthening (v < 0) exceeds isometric, capped (no eccentric realism, F7).

        Force-Velocity Model: Linear (E-11)
        Limitation: Underestimates force reduction at high concentric velocities
        compared to hyperbolic Zajac form. Eccentric cap = 1.5×Fmax.
        Upgrade path: Replace with hyperbolic Zajac when Af constant is available
        from literature. See R2_MUSCLE_TENDON_SPEC.md §Tendon/curves.
        """
        fv = 1.0 - velocity_m_s / self.vmax_m_s
        return min(1.5, max(0.0, fv))

    def fPE(self, length_m):
        """Passive exponential, zero at/below Lopt (Zajac class, eps0 STD). Dimensionless."""
        if length_m <= self.Lopt_m:
            return 0.0
        strain = (length_m - self.Lopt_m) / self.Lopt_m
        return (math.exp(strain / (self.passive_eps0 - 1.0)) - 1.0) / (math.exp(1.0) - 1.0)

    def contraction_factor(self, velocity_m_s):
        """PROVISIONAL type factors: concentric 1.0 / isometric 0.8 / eccentric 0.6."""
        if abs(velocity_m_s) <= FATIGUE_V_DEADBAND_FRAC * self.vmax_m_s:
            return FATIGUE_ISOMETRIC
        return FATIGUE_CONCENTRIC if velocity_m_s > 0 else FATIGUE_ECCENTRIC

    def update_fatigue(self, activation, velocity_m_s, dt):
        """Explicit-Euler fatigue ODE step (dt << 1/kf: hyper-stable).
        a=0 recovers toward baseline; NO hidden drains (only this ODE)."""
        a = min(1.0, max(0.0, activation))
        c = self.contraction_factor(velocity_m_s)
        dF = (-self.kf * a * c * self.F_avail
              + self.kr * (self.Fmax_N - self.F_avail)) * dt
        self.F_avail = min(self.Fmax_N, max(0.0, self.F_avail + dF))
        return self.F_avail

    def reset_fatigue(self):
        self.F_avail = float(self.Fmax_N)
        return self.F_avail

    @property
    def fatigue_fraction(self):
        if self.Fmax_N <= 0:
            return 0.0  # inert placeholder (Fmax=0): no capacity to lose
        return 1.0 - self.F_avail / self.Fmax_N

    def force(self, activation, length_m, velocity_m_s):
        """Total fiber force in NEWTONS. activation clamped to [0,1].
        Active term uses F_avail (fatigue); passive uses Fmax_baseline (immune)."""
        a = min(1.0, max(0.0, activation))
        f_active = (self.F_avail * a * self.fL(length_m)
                    * self.fV(velocity_m_s) * math.cos(self.pennation_rad))
        f_pass = self.Fmax_N * self.fPE(length_m)
        return f_active + f_pass
