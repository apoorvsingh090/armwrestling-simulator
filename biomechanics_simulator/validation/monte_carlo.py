"""Monte Carlo uncertainty propagation (MVP scale).

Distributions load from the JSON uncertainty blocks (single source of truth);
tests may override. N is caller-chosen: tests use small N with a FIXED seed
(documented reproducibility); production needs N>=1000. Draws apply to BOTH
athletes identically (population-archetype variation, documented).
Timeouts (no pin) are a third outcome category: P_A + P_B + P_draw == 1.
"""
import json
import math
import os
import random

from validation.sensitivity import scale_table

BASE = os.path.join(os.path.dirname(__file__), "..", "data")


def load_distributions(r2_path=None, r3_path=None):
    r2 = json.load(open(r2_path or os.path.join(BASE, "r2_mtus.json"), encoding="utf-8"))
    r3 = json.load(open(r3_path or os.path.join(BASE, "r3_hand_contact_spec.json"), encoding="utf-8"))
    return {"fmax": r2["uncertainty"]["Fmax"], "ma": r2["uncertainty"]["moment_arm"],
            "fatigue": r2["uncertainty"]["fatigue_rates"],
            "friction": r3["uncertainty"]["friction_mu"]}


class MonteCarloRunner:
    MUSCLES = ("biceps_long", "triceps_long", "pronator_teres", "brachioradialis")
    MA_ENTRIES = (("biceps_long", "elbow"), ("pronator_teres", "forearm"))

    def __init__(self, match_factory, distributions=None, seed=0):
        self.factory = match_factory
        self.dist = distributions or load_distributions()
        self.rng = random.Random(seed)

    def _sample(self, match):
        d = self.dist
        dF = {n: self.rng.gauss(d["fmax"]["mean_mult"], d["fmax"]["std_frac"]) for n in self.MUSCLES}
        dMA = {k: self.rng.gauss(d["ma"]["mean_mult"], d["ma"]["std_frac"]) for k in self.MA_ENTRIES}
        mu = self.rng.uniform(d["friction"]["min"], d["friction"]["max"])
        kf = math.exp(self.rng.gauss(0.0, d["fatigue"]["sigma"]))
        kr = math.exp(self.rng.gauss(0.0, d["fatigue"]["sigma"]))
        applied = {"Fmax": dF, "MA": dMA, "mu": mu, "kf": kf, "kr": kr}
        for sim in (match.A, match.B):
            for n, f in dF.items():
                sim.muscles[n].Fmax_N *= f
            for (n, key), f in dMA.items():
                sim.mt[n][key] = scale_table(sim.mt[n][key], f)
            for n in sim.muscles:
                sim.muscles[n].kf *= kf
                sim.muscles[n].kr *= kr
        match.grasp.mu = mu
        match.grip_A.mu = mu
        match.grip_B.mu = mu
        return applied

    def run(self, n_samples, duration_s=2.0, acts_A=None, acts_B=None):
        acts_A = acts_A or {"pronator_teres": 1.0}
        acts_B = acts_B if acts_B is not None else {"pronator_teres": 0.8}
        outcomes = []
        for _ in range(n_samples):
            m = self.factory()
            applied = self._sample(m)
            hist = m.run_match(duration_s, lambda t: dict(acts_A), lambda t: dict(acts_B), 1.0, 1.0)
            pin_t = next((s["t"] for s in hist if s["pin"] is not None), None)
            outcomes.append({"pin": hist[-1]["pin"], "pin_time": pin_t,
                             "xB_end": hist[-1]["x_B"], "applied": applied})
        return outcomes

    @staticmethod
    def statistics(outcomes):
        n = len(outcomes)
        wins = [o["pin"] for o in outcomes]
        pA = wins.count("A") / n
        pB = wins.count("B") / n
        pD = 1.0 - pA - pB
        times = [o["pin_time"] for o in outcomes if o["pin_time"] is not None]
        if times:
            mean = sum(times) / len(times)
            var = sum((t - mean) ** 2 for t in times) / len(times)
            sd = math.sqrt(var)
            ci = 1.96 * sd / math.sqrt(len(times)) if len(times) > 1 else 0.0
        else:
            mean = sd = ci = None
        return {"n": n, "P_A": pA, "P_B": pB, "P_draw": pD,
                "pin_mean": mean, "pin_sd": sd, "pin_ci95": ci,
                "n_pinned": len(times)}
