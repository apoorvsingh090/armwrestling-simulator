"""test_web_api: wire-protocol schema + technique resolution."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from web.server import app

client = TestClient(app)


def test_health_and_techniques():
    assert client.get("/health").json() == {"ok": True}
    techs = client.get("/techniques").json()
    assert set(techs) == {"top_roll", "hook", "press", "defensive"}
    assert "brachialis" in techs["hook"]["unmapped_no_object"]


def test_simulate_schema():
    r = client.post("/simulate", json={
        "duration_s": 0.5,
        "athlete_A": {"mode": "dict", "activations": {"pronator_teres": 0.5}, "grip": 1.0},
        "athlete_B": {"mode": "dict", "activations": {}, "grip": 1.0}})
    assert r.status_code == 200
    d = r.json()
    assert set(d) >= {"meta", "t", "frames", "contact_Ft", "slipped", "pin", "winner"}
    assert len(d["frames"]) == len(d["t"]) > 5
    f0 = d["frames"][0]
    for s in ("A", "B"):
        assert set(f0[s]) >= {"shoulder", "elbow", "wrist", "grip", "palm", "flags"}
        assert len(f0[s]["grip"]) == 3
        assert set(f0["joints_" + s]) == {"theta", "phi", "wfe", "rud"}
    assert set(f0["forces_A"]) == {"biceps_long", "triceps_long", "pronator_teres"}
    assert d["meta"]["dt"] == 0.001


def test_simulate_technique_and_errors():
    r = client.post("/simulate", json={
        "duration_s": 0.5,
        "athlete_A": {"mode": "technique", "technique": "press", "grip": 1.0},
        "athlete_B": {"mode": "technique", "technique": "defensive", "grip": 1.0}})
    assert r.status_code == 200 and len(r.json()["frames"]) > 5
    r2 = client.post("/simulate", json={
        "duration_s": 0.5,
        "athlete_A": {"mode": "technique", "technique": "flying_mare", "grip": 1.0},
        "athlete_B": {"mode": "dict", "activations": {}, "grip": 1.0}})
    assert r2.status_code == 400
    r3 = client.post("/simulate", json={
        "duration_s": 60.0,
        "athlete_A": {"mode": "dict", "activations": {}, "grip": 1.0},
        "athlete_B": {"mode": "dict", "activations": {}, "grip": 1.0}})
    assert r3.status_code == 400
