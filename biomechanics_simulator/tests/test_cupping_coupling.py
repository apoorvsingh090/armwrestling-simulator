"""test_cupping_coupling: FCU (flexion + ulnar roles) drives the wrist toward
the cupping quadrant (flexion + ulnar deviation). Uses TEST-ONLY Fmax:
asserts MOTION DIRECTION (coupled action), never torque magnitudes.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers_4dof import build_4dof_sim


def test_cupping_coupling():
    sim, _ = build_4dof_sim(test_fmax=True)
    sim.phi_wfe = 0.0
    sim.phi_rud = 0.0
    for _ in range(10):
        sim.step({"fcu_flexor_carpi_ulnaris": 1.0})
    assert sim.phi_wfe > 0.0, "FCU must flex the wrist"
    assert sim.phi_rud < 0.0, "FCU must ulnar-deviate (cupping quadrant)"
