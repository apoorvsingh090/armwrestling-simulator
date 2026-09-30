"""test_ai_opponent: valid outputs, delayed reaction, switching, emergence."""
import math
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from controllers.ai_opponent import AIOpponent
from helpers_ai import live_ma_resolver, muscle_roles, neutral_sensory, KP, KD, DOFS
from helpers_match import build_match

warnings.simplefilter("ignore")


def _ai(sim, **kw):
    from helpers_4dof import build_4dof_sim  # noqa (documents sim-sourced wiring)
    args = dict(muscles=muscle_roles(sim), ma_resolver=live_ma_resolver(sim),
                technique="top_roll", reaction_time=0.2, Kp=dict(KP), Kd=dict(KD))
    args.update(kw)
    return AIOpponent(**args)


def test_valid_outputs():
    from helpers_4dof import build_4dof_sim
    sim, _ = build_4dof_sim()
    ai = _ai(sim)
    acts = ai.compute_activations(neutral_sensory(), 0.01)
    assert set(acts) == set(sim.muscles)
    assert all(isinstance(a, float) and 0.0 <= a <= 1.0 for a in acts.values())


def test_delayed_switch_to_defensive():
    from helpers_4dof import build_4dof_sim
    sim, _ = build_4dof_sim()
    ai = _ai(sim)
    for _ in range(30):
        ai.compute_activations(neutral_sensory(), 0.01)
    assert ai.last_technique == "top_roll"
    losing = neutral_sensory(hand_velocity=-0.5)
    for _ in range(10):  # 0.1 s < reaction 0.2 s: still old news
        ai.compute_activations(losing, 0.01)
    assert ai.last_technique == "top_roll"
    for _ in range(80):  # 0.2 s delay + 0.5 s rule elapse
        ai.compute_activations(losing, 0.01)
    assert ai.last_technique == "defensive"


def test_no_cheat_imports_or_tokens():
    import inspect
    import controllers.ai_opponent as aio
    import controllers.recruitment as rec
    import controllers.sensory as sen
    import controllers.reaction as rea
    import controllers.transitions as tra
    for mod in (aio, rec, sen, rea, tra):
        src = inspect.getsource(mod)
        assert "core.simulation" not in src and "core.match" not in src, mod.__name__
        for tok in ("opponent_activation", "intended_technique", "opponent_fatigue"):
            assert tok not in src, (mod.__name__, tok)


def test_emergent_match_outcome():
    m = build_match()
    from helpers_4dof import build_4dof_sim  # noqa
    ai = _ai(m.A)
    m.controller_A = ai
    hist = m.run_match(2.0, lambda t: None, lambda t: {}, 1.0, 1.0)
    assert len(hist) > 50
    assert m.impulse_A != 0.0  # forces flowed through contact physics
    assert hist[-1]["ai_A"] is not None  # decisions recorded
