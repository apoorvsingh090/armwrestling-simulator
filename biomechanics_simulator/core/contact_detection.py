"""Contact detection primitives + grip model (kinematics-light MVP).

Points carry position/velocity callbacks (world-frame suppliers); surfaces are
infinite planes (peg simplified to a plane per spec). No FK lives here: the
caller (tests now, full chain in M5) supplies positions. Table geometry loads
from r3 JSON (E:WAF2024); forces on those planes remain UNKNOWN.
"""
import math
import warnings


class ContactPoint:
    def __init__(self, name, position_fn, velocity_fn):
        self.name = name
        self.pos = position_fn
        self.vel = velocity_fn


class PlaneSurface:
    """Plane: normal.n (unit) + offset c. Penetration of point p (moving with v):
    delta = -(n.p + c) if inside (n.p + c < 0); rate = -(n.v). Unilateral."""

    def __init__(self, name, normal, offset):
        n = [float(x) for x in normal]
        l = math.sqrt(sum(x * x for x in n))
        self.name = name
        self.n = [x / l for x in n]
        self.c = float(offset)

    def query(self, p, v):
        s = sum(a * b for a, b in zip(self.n, p)) + self.c
        rate = -(sum(a * b for a, b in zip(self.n, v)))
        if s >= 0:
            return {"contact": False, "penetration": 0.0, "rate": 0.0}
        return {"contact": True, "penetration": -s, "rate": rate}


class ContactDetector:
    @staticmethod
    def detect(points, surfaces):
        out = []
        for pt in points:
            p, v = pt.pos(), pt.vel()
            for sf in surfaces:
                q = sf.query(p, v)
                if q["contact"]:
                    out.append({"point": pt.name, "surface": sf.name, **q})
        return out


def load_table_planes(path):
    """WAF planes in sim frame (z up, table top at stand height by default).

    Elbow-pad top plane + table-top plane + peg plane (x-normal, MVP plane
    simplification of the 1in-dia cylinder at its nominal station).
    Touch-pad plane height 0.1016 m = 4in WAF touch-pad height     (WAF geometric).
    Geometry E:WAF2024; all force parameters UNKNOWN (not loaded).
    """
    import json
    with open(path, encoding="utf-8") as f:
        g = json.load(f)["table_geometry_SI"]
    top = g["height_stand_m"][0]
    pad_top = top + g["elbow_pad_thick_m"][0]
    return {"table_top": PlaneSurface("table_top", [0, 0, 1], -top),
            "elbow_pad": PlaneSurface("elbow_pad", [0, 0, 1], -pad_top),
            "touch_pad": PlaneSurface("touch_pad", [0, 0, 1], -(top + 0.1016)),
            "peg": PlaneSurface("peg", [1, 0, 0], 0.33)}


class GripModel:
    """Scalar grip: Fn = activation * max_grip_N. Slip iff |demand| > mu*Fn.

    max_grip default 462 N = E male-mean n=12 (override per population).
    mu is EXPLICIT (pair UNKNOWN in sim context): no default manufactured.
    """

    def __init__(self, max_grip_N=462.0, mu=None):
        warnings.warn("[GripModel] max_grip 462N = E male-mean n=12; override per cohort.",
                      UserWarning, stacklevel=2)
        if mu is None:
            raise ValueError("mu UNKNOWN for the sim pair: pass explicit value (proxy or calibrated)")
        self.max_grip_N = float(max_grip_N)
        self.mu = float(mu)

    def normal_force(self, activation):
        return max(0.0, min(1.0, activation)) * self.max_grip_N

    def slip_state(self, activation, tangential_demand_N):
        fn = self.normal_force(activation)
        cap = self.mu * fn
        slipped = abs(tangential_demand_N) > cap
        return {"Fn": fn, "cap": cap, "slipped": slipped,
                "held": max(-cap, min(cap, tangential_demand_N))}
