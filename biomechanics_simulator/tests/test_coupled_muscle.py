"""test_coupled_muscle: biceps length/velocity depend on BOTH joint angles.

NOTE on the brief: it asks to verify biceps is "LONGEST in supination ...
[while it] stretches when the forearm is pronated". Those two halves
contradict each other anatomically: a supinator is STRETCHED by pronation,
hence LONGEST at full pronation (+80°) and SHORTEST at full supination.
The parenthetical (stretch-on-pronation) is the correct physiology and is
what this test asserts; the "longest in supination" wording is recorded here
as a brief-text inconsistency, not followed.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_2dof import build_2dof_sim

TH90 = math.pi / 2


def test_biceps_length_coupled():
    sim, _ = build_2dof_sim()
    L_pro = sim.compute_muscle_state(TH90, 0.0, math.radians(80), 0.0)["biceps_long"][0]
    L_neu = sim.compute_muscle_state(TH90, 0.0, 0.0, 0.0)["biceps_long"][0]
    L_sup = sim.compute_muscle_state(TH90, 0.0, math.radians(-87), 0.0)["biceps_long"][0]
    assert L_pro > L_neu > L_sup, "supinator longest when pronated"
    assert L_neu == pytest.approx(sim.muscles["biceps_long"].Lopt_m, abs=1e-12)


def test_biceps_velocity_coupled():
    sim, _ = build_2dof_sim()
    v_e = sim.compute_muscle_state(TH90, 1.0, 0.0, 0.0)["biceps_long"][1]
    v_f = sim.compute_muscle_state(TH90, 0.0, 0.0, 1.0)["biceps_long"][1]
    v_both = sim.compute_muscle_state(TH90, 1.0, 0.0, 1.0)["biceps_long"][1]
    assert v_e > 0.0, "elbow flexion shortens biceps"
    assert v_f < 0.0, "pronation lengthens biceps (shortening-velocity decreases)"
    assert v_both == pytest.approx(v_e + v_f, abs=1e-15), "velocity is linear in both omegas"
