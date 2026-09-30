"""Shared Milestone-2 builder: full 6-muscle 2-DOF elbow-forearm simulation.

All values from data/r2_mtus.json (tags preserved). inertia_ff / restraint
constants are TEST-ONLY (UNKNOWN in corpus — documented at each call site).
"""
import json
import math
import os
import warnings

from core.integrator import SemiImplicitEuler
from core.rigid_body import Segment
from core.joint import HingeJoint
from core.simulation import Simulation
from actuators.hill_muscle import HillMuscle
from actuators.moment_arm import MomentArmTable, load_mtu_set

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(BASE, "data", "r2_mtus.json")


def build_2dof_sim(theta0_deg=90.0, phi0_deg=0.0, g=9.81,
                   elbow_k=15.0, elbow_c=1.0, fore_k=5.0, fore_c=0.5,
                   inertia_ff=0.005, inertia_ef=0.0):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reg = load_mtu_set(DATA)
        data = json.load(open(DATA, encoding="utf-8"))
        muscles = {}
        for name in ("biceps_long", "triceps_long", "pronator_teres",
                     "pronator_quadratus", "supinator", "brachioradialis"):
            e = data[name]
            kw = {"name": name, "Fmax_N": e["Fmax_N"]["value"],
                  "Lopt_m": e["Lopt_m"]["value"],
                  "pennation_deg": e["pennation_deg"]["value"]}
            if "slack_m" in e:
                kw["slack_m"] = e["slack_m"]["value"]
            muscles[name] = HillMuscle(**kw)
        elbow_ma = {n: reg[n]["elbow_table"] for n in muscles if reg[n]["elbow_table"] is not None}
        mtu_tables = {n: {"elbow": reg[n]["elbow_table"], "forearm": reg[n]["forearm_table"]}
                      for n in muscles}
        roles = {n: reg[n]["roles"][0] for n in muscles}
        f_roles = {n: reg[n]["roles"][1] for n in muscles}
        seg = Segment("forearm", mass_kg=1.5, com_m=0.18, inertia_kgm2=0.06,
                      theta0_rad=math.radians(theta0_deg), wrist_m=0.30)
        ej = HingeJoint(restraint_k=elbow_k, restraint_c=elbow_c)
        fj = HingeJoint(anat_min_deg=-87.0, anat_max_deg=80.0,
                        feas_min_deg=-50.0, feas_max_deg=50.0,
                        restraint_k=fore_k, restraint_c=fore_c)
        sim = Simulation(seg, ej, muscles, elbow_ma, SemiImplicitEuler(dt=0.001),
                         roles=roles, gravity_m_s2=g, f_roles=f_roles,
                         mtu_tables=mtu_tables, forearm_joint=fj,
                         inertia_ff=inertia_ff, inertia_ef=inertia_ef)
        sim.phi = math.radians(phi0_deg)
    return sim, reg
