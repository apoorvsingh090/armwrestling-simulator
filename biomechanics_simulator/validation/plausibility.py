"""Match plausibility gates (flag bands, not validation).

Ranges: pin 1-30 s plausible (<0.5 or >60 WARNING); hand speed < 2 m/s;
activations in [0,1] (FAIL if violated — clamping invariant); joints within
R1 anatomical ROM (FAIL); contact |Ft| < 5000 N. Bands are general
observations (task-specific data unavailable); each finding carries its rule.
"""
import math

ROM = {"theta": (0.0, math.radians(145)), "phi": (math.radians(-87), math.radians(80)),
       "phi_wfe": (math.radians(-70), math.radians(80)),
       "phi_rud": (math.radians(-30), math.radians(20))}


class PlausibilityChecker:
    def __init__(self, pin_fast=0.5, pin_slow=60.0, vmax=2.0, fmax=5000.0):
        self.pin_fast, self.pin_slow, self.vmax, self.fmax = pin_fast, pin_slow, vmax, fmax

    def check_match(self, history):
        findings = []
        pins = [(s["t"], s["pin"]) for s in history if s["pin"] is not None]
        if pins:
            t, w = pins[0]
            if t < self.pin_fast:
                findings.append({"level": "WARNING", "check": "pin_time",
                                 "detail": f"pin at {t:.3f}s < {self.pin_fast}s (test-rig fast)"})
            elif t > self.pin_slow:
                findings.append({"level": "WARNING", "check": "pin_time",
                                 "detail": f"pin at {t:.1f}s > {self.pin_slow}s"})
        xs = [(s["x_A"], s["x_B"]) for s in history]
        ts = [s["t"] for s in history]
        peak_v = 0.0
        for i in range(1, len(xs)):
            dt = ts[i] - ts[i - 1]
            if dt > 0:
                peak_v = max(peak_v, abs(xs[i][0] - xs[i - 1][0]) / dt,
                             abs(xs[i][1] - xs[i - 1][1]) / dt)
        if peak_v > self.vmax:
            findings.append({"level": "WARNING", "check": "hand_velocity",
                             "detail": f"peak {peak_v:.2f} m/s > {self.vmax}"})
        peak_f = 0.0
        for s in history:
            peak_f = max(peak_f, abs(s["contact"]["Ft_on_A"]))
            for key in ("theta", "phi", "phi_wfe", "phi_rud"):
                lo, hi = ROM[key]
                for tag in ("A", "B"):
                    q = s[tag][key]
                    if not (lo - 1e-9 <= q <= hi + 1e-9):
                        findings.append({"level": "FAIL", "check": "joint_rom",
                                         "detail": f"{tag}.{key}={q:.3f} outside ROM"})
        if peak_f > self.fmax:
            findings.append({"level": "WARNING", "check": "contact_force",
                             "detail": f"peak |Ft| {peak_f:.0f} N > {self.fmax}"})
        return findings

    def check_activations(self, activations):
        bad = {n: a for n, a in activations.items() if not (0.0 <= a <= 1.0)}
        if bad:
            return [{"level": "FAIL", "check": "activation_bounds", "detail": str(bad)}]
        return []
