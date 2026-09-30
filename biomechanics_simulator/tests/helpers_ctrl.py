"""Shared M7 builder: PD + Strategy wired to live sim tables (honest objects).

MA closures read per-call ma_args (live angles). TEST_FMAX variant overrides
wrist Fmax for ROUTING checks only (documented NOT physics).
"""
import os
import warnings

from controllers.base_controller import PDController
from controllers.strategy import StrategyController

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from helpers_4dof import build_4dof_sim

KP = {"elbow": 50.0, "forearm": 2.0, "wrist_fe": 1.0, "wrist_rud": 1.0}  # test-tuned engineering choices
KD = {"elbow": 5.0, "forearm": 0.2, "wrist_fe": 0.1, "wrist_rud": 0.1}
TEST_FMAX = 100.0  # TEST-ONLY routing probe (NOT physiological)


def pd_wiring(sim, test_fmax_wrist=False):
    muscles, ma = {}, {}
    for name, mus in sim.muscles.items():
        fmax = TEST_FMAX if (test_fmax_wrist and mus.Fmax_N == 0.0 and
                             name.startswith(("fcr", "fcu", "ecr", "ecu"))) else mus.Fmax_N
        muscles[name] = {"Fmax": fmax,
                         "roles": {"elbow": sim.roles.get(name, 0.0),
                                   "forearm": sim.f_roles.get(name, 0.0),
                                   "wrist_fe": sim.wfe_roles.get(name, 0.0),
                                   "wrist_rud": sim.wrud_roles.get(name, 0.0)}}
        entry = sim.mt[name]
        fns = {}
        if entry["elbow"] is not None:
            t = entry["elbow"]
            fns["elbow"] = lambda _t=t, **a: _t(a["theta"])
        if entry["forearm"] is not None:
            t = entry["forearm"]
            fns["forearm"] = lambda _t=t, **a: _t(a["theta"], a["theta_f"])
        if entry["wfe"] is not None:
            t = entry["wfe"]
            fns["wrist_fe"] = lambda _t=t, **a: _t()
        if entry["wrud"] is not None:
            t = entry["wrud"]
            fns["wrist_rud"] = lambda _t=t, **a: _t()
        ma[name] = fns
    return muscles, ma


def strategy_for(sim, technique, mode="OFFENSIVE", test_fmax_wrist=False):
    muscles, ma = pd_wiring(sim, test_fmax_wrist)
    pd = PDController(muscles, ma, dict(KP), dict(KD))
    return StrategyController(technique, pd, mode=mode)
