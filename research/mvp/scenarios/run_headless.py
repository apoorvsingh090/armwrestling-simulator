"""Headless MVP scenario (req. 13): fixed initial angle, prescribed
biceps/triceps excitation, fixed-step simulate, write CSV with:
time, elbow_angle, angular_velocity, angular_acceleration,
biceps_activation, triceps_activation, biceps_force, triceps_force,
biceps_moment_arm, triceps_moment_arm, net_torque.
SI units (s, rad, rad/s, rad/s^2, N, m, Nm). No graphics here.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from biomech.simulation import ElbowSimulation, SimConfig

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "mvp_trace.csv")


def main():
    cfg = SimConfig(dt=0.001, duration_s=3.0,
                    theta0_rad=80.0 * 3.141592653589793 / 180.0,
                    omega0=0.0, u_biceps=0.8, u_triceps=0.2,
                    gravity_on=True)
    trace = ElbowSimulation(cfg).run()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "elbow_angle", "angular_velocity",
                    "angular_acceleration", "biceps_activation",
                    "triceps_activation", "biceps_force", "triceps_force",
                    "biceps_moment_arm", "triceps_moment_arm", "net_torque"])
        for i in range(len(trace.t)):
            w.writerow([trace.t[i], trace.theta[i], trace.omega[i],
                        trace.alpha[i], trace.a_bic[i], trace.a_tri[i],
                        trace.f_bic[i], trace.f_tri[i],
                        trace.ma_bic[i], trace.ma_tri[i],
                        trace.tau_net[i]])
    print(f"Wrote {OUT} ({len(trace.t)} rows)")
    print(f"final angle: {trace.theta[-1]*180/3.141592653589793:.2f} deg, "
          f"final omega: {trace.omega[-1]:.3f} rad/s")


if __name__ == "__main__":
    main()
