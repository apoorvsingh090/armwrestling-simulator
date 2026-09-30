"""1-DOF elbow hinge (R1 stops; hard-stop velocity projection).

Choice documented: HARD stops with inelastic velocity projection (omega = 0
into the wall, restitution 0 — no bounce invented). Optional soft restraint
torque inside the feasible band; stiffness/damping default with warnings
(MVP PROV-09 surrogate for P021, preserved as-written in DB, not used directly).
"""
import math
import warnings


class HingeJoint:
    def __init__(self, anat_min_deg=0.0, anat_max_deg=145.0,
                 feas_min_deg=30.0, feas_max_deg=130.0,
                 restraint_k=15.0, restraint_c=1.0):
        warnings.warn("[HingeJoint] restraint k/c are PROVISIONAL surrogates for P021 "
                      "(100 Nm/deg as-written, intractable); sensitivity-sweep before claims.",
                      UserWarning, stacklevel=2)
        self.anat_min = math.radians(anat_min_deg)
        self.anat_max = math.radians(anat_max_deg)
        self.feas_min = math.radians(feas_min_deg)
        self.feas_max = math.radians(feas_max_deg)
        self.k = float(restraint_k)
        self.c = float(restraint_c)

    def clamp(self, theta):
        return min(self.anat_max, max(self.anat_min, theta))

    def project_velocity(self, theta, omega):
        if theta <= self.anat_min and omega < 0.0:
            return 0.0
        if theta >= self.anat_max and omega > 0.0:
            return 0.0
        return omega

    def restraint_torque(self, theta, omega):
        if theta < self.feas_min:
            return self.k * (self.feas_min - theta) - self.c * min(0.0, omega)
        if theta > self.feas_max:
            return -(self.k * (theta - self.feas_max)) - self.c * max(0.0, omega)
        return 0.0


def wrist_hinge(axis, restraint_k=0.0, restraint_c=0.0):
    """Wrist HingeJoint factory (additive; base class untouched).

    axis="fe": anat -70..+80 deg; axis="rud": anat -30..+20 deg (R1/AAOS).
    feas=anat so the (placeholder) restraint never fires in-ROM: end-range
    resistance comes from the Delp-anchored WristPassiveTorque curves instead.
    Restraint k/c default to ZERO (not the elbow P021 surrogate): pass explicit
    values only for experiments. OBLIQUE-AXIS FLAG: axes modeled orthogonal;
    R1 26.6deg obliquity deferred to Milestone 4.
    """
    import warnings as _w
    _w.warn("[wrist_hinge] WRIST OBLIQUE AXIS: 26.6deg oblique per R1; modeled orthogonal for MVP.",
            UserWarning, stacklevel=3)
    if axis == "fe":
        return HingeJoint(anat_min_deg=-70.0, anat_max_deg=80.0,
                          feas_min_deg=-70.0, feas_max_deg=80.0,
                          restraint_k=restraint_k, restraint_c=restraint_c)
    if axis == "rud":
        return HingeJoint(anat_min_deg=-30.0, anat_max_deg=20.0,
                          feas_min_deg=-30.0, feas_max_deg=20.0,
                          restraint_k=restraint_k, restraint_c=restraint_c)
    raise ValueError("axis must be 'fe' or 'rud'")
