"""Deployment wiring (single-source reuse, NOT a fork).

Builders/PD/techniques are imported from tests/helpers_* (documented reuse:
duplicating them here would let physics and deployment drift). Controllers and
matches are assembled from the same objects the test suite verifies.
Run: uvicorn web.server:app  (from biomechanics_simulator/)
"""
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests"))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from helpers_match import build_match
from helpers_ctrl import pd_wiring, KP, KD
from controllers.strategy import StrategyController
from controllers.technique_controllers import TECHNIQUES
from web.fk import pose, VISUAL_FLAGS

warnings.simplefilter("ignore")

app = FastAPI(title="Arm-wrestling physics (validated engine, visual demo)")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__))), name="static")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


class AthleteSpec(BaseModel):
    mode: str = "dict"  # "dict" (explicit activations) or "technique"
    activations: dict = {}
    technique: str = "top_roll"
    grip: float = 1.0


class SimulateRequest(BaseModel):
    duration_s: float = 2.0
    athlete_A: AthleteSpec = AthleteSpec()
    athlete_B: AthleteSpec = AthleteSpec(activations={})
    downsample_hz: int = 60


def _wire_strategy(sim, technique):
    muscles, ma = pd_wiring(sim)
    from controllers.base_controller import PDController
    pd = PDController(muscles, ma, dict(KP), dict(KD))
    return StrategyController(technique, pd, mode="OFFENSIVE")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/techniques")
def techniques():
    return {n: {"targets_deg": t.targets_deg,
                "mapped": t.emphasis_mapped,
                "unmapped_no_object": t.unmapped} for n, t in TECHNIQUES.items()}


@app.get("/config")
def config():
    return {"dt": 0.001, "units": "SI",
            "visual_flags": VISUAL_FLAGS,
            "provisional_physics": ["inertia_ff (UNKNOWN)", "grip lever 0.08",
                                    "grasp kt/ct/mu (UNKNOWN pair)"],
            "note": "1 kHz validated config. Demo matches use test-scale inertias; "
                    "outcomes are illustrative, never validation."}


@app.post("/simulate")
def simulate(req: SimulateRequest):
    if not (0 < req.duration_s <= 10):
        raise HTTPException(400, "duration_s must be in (0, 10]")
    m = build_match()
    sched = {}
    for tag, spec in (("A", req.athlete_A), ("B", req.athlete_B)):
        sim = getattr(m, tag)
        if spec.mode == "technique":
            if spec.technique not in TECHNIQUES:
                raise HTTPException(400, f"unknown technique {spec.technique}")
            strat = _wire_strategy(sim, spec.technique)
            sched[tag] = lambda t, s=strat, msim=sim: s.compute_activations(
                {"joints": {"elbow": (msim.seg.theta, msim.seg.omega),
                            "forearm": (msim.phi, msim.omega_f),
                            "wrist_fe": (msim.phi_wfe, msim.omega_wfe),
                            "wrist_rud": (msim.phi_rud, msim.omega_rud)},
                 "ma_args": {"theta": msim.seg.theta, "theta_f": msim.phi}}, 0.001)
        elif spec.mode == "dict":
            acts = dict(spec.activations)
            sched[tag] = lambda t, a=acts: dict(a)
        else:
            raise HTTPException(400, "mode must be 'dict' or 'technique'")
    hist = m.run_match(req.duration_s, sched["A"], sched["B"],
                       req.athlete_A.grip, req.athlete_B.grip)
    step = max(1, int(round((1.0 / req.downsample_hz) / 0.001)))
    frames, contact, slipped = [], [], []
    for s in hist[::step]:
        fa = pose(s["A"]["theta"], s["A"]["phi"], s["A"]["phi_wfe"], s["A"]["phi_rud"], +1)
        fb = pose(s["B"]["theta"], s["B"]["phi"], s["B"]["phi_wfe"], s["B"]["phi_rud"], -1)
        frames.append({"t": s["t"], "A": fa, "B": fb,
                       "joints_A": {"theta": s["A"]["theta"], "phi": s["A"]["phi"],
                                    "wfe": s["A"]["phi_wfe"], "rud": s["A"]["phi_rud"]},
                       "joints_B": {"theta": s["B"]["theta"], "phi": s["B"]["phi"],
                                    "wfe": s["B"]["phi_wfe"], "rud": s["B"]["phi_rud"]},
                       "forces_A": {k: s["A"]["forces"][k] for k in
                                    ("biceps_long", "triceps_long", "pronator_teres")},
                       "forces_B": {k: s["B"]["forces"][k] for k in
                                    ("biceps_long", "triceps_long", "pronator_teres")}})
        contact.append(s["contact"]["Ft_on_A"])
        slipped.append(s["contact"]["slipped"])
    last = hist[-1]
    return {"meta": {"dt": 0.001, "steps": len(hist), "downsample_hz": req.downsample_hz,
                     "note": "illustrative demo output, not validation"},
            "t": [f["t"] for f in frames], "frames": frames,
            "contact_Ft": contact, "slipped": slipped,
            "pin": last["pin"], "winner": last["pin"],
            "x_A": [s["x_A"] for s in hist[::step]], "x_B": [s["x_B"] for s in hist[::step]]}
