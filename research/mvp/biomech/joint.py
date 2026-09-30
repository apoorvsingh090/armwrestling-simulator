"""Elbow joint: 1-DOF hinge, clinical 0 = full extension (C-01 resolution).

  P006 IMPLEMENT_WITH_RANGE: anatomical 0..145 deg (ACTIVE_ROM, general human)
  P017 ASSUMPTION: feasible placeholder 30..130 deg (ADL-derived, NOT measured;
       ARM_WRESTLING_MEASURED_ROM is UNKNOWN for every joint, C-18)
  P021 MODEL_DERIVED as-written 100 Nm/deg + 0.001745 Nm*s/deg (Holzbaur via
       Rankin): preserved in parameter DB but NOT used directly — at SI scale
       100 Nm/deg = 5729 Nm/rad is numerically intractable at 1 kHz and
       implausible as a linear stiffness. MVP uses a stable soft restraint
       (PROVISIONAL k=15 Nm/rad, c=1.0 Nms/rad) applied beyond the feasible
       placeholder, with a hard clamp at anatomical stops. Deviation logged
       in IMPLEMENTATION_STATUS.md.
"""
import math

from .units import DEG2RAD


class ElbowJoint:
    ANAT_MIN_RAD = 0.0
    ANAT_MAX_RAD = 145.0 * DEG2RAD
    FEAS_MIN_RAD = 30.0 * DEG2RAD
    FEAS_MAX_RAD = 130.0 * DEG2RAD

    def __init__(self, restraint_k: float = 15.0, restraint_c: float = 1.0):
        self.k = float(restraint_k)
        self.c = float(restraint_c)

    def clamp_anatomical(self, theta: float) -> float:
        return min(self.ANAT_MAX_RAD, max(self.ANAT_MIN_RAD, theta))

    def restraint_torque(self, theta: float, omega: float) -> float:
        # Soft restraint beyond feasible placeholder; hard stops enforced by
        # clamp_anatomical. Spring pushes back toward feasible band, damper
        # opposes velocity deeper into violation.
        if theta < self.FEAS_MIN_RAD:
            return self.k * (self.FEAS_MIN_RAD - theta) - self.c * min(0.0, omega)
        elif theta > self.FEAS_MAX_RAD:
            return -self.k * (theta - self.FEAS_MAX_RAD) - self.c * max(0.0, omega)
        return 0.0
