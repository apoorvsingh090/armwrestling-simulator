"""test_validation_report: generation is total, sections complete, Markdown
valid. ALSO WRITES validation/VALIDATION_REPORT.md (the required artifact;
single-sourced here so it can never drift from the code)."""
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

warnings.simplefilter("ignore")

from validation.report import ValidationReport
from helpers_validation import consistency_ctx, ma_rows, rom_rows, force_rows
from helpers_4dof import build_4dof_sim
from helpers_match import build_match

ARTIFACT = os.path.join(os.path.dirname(__file__), "..", "validation", "VALIDATION_REPORT.md")


def test_report_generates_and_saves():
    sim, _ = build_4dof_sim()
    m = build_match()
    hist = m.run_match(0.3, lambda t: {"pronator_teres": 0.5}, lambda t: {}, 1.0, 1.0)
    acts = {n: 0.5 for n in sim.muscles}
    rep = ValidationReport({"consistency": consistency_ctx(), "ma_rows": ma_rows(sim),
                            "rom_rows": rom_rows(sim), "force_rows": force_rows(),
                            "demo_match": hist, "demo_activations": acts})
    sections = rep.generate()
    assert set(sections) == {"consistency", "moment_arms", "rom", "forces",
                             "plausibility", "activations", "sensitivity", "monte_carlo"}
    md = rep.to_markdown()
    for h in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7."):
        assert h in md
    assert "FAIL" in md  # failures reported, never hidden (force rows)
    with open(ARTIFACT, "w", encoding="utf-8") as f:
        f.write(md)
    assert os.path.getsize(ARTIFACT) > 1000
