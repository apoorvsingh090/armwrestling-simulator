"""Shared Milestone-3 builder: 10-muscle 4-DOF wrist-capable simulation.

JSON-honest objects use registry Fmax (wrist muscles inert at 0.0).
Direction/routing tests use TEST_FMAX (explicit, documented NOT physics —
same precedent as TEST-ONLY inertia values): it exercises sign/routing logic
only; magnitudes are never reported as biomechanics.
"""
import json
import math
import os
import warnings

from core.integrator import SemiImplicitEuler
from core.rigid_body import Segment, HandSegment
from core.joint import HingeJoint, wrist_hinge
from core.simulation import Simulation
from actuators.hill_muscle import HillMuscle
from actuators.moment_arm import MomentArmTable, BilinearTable, ConstantMA, load_mtu_set, load_wrist_passive, wrist_tables_from_registry

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(BASE, "data", "r2_mtus.json")
R3P = os.path.join(BASE, "data", "r3_wrist_passive.json")

TEST_FMAX = 100.0  # TEST-ONLY routing probe (NOT a physiological value)
TEST_I_W = 0.002   # TEST-ONLY wrist inertia (UNKNOWN in corpus)
TEST_I_FF = 0.005  # TEST-ONLY forearm inertia (UNKNOWN in corpus)

WRIST_NAMES = ("fcr_flexor_carpi_radialis", "fcu_flexor_carpi_ulnaris",
               "ecr_extensor_carpi_radialis", "ecu_extensor_carpi_ulnaris")


def build_4dof_sim(theta0_deg=90.0, g=9.81, test_fmax=False,
                   elbow_k=15.0, elbow_c=1.0, fore_k=5.0, fore_c=0.5,
                   inertia_ff=TEST_I_FF, inertia_w=TEST_I_W,
                   with_hand=True, f_ext_levers=True, sim_kwargs=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reg = load_mtu_set(DATA)
        data = json.load(open(DATA, encoding="utf-8"))
        wreg = wrist_tables_from_registry(DATA)
        wp = load_wrist_passive(R3P)
        muscles, elbow_ma, mtu_tables = {}, {}, {}
        for name in ("biceps_long", "triceps_long", "pronator_teres",
                     "pronator_quadratus", "supinator", "brachioradialis") + WRIST_NAMES:
            e = data[name]
            fmax = TEST_FMAX if (test_fmax and name in WRIST_NAMES) else e["Fmax_N"]["value"]
            kw = {"name": name, "Fmax_N": fmax, "Lopt_m": e["Lopt_m"]["value"],
                  "pennation_deg": e["pennation_deg"]["value"]}
            if "slack_m" in e:
                kw["slack_m"] = e["slack_m"]["value"]
            muscles[name] = HillMuscle(**kw)
            et = reg[name]["elbow_table"]
            if et is not None:
                elbow_ma[name] = et
            wfe = wreg[name]["wfe"] if name in wreg else None
            wrud = wreg[name]["wrud"] if name in wreg else None
            mtu_tables[name] = {"elbow": et, "forearm": reg[name]["forearm_table"],
                                "wfe": wfe, "wrud": wrud}
        roles = {n: reg[n]["roles"][0] for n in muscles}
        f_roles = {n: reg[n]["roles"][1] for n in muscles}
        wfe_roles = {n: (data[n]["roles"].get("wrist_fe", 0) if "roles" in data[n] and "wrist_fe" in data[n]["roles"] else 0)
                     for n in muscles}
        wrud_roles = {n: (data[n]["roles"].get("wrist_rud", 0) if "roles" in data[n] and "wrist_rud" in data[n]["roles"] else 0)
                      for n in muscles}
        seg = Segment("forearm", mass_kg=1.5, com_m=0.18, inertia_kgm2=0.06,
                      theta0_rad=math.radians(theta0_deg), wrist_m=0.30)
        ej = HingeJoint(restraint_k=elbow_k, restraint_c=elbow_c)
        fj = HingeJoint(anat_min_deg=-87.0, anat_max_deg=80.0,
                        feas_min_deg=-50.0, feas_max_deg=50.0,
                        restraint_k=fore_k, restraint_c=fore_c)
        wfej = wrist_hinge("fe", restraint_k=0.0, restraint_c=0.0)
        wrudj = wrist_hinge("rud", restraint_k=0.0, restraint_c=0.0)
        hand = HandSegment(0.4, 0.05, 0.001, 0.08) if with_hand else None
        sim = Simulation(seg, ej, muscles, elbow_ma, SemiImplicitEuler(dt=0.001),
                         roles=roles, gravity_m_s2=g, f_roles=f_roles,
                         mtu_tables=mtu_tables, forearm_joint=fj,
                         inertia_ff=inertia_ff,
                         wrist_fe_joint=wfej, wrist_rud_joint=wrudj,
                         wfe_roles=wfe_roles, wrud_roles=wrud_roles,
                         inertia_wfe=inertia_w, inertia_wrud=inertia_w,
                         wrist_passive_fe=wp["fe"], wrist_passive_rud=wp["rud"],
                         hand=hand, **(sim_kwargs or {}))
    return sim, {"passive": wp}
