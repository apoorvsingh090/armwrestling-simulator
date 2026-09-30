"""Provisional angle-dependent moment-arm interpolation layer.

STATUS: PROVISIONAL INTERPOLATION — NOT experimentally validated.
Only the peak anchors are empirical:
  biceps  P038 EMPIRICAL 4.7 cm peak (cadaveric tendon excursion)
  triceps P041 EMPIRICAL 2.3 cm peak
Everything else about the shape is an IMPLEMENTATION ASSUMPTION.

Form (E-12 required form, coefficients UNKNOWN in corpus):
  MA_bic(theta)  = peak_bic  * (0.65 + 0.35*sin(theta))
  MA_tri(theta)  = peak_tri  * (0.70 + 0.30*sin(theta + 0.3))
  theta in radians, clinical 0 = full extension, flexion positive.

Properties:
- C1 continuous (sin-based), strictly positive on 0..145 deg.
- Peak of biceps exactly at 90 deg (= peak anchor). Triceps peaks at
  ~72.8 deg with exactly the anchor value; at 90 deg it evaluates 1.3%
  below peak (measured 1.34% — shape assumption, not a finding).
- Variation ~35% (biceps) / ~30% (triceps) across ROM, consistent with
  P050 (>=30% variation over 95-deg arc) which forbids constant-MA models
  (constant-MA torque error ~35%, P051).
- Validity range for fitted functions per F6 grid: 5..140 deg. Evaluation
  outside is EXTRAPOLATED (flagged by caller).

Do NOT cite interpolated values as measurements. Anchors only.
"""
import math
from abc import ABC, abstractmethod


class MomentArmModel(ABC):
    """Replaceable moment-arm interface (AUDIT 2 recommendation).

    Muscle and joint-dynamics code must depend ONLY on this interface, so a
    future empirical lookup table, interpolated measurement set, or fitted
    function (E-12 coefficients from the F6 workflow) can be substituted
    without touching muscle.py, joint.py, dynamics.py, or simulation.py.
    All implementations: theta in SI radians (clinical 0 = full extension),
    returns meters, C1 continuity expected, validity domain declared.
    """

    @abstractmethod
    def biceps(self, theta_rad: float) -> float: ...

    @abstractmethod
    def triceps(self, theta_rad: float) -> float: ...

    @abstractmethod
    def is_extrapolated(self, theta_rad: float) -> bool: ...


class MomentArmProvisional(MomentArmModel):
    VALID_MIN_DEG = 5.0
    VALID_MAX_DEG = 140.0

    def __init__(self, peak_biceps_m: float = 0.047,
                 peak_triceps_m: float = 0.023):
        self.peak_bic = float(peak_biceps_m)
        self.peak_tri = float(peak_triceps_m)

    @staticmethod
    def _bic_shape(theta_rad: float) -> float:
        return 0.65 + 0.35 * math.sin(theta_rad)

    @staticmethod
    def _tri_shape(theta_rad: float) -> float:
        return 0.70 + 0.30 * math.sin(theta_rad + 0.3)

    def biceps(self, theta_rad: float) -> float:
        return self.peak_bic * self._bic_shape(theta_rad)

    def triceps(self, theta_rad: float) -> float:
        return self.peak_tri * self._tri_shape(theta_rad)

    def is_extrapolated(self, theta_rad: float) -> bool:
        deg = theta_rad * 180.0 / math.pi
        return deg < self.VALID_MIN_DEG or deg > self.VALID_MAX_DEG
