"""One-at-a-time sensitivity (MVP): hand displacement at a fixed horizon.

Outcome: x_B displacement (pin disabled by far geometry so NOTHING truncates:
pin_x huge). Rankings are PER-CONFIG (explicit-activation vs AI-driven runs
are not comparable); OAT ignores interactions (documented).
Parameter application is non-invasive: Fmax/kf/kr/mu/grip mutated + restored;
MA scales rebuild table objects (originals never mutated).
"""
import copy
import math
import warnings


def _scale_pchip(table, factor):
    from actuators.moment_arm import MomentArmTable
    xs_deg = [x * 180.0 / math.pi for x in table._pchip.xs]
    vals = [y * factor for y in table._pchip.ys]
    return MomentArmTable(table.name + "-scaled",
                          list(zip(xs_deg, vals, table.tags)))


def _scale_bilinear(table, factor):
    from actuators.moment_arm import BilinearTable
    return BilinearTable(table.name + "-scaled",
                         [r * 180.0 / math.pi for r in table.rows],
                         [c * 180.0 / math.pi for c in table.cols],
                         [[v * factor for v in row] for row in table.vals], "scaled")


def _scale_const(table, factor):
    from actuators.moment_arm import ConstantMA
    return ConstantMA(table.name + "-scaled", table.value_m * factor, table.tag + "+scaled")


def scale_table(table, factor):
    cls = type(table).__name__
    if cls == "MomentArmTable":
        return _scale_pchip(table, factor)
    if cls == "BilinearTable":
        return _scale_bilinear(table, factor)
    if cls == "ConstantMA":
        return _scale_const(table, factor)
    raise ValueError(f"cannot scale {cls}")


class SensitivityAnalyzer:
    def __init__(self, match_factory, specs, duration_s=0.25, pin_x_m=10.0):
        """specs: list of {name, kind, ...}, kind in
        Fmax/muscle_attr/grasp_mu/grip_max/ma_table. Each variant gets a FRESH
        match from the factory (mutations never leak). AI/controller params
        (reaction time, PD gains, transition thresholds) are OUT OF SCOPE for
        OAT here: they need controller-driven matches and longer horizons;
        covered by dedicated controller tests. Rankings are per-config only."""
        self.factory = match_factory
        self.specs = specs
        self.duration_s = duration_s
        self.pin_x_m = pin_x_m

    def _outcome(self, match):
        hist = match.run_match(self.duration_s, lambda t: {"pronator_teres": 1.0},
                               lambda t: {}, 1.0, 1.0)
        return abs(hist[-1]["x_B"] - hist[0]["x_B"])

    def _apply(self, match, spec, factor):
        both = (match.A, match.B)
        if spec["kind"] == "Fmax":
            for sim in both:
                for n in spec["muscles"]:
                    sim.muscles[n].Fmax_N *= factor
        elif spec["kind"] == "muscle_attr":
            for sim in both:
                for n in spec["muscles"]:
                    setattr(sim.muscles[n], spec["attr"],
                            getattr(sim.muscles[n], spec["attr"]) * factor)
        elif spec["kind"] == "grasp_mu":
            match.grasp.mu *= factor
            match.grip_A.mu *= factor
            match.grip_B.mu *= factor
        elif spec["kind"] == "grip_max":
            match.grip_A.max_grip_N *= factor
            match.grip_B.max_grip_N *= factor
        elif spec["kind"] == "ma_table":
            for sim in both:
                for n, key in spec["entries"]:
                    sim.mt[n][key] = scale_table(sim.mt[n][key], factor)
        else:
            raise ValueError(f"unknown spec kind {spec['kind']}")
        return match

    def run_oat(self, perturbation=0.2):
        rows = []
        base_m = self.factory()
        base_m.pin_x = self.pin_x_m
        base = self._outcome(base_m)
        for spec in self.specs:
            outs = {}
            for f in (1.0 - perturbation, 1.0 + perturbation):
                m = self.factory()
                m.pin_x = self.pin_x_m
                self._apply(m, spec, f)
                outs[f] = self._outcome(m)
            idx = abs(outs[1.0 + perturbation] - outs[1.0 - perturbation]) / (2 * perturbation)
            rows.append({"parameter": spec["name"], "baseline_outcome": base,
                         "down": outs[1.0 - perturbation], "up": outs[1.0 + perturbation],
                         "sensitivity_index": idx})
        rows.sort(key=lambda r: r["sensitivity_index"], reverse=True)
        return rows
