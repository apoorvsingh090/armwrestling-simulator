"""Rigid-body segment (M1: single forearm). SI units throughout.

Mass/inertia UNKNOWN for the forearm in R1 (humerus P019/P020 only) —
constructor REQUIRES explicit values (no defaults manufactured):
pass anthropometric estimates and heed the warnings.
"""
import warnings


class Segment:
    def __init__(self, name, mass_kg, com_m, inertia_kgm2, theta0_rad=0.0,
                 omega0=0.0, wrist_m=None):
        for label in ("mass_kg", "com_m", "inertia_kgm2"):
            warnings.warn(
                f"[Segment:{name}] {label} is UNKNOWN (no forearm values in R1): "
                "REQUIRES ANTHROPOMETRIC DATA.", UserWarning, stacklevel=2)
        self.name = name
        self.mass_kg = float(mass_kg)
        self.com_m = float(com_m)
        self.inertia_kgm2 = float(inertia_kgm2)
        self.theta = float(theta0_rad)
        self.omega = float(omega0)
        self.wrist_m = None if wrist_m is None else float(wrist_m)
        if wrist_m is None:
            warnings.warn(f"[Segment:{name}] wrist distance UNKNOWN: external-load lever unset",
                          UserWarning, stacklevel=2)


class HandSegment(Segment):
    """Hand as rigid endpoint (additive; base class untouched).

    Mass/COM/inertia UNKNOWN (no R1 values) -> constructor REQUIRES explicit
    values and the base warnings fire. Mass is STORED, not integrated: hand
    gravity is OMITTED (COM unmeasured; documented simplification warned at
    attach). grip_lever_m: wrist-to-grip-center distance (PROVISIONAL 0.08).
    """

    def __init__(self, mass_kg, com_m, inertia_kgm2, grip_lever_m=None):
        if grip_lever_m is None:
            raise ValueError("grip_lever_m UNKNOWN: pass explicit value (no default manufactured)")
        super().__init__("hand", mass_kg, com_m, inertia_kgm2, wrist_m=grip_lever_m)
        warnings.warn("[HandSegment] grip lever is caller-supplied PROVISIONAL (~0.08 m, no corpus value).",
                      UserWarning, stacklevel=2)
        warnings.warn("[HandSegment] hand gravity OMITTED (COM unmeasured); mass stored-not-integrated.",
                      UserWarning, stacklevel=2)
