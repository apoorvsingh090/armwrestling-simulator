"""Hill-type muscle force (E-10 reference form + E-11 minimal rigid-tendon branch).

F = a * Fmax * f_L(L) * f_v(v)
  a     : activation [0,1] from Zajac ODE (E-08)
  Fmax  : PCSA * specific_tension
  f_L   : Gaussian force-length, E-11: exp(-0.5*((L-Lopt)/sigma)^2)
  f_v   : linear force-velocity, E-11: 1 - v_CE/v_max (clamped)
  Rigid tendon: L_MTU = L_CE (C-09 branch A, ~20% Fmax MAE P060).

Evidence status per muscle (biceps / triceps as single-head equivalents):
  PCSA  P026/P027 EMPIRICAL (cadaveric, n=10): 4.6 / 10.3 cm^2
  Lopt  P026/P027 EMPIRICAL: 23.2 / 45.4 cm (preserved as-written;
        triceps value is unusually long — flagged, not corrected)
  sigma_specific_tension: PROVISIONAL 50 N/cm^2 (NOT from corpus).
        Corpus gives NO specific tension (equations.md absent #2).
  sigma_FL width: PROVISIONAL 0.30*Lopt (corpus absent).
  v_max: PROVISIONAL 10*Lopt/s (corpus absent).
  theta_opt (angle of Lopt): PROVISIONAL 90 deg (corpus absent).
  Missing heads (biceps short head, triceps lateral/medial): UNKNOWN —
        each object models its named long head only.

Force arises ONLY from a*Fmax*fL*fv. No strength multipliers anywhere.
"""
import math

from .units import require_si_angle_rad


class Muscle:
    def __init__(self, name: str, pcsa_cm2: float, lopt_m: float,
                 specific_tension_N_per_cm2: float = 50.0,
                 fl_width_frac: float = 0.30, vmax_lopt_per_s: float = 10.0,
                 theta_opt_rad: float = math.pi / 2,
                 peak_ma_m: float = 0.04):
        self.name = name
        self.pcsa_cm2 = float(pcsa_cm2)
        self.lopt_m = float(lopt_m)
        self.sigma_tension = float(specific_tension_N_per_cm2)
        self.fmax_N = self.pcsa_cm2 * self.sigma_tension
        self.sigma_fl_m = float(fl_width_frac) * self.lopt_m
        self.vmax_m_s = float(vmax_lopt_per_s) * self.lopt_m
        self.theta_opt = float(theta_opt_rad)
        self.peak_ma_m = float(peak_ma_m)

    def fiber_length(self, theta_rad: float) -> float:
        """Provisional length model: L = Lopt + MA_peak*(theta_opt - theta).

        Linear surrogate for integral of MA over angle. PROVISIONAL.
        """
        require_si_angle_rad(theta_rad)
        return self.lopt_m + self.peak_ma_m * (self.theta_opt - theta_rad)

    def force_length(self, length_m: float) -> float:
        x = (length_m - self.lopt_m) / self.sigma_fl_m
        return math.exp(-0.5 * x * x)

    def force_velocity(self, vce_m_s: float) -> float:
        """Linear concentric law, clamped. No eccentric realism (per F7)."""
        fv = 1.0 - vce_m_s / self.vmax_m_s
        return min(1.5, max(0.0, fv))

    def force(self, activation: float, theta_rad: float,
              vce_m_s: float) -> tuple:
        L = self.fiber_length(theta_rad)
        fL = self.force_length(L)
        fv = self.force_velocity(vce_m_s)
        F = activation * self.fmax_N * fL * fv
        return F, {"fiber_length_m": L, "fL": fL, "fv": fv,
                   "fmax_N": self.fmax_N}


class Biceps(Muscle):
    def __init__(self, **kw):
        super().__init__("biceps", pcsa_cm2=4.6, lopt_m=0.232,
                         peak_ma_m=0.047, **kw)


class Triceps(Muscle):
    def __init__(self, **kw):
        super().__init__("triceps", pcsa_cm2=10.3, lopt_m=0.454,
                         peak_ma_m=0.023, **kw)
