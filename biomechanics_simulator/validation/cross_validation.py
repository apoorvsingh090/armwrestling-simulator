"""Cross-validation against published anchors (NO new data collected).

HONESTY NOTICE: moment-arm and ROM comparisons below check PIPELINE FIDELITY
(data -> table -> sim), NOT independent validation — the simulated values are
constructed from the same anchors they are compared against. Circularity is
declared per-row. The FORCE comparison is genuinely informative: Seth Fmax
vs PCSA x sigma exposes the bundle-map conflict (R2 directive 5) and FAILS
as it should. Thresholds 20%/50% PROVISIONAL. Torque data: MISSING (no source).
"""
import math

PASS_T, WARN_T = 0.20, 0.50


def _grade(sim_val, pub_val):
    err = abs(sim_val - pub_val) / abs(pub_val)
    if err < PASS_T:
        grade = "PASS"
    elif err < WARN_T:
        grade = "WARNING"
    else:
        grade = "FAIL"
    return {"sim": sim_val, "published": pub_val, "rel_err": err, "grade": grade}


class CrossValidator:
    def __init__(self, pass_tol=PASS_T, warn_tol=WARN_T):
        self.pass_tol = pass_tol
        self.warn_tol = warn_tol

    def validate_moment_arms(self, rows):
        """rows: {name: {"get": callable(theta)->m or float, "at": theta_or_None,
        "pub": published_m, "note": str}}."""
        out = {}
        for n, r in rows.items():
            v = r["get"](r["at"]) if callable(r["get"]) else float(r["get"])
            out[n] = {**_grade(v, r["pub"]), "note": r["note"]}
        return out

    def validate_rom(self, joints):
        """joints: {name: ((sim_min, sim_max), (pub_min, pub_max), note)}."""
        out = {}
        for n, ((a, b), (c, d), note) in joints.items():
            err = (abs(a - c) + abs(b - d)) / (abs(d - c) or 1.0)
            g = "PASS" if err < self.pass_tol else ("WARNING" if err < self.warn_tol else "FAIL")
            out[n] = {"sim": (a, b), "published": (c, d), "rel_err": err, "grade": g, "note": note}
        return out

    def validate_forces(self, rows):
        """rows: {name: (sim_Fmax, pcsa_cm2, sigma, note)} with pcsa-derived reference."""
        out = {}
        for n, (f, pcsa, sig, note) in rows.items():
            out[n] = {**_grade(f, pcsa * sig), "note": note}
        return out
