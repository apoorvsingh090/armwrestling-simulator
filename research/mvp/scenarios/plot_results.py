"""Plot MVP trace CSV (req. 14): angle vs time, omega vs time,
muscle force vs time, torque vs time. Saves PNGs to outputs/.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(__file__), "..", "outputs")
CSV = os.path.join(BASE, "mvp_trace.csv")


def load():
    cols = {}
    with open(CSV) as f:
        r = csv.DictReader(f)
        for k in r.fieldnames:
            cols[k] = []
        for row in r:
            for k in cols:
                cols[k].append(float(row[k]))
    return cols


def plot(x, ys, labels, title, ylabel, fname):
    plt.figure()
    for y, lab in zip(ys, labels):
        plt.plot(x, y, label=lab)
    plt.xlabel("time (s)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(BASE, fname), dpi=150)
    plt.close()
    print(f"Wrote {fname}")


def main():
    d = load()
    t = d["time"]
    rad2deg = 57.29577951308232
    plot(t, [[v * rad2deg for v in d["elbow_angle"]]], ["elbow angle"],
         "Elbow angle vs time", "deg", "angle_vs_time.png")
    plot(t, [d["angular_velocity"]], ["omega"],
         "Angular velocity vs time", "rad/s", "omega_vs_time.png")
    plot(t, [d["biceps_force"], d["triceps_force"]],
         ["biceps", "triceps"], "Muscle force vs time", "N", "force_vs_time.png")
    plot(t, [d["net_torque"]], ["net torque"],
         "Net elbow torque vs time", "Nm", "torque_vs_time.png")


if __name__ == "__main__":
    main()
