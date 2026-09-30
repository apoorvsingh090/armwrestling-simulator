"""ValidationReport: runs fast checks, renders Markdown with all sections.

Slow analyses (OAT sensitivity, Monte Carlo) are evidenced by their dedicated
test modules, not re-run here; their sections state exactly that (no fake
freshness). generate() returns the section dict; to_markdown() renders it.
"""
from validation.consistency import ConsistencyChecker
from validation.cross_validation import CrossValidator
from validation.plausibility import PlausibilityChecker


class ValidationReport:
    def __init__(self, ctx):
        """ctx: {"consistency": {...}, "ma_rows": ..., "rom_rows": ...,
        "force_rows": ..., "demo_match": [...], "demo_activations": {...}}"""
        self.ctx = ctx
        self.sections = {}

    def generate(self):
        cc = ConsistencyChecker()
        self.sections["consistency"] = cc.run_all(self.ctx["consistency"])
        cv = CrossValidator()
        self.sections["moment_arms"] = cv.validate_moment_arms(self.ctx["ma_rows"])
        self.sections["rom"] = cv.validate_rom(self.ctx["rom_rows"])
        self.sections["forces"] = cv.validate_forces(self.ctx["force_rows"])
        pc = PlausibilityChecker()
        self.sections["plausibility"] = pc.check_match(self.ctx["demo_match"])
        self.sections["activations"] = pc.check_activations(self.ctx["demo_activations"])
        self.sections["sensitivity"] = {"status": "see tests/test_sensitivity.py",
                                        "note": "OAT evidence lives in the dedicated suite (not re-run here)."}
        self.sections["monte_carlo"] = {"status": "see tests/test_monte_carlo.py",
                                        "note": "N-sample evidence lives in the dedicated suite."}
        return self.sections

    def to_markdown(self):
        L = ["# VALIDATION REPORT — arm-wrestling simulator (physics engine)",
             "",
             "Thresholds 20%/50% PROVISIONAL; MA/ROM rows are pipeline-fidelity "
             "(circular by construction, declared); force rows expose the R2 "
             "bundle-map conflict; torque data MISSING.",
             ""]
        L.append("## 1. Internal consistency")
        for name, r in self.sections["consistency"].items():
            L.append(f"- {name}: **{r['status']}** — {r['detail']}")
        L.append("")
        for title, key in (("2. Moment arms", "moment_arms"), ("3. ROM", "rom"), ("4. Forces", "forces")):
            L.append(f"## {title}")
            for name, r in self.sections[key].items():
                L.append(f"- {name}: **{r['grade']}** (rel err {r['rel_err']:.3f}) — {r['note']}")
            L.append("")
        L.append("## 5. Plausibility findings")
        if self.sections["plausibility"]:
            for f in self.sections["plausibility"]:
                L.append(f"- {f['level']} [{f['check']}] {f['detail']}")
        else:
            L.append("- none: demo match inside all bands")
        L.append("")
        L.append("## 6. Sensitivity / Monte Carlo")
        L.append(f"- sensitivity: {self.sections['sensitivity']['status']}")
        L.append(f"- monte carlo: {self.sections['monte_carlo']['status']}")
        L.append("")
        L.append("## 7. Known limitations")
        L.extend(["- No sport-specific validation data (D-01 cap: Partially Validated at best).",
                  "- MA/ROM rows are circular (same anchors built the tables).",
                  "- Torque references missing; friction/fatigue rates provisional.",
                  "- OAT ignores interactions; MC at MVP scale (see test files)."])
        return "\n".join(L) + "\n"
