"""Milestone 1 wiring: Biceps + Triceps -> MA -> torque -> segment -> integrate.

Geometry note: gravity uses the spec form tau_grav = m*g*d_com*cos(theta),
i.e. zero gravity torque at 90° (upper-arm-forward reference posture).
External loads are modeled perpendicular to the forearm:
tau_ext = -F_ext * d_wrist (extension direction). Both documented; at the 90°
equilibrium test gravity and passive tissue torques vanish by construction.
"""
import json
import math
import os

from core.integrator import SemiImplicitEuler
from core.rigid_body import Segment
from core.joint import HingeJoint
from core.simulation import Simulation
from actuators.hill_muscle import HillMuscle
from actuators.moment_arm import load_elbow_tables

G = 9.80665
BASE = os.path.dirname(os.path.abspath(__file__))
THETA_OPT = math.pi / 2  # PROVISIONAL (PROV-04): angle of Lopt, warned below
import warnings as _w
_w.warn("[main] THETA_OPT=90deg is PROVISIONAL (no corpus value)", UserWarning, stacklevel=2)


def build_system():
    with open(os.path.join(BASE, "data", "r2_mtus.json"), encoding="utf-8") as f:
        mtus = json.load(f)
    ma = load_elbow_tables(os.path.join(BASE, "data", "r2_mtus.json"))
    bic = HillMuscle("biceps_long", Fmax_N=mtus["biceps_long"]["Fmax_N"]["value"],
                     Lopt_m=mtus["biceps_long"]["Lopt_m"]["value"],
                     pennation_deg=mtus["biceps_long"]["pennation_deg"]["value"],
                     slack_m=mtus["biceps_long"]["slack_m"]["value"])
    tri = HillMuscle("triceps_long", Fmax_N=mtus["triceps_long"]["Fmax_N"]["value"],
                     Lopt_m=mtus["triceps_long"]["Lopt_m"]["value"],
                     pennation_deg=mtus["triceps_long"]["pennation_deg"]["value"],
                     slack_m=mtus["triceps_long"]["slack_m"]["value"])
    seg = Segment("forearm", mass_kg=1.5, com_m=0.18, inertia_kgm2=0.06,
                  theta0_rad=math.pi / 2, wrist_m=0.30)
    joint = HingeJoint()
    integrator = SemiImplicitEuler(dt=0.001)
    return {"muscles": (bic, tri), "ma": ma, "seg": seg, "joint": joint,
            "integrator": integrator}


def build_simulation(theta0_deg=80.0):
    sys = build_system()
    sys["seg"].theta = math.radians(theta0_deg)
    sys["seg"].omega = 0.0
    bic, tri = sys["muscles"]
    return Simulation(sys["seg"], sys["joint"],
                      {"biceps_long": bic, "triceps_long": tri},
                      {"biceps_long": sys["ma"]["biceps"],
                       "triceps_long": sys["ma"]["triceps"]},
                      sys["integrator"])


def torques(sys, theta, omega, a_bic, a_tri, f_ext=0.0):
    """LEGACY Milestone-1 1-DOF reference kept for the equilibrium_demo only.

    The physics of record is Simulation.compute_torques (2-DOF, coupled
    wrist/forearm); this function duplicates the minimal 1-DOF stack for
    print-out comparison and must not be used for new work.
    """
    bic, tri = sys["muscles"]
    ma = sys["ma"]
    seg, joint = sys["seg"], sys["joint"]
    r_b, r_t = ma["biceps"](theta), ma["triceps"](theta)
    v_b = r_b * omega
    v_t = -r_t * omega
    L_b = ma["biceps"].fiber_length(theta, bic.Lopt_m, THETA_OPT, role=+1.0)
    L_t = ma["triceps"].fiber_length(theta, tri.Lopt_m, THETA_OPT, role=-1.0)
    F_b = bic.force(a_bic, L_b, v_b)
    F_t = tri.force(a_tri, L_t, v_t)
    tau_m = r_b * F_b - r_t * F_t
    tau_g = seg.mass_kg * G * seg.com_m * math.cos(theta)
    tau_p = joint.restraint_torque(theta, omega)
    tau_e = -f_ext * seg.wrist_m
    return {"tau_muscle": tau_m, "tau_gravity": tau_g, "tau_passive": tau_p,
            "tau_external": tau_e,
            "net": tau_m + tau_g + tau_p + tau_e,
            "F_bic": F_b, "F_tri": F_t, "r_bic": r_b, "r_tri": r_t}


def equilibrium_demo():
    sys = build_system()
    th = math.pi / 2
    rep = torques(sys, th, 0.0, 0.5, 0.0, f_ext=50.0)
    print(f"theta=90deg a_bic=0.5 F_ext=50N @ wrist")
    for k in ("F_bic", "F_tri", "r_bic", "r_tri", "tau_muscle",
              "tau_gravity", "tau_passive", "tau_external", "net"):
        print(f"  {k} = {rep[k]:.6f}")
    return rep


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["static", "dynamic"], default="static")
    args = ap.parse_args()
    if args.mode == "static":
        equilibrium_demo()
    else:
        sim = build_simulation(theta0_deg=80.0)
        hist = sim.run(3.0, lambda t: {"biceps_long": 0.8 if t < 1.5 else 0.2,
                                       "triceps_long": 0.2})
        print("t(s) theta(deg) omega(tau_net) F_bic F_tri")
        for s in hist[::100]:
            print(f"{s['t']:.2f} {s['theta']*57.2958:7.2f} {s['omega']:7.3f} "
                  f"{s['net']:7.3f} {s['forces']['biceps_long']:7.1f} "
                  f"{s['forces']['triceps_long']:7.1f}")
