"""test_plausibility: synthetic histories hit every gate exactly once."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation.plausibility import PlausibilityChecker

DEG = math.pi / 180.0


def _side(th=90.0, ph=0.0, wfe=0.0, rud=0.0, forces=None):
    return {"theta": th * DEG, "phi": ph * DEG, "phi_wfe": wfe * DEG,
            "phi_rud": rud * DEG, "forces": forces or {}}


def _hist(n=12, pin_at=None, ft=10.0, th=90.0):
    return [{"t": i * 0.2, "pin": ("A" if pin_at is not None and i * 0.2 >= pin_at else None),
             "x_A": 0.01 * i, "x_B": 0.012 * i,
             "A": _side(th), "B": _side(th), "contact": {"Ft_on_A": ft}} for i in range(n)]


def test_plausible_passes():
    assert PlausibilityChecker().check_match(_hist()) == []


def test_fast_pin_warns():
    f = PlausibilityChecker().check_match(_hist(pin_at=0.05))
    assert any(x["check"] == "pin_time" and x["level"] == "WARNING" for x in f)


def test_force_warns():
    f = PlausibilityChecker().check_match(_hist(ft=6000.0))
    assert any(x["check"] == "contact_force" for x in f)


def test_rom_violation_fails():
    f = PlausibilityChecker().check_match(_hist(th=160.0))
    assert any(x["check"] == "joint_rom" and x["level"] == "FAIL" for x in f)


def test_activation_bounds():
    pc = PlausibilityChecker()
    assert pc.check_activations({"a": 0.5}) == []
    bad = pc.check_activations({"a": 1.2})
    assert bad and bad[0]["level"] == "FAIL"
