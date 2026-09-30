"""Table contact elements (M6): ElbowPad, Peg, PinPad, TableTop.

All Hunt-Crossley k/d/n and Coulomb mu are constructor-REQUIRED (r3: pad vinyl
CoF unmeasured, no stiffness data anywhere — UNKNOWN). Geometry from WAF rules
(E). Classes operate on EXPLICIT probe kinematics; only PinPad reaction is
wired into sim dynamics (lateral hand force -> roll torque, M5 power-consistent
path). Elbow/peg/table forces have no generalized coordinate to act on in the
fixed-base MVP (documented per method); they are fully tested primitives awaiting
a mobile base / free hand (M7+).
"""
import math
import warnings


class _HCRequired:
    @staticmethod
    def need_hc(hc):
        if hc is None:
            raise ValueError("Hunt-Crossley model UNKNOWN for this pair: pass explicit k/d/n")


class ElbowPad:
    """7x7x2in vinyl dense-foam pad (E:WAF2024 geometry). k/d/n + mu REQUIRED."""

    def __init__(self, top_z, half_extent_xy, hc, mu_pad):
        _HCRequired.need_hc(hc)
        if mu_pad is None:
            raise ValueError("mu_pad UNKNOWN (pad vinyl unmeasured): pass explicit value")
        self.top_z = float(top_z)
        self.half = float(half_extent_xy)
        self.hc = hc
        self.mu = float(mu_pad)

    def contact(self, elbow_z, elbow_vz, elbow_xy=(0.0, 0.0)):
        """Vertical unilateral contact + lateral friction (pure functions)."""
        inside = abs(elbow_xy[0]) <= self.half and abs(elbow_xy[1]) <= self.half
        delta = self.top_z - elbow_z if inside else 0.0
        fn = self.hc.normal_force(delta, -elbow_vz) if inside else 0.0
        return {"contact": delta > 0, "penetration": max(0.0, delta),
                "Fn": fn, "on_pad": inside}

    def tangential(self, Fn, v_lateral):
        """Coulomb lateral friction (pure function; no lateral elbow state
        exists in-sim to consume it — tested on explicit kinematics)."""
        if v_lateral == 0:
            return 0.0, True
        return -self.mu * Fn * (1.0 if v_lateral > 0 else -1.0), False

    def check_lift(self, elbow_z):
        """True = separated above surface (illegal-move detector input ONLY;
        enforcement is game/referee logic, not physics)."""
        return elbow_z > self.top_z


class Peg:
    """1in-dia x 6in peg as vertical PLANE (flagged cylinder simplification).
    Free hand is UNMODELED: pure-function reactions on explicit kinematics."""

    def __init__(self, plane_x, mu_peg, hc=None):
        if mu_peg is None:
            raise ValueError("mu_peg UNKNOWN: pass explicit value")
        self.plane_x = float(plane_x)
        self.mu = float(mu_peg)
        self.hc = hc
        warnings.warn("[Peg] plane simplification of 1in cylinder; free hand unmodeled.",
                      UserWarning, stacklevel=2)

    def contact(self, hand_x, hand_vx, hand_vz=0.0):
        delta = self.plane_x - hand_x if hand_x is not None else 0.0
        if hand_x is None or delta <= 0:
            return {"contact": False, "F_react": 0.0, "F_friction": 0.0}
        if self.hc is None:
            raise ValueError("peg normal needs explicit HuntCrossley (stiffness UNKNOWN)")
        fn = self.hc.normal_force(delta, -hand_vx)
        return {"contact": True, "F_react": fn,
                "F_friction": -self.mu * fn * (1.0 if hand_vz > 0 else (-1.0 if hand_vz < 0 else 0.0))}


class PinPad:
    """Touch-pad contact gate: pinned iff normal force exceeds threshold.

    Threshold is caller POLICY (not physics): required, no default.
    Friction along pad (vertical sliding) is a pure function (no vertical hand
    state exists in-sim to consume it)."""

    def __init__(self, plane_x, side, hc, mu_pad, force_threshold_N=None):
        _HCRequired.need_hc(hc)
        if mu_pad is None:
            raise ValueError("pad mu UNKNOWN: pass explicit value")
        self.plane_x = float(plane_x)
        self.side = side  # +1: B's pad at +x; -1: A's pad at -x
        self.hc = hc
        self.mu = float(mu_pad)
        self.threshold = force_threshold_N

    def contact(self, hand_x, hand_vx):
        pen = (hand_x - self.plane_x) * self.side
        if pen <= 0:
            return {"contact": False, "penetration": 0.0, "Fn": 0.0, "pinned": False}
        fn = self.hc.normal_force(pen, -self.side * hand_vx)
        pinned = (fn > self.threshold) if self.threshold is not None else None
        return {"contact": True, "penetration": pen, "Fn": fn, "pinned": pinned}

    def friction_along_pad(self, Fn, vz):
        if vz == 0:
            return 0.0, True
        return -self.mu * Fn * (1.0 if vz > 0 else -1.0), False


class TableTop:
    """Table-top plane reuse note: PlaneSurface (contact_detection) IS the table
    model (z-up at WAF stand height). No new physics here; see its tests."""

    def __init__(self, plane):
        self.plane = plane
