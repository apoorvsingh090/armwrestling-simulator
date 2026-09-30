"""Shared M5 builder: two 4-DOF athletes + grasp-coupled match.

Test-only grasp/dynamics numbers (kt/ct/mu/pin_x/I_ff) are documented at each
use; production values are all UNKNOWN (r3) and stay caller-supplied.
"""
import os
import warnings

from core.match import MatchSimulation
from core.contact_detection import load_table_planes

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from helpers_4dof import build_4dof_sim

R3 = os.path.join(os.path.dirname(__file__), "..", "data", "r3_hand_contact_spec.json")


def build_match(gA=1.0, gB=1.0, mu=0.5, kt=2000.0, ct=5.0, lever=0.08,
                pin_x=0.05, maxA=462.0, maxB=462.0, I_ff=0.002, theta0=90.0):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        A, _ = build_4dof_sim(theta0_deg=theta0, inertia_ff=I_ff)
        B, _ = build_4dof_sim(theta0_deg=theta0, inertia_ff=I_ff)
        m = MatchSimulation(A, B, load_table_planes(R3), friction_mu=mu,
                            tangential_k=kt, tangential_c=ct, lever_m=lever,
                            pin_x_m=pin_x, max_grip_A=maxA, max_grip_B=maxB)
    return m
