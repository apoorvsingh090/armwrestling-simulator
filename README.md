# Arm-Wrestling Biomechanics Simulator

Deterministic, first-principles biomechanics engine for arm-wrestling simulation:
4-DOF musculoskeletal model (elbow, forearm rotation, wrist FE/RUD), Hill-type
muscles, contact mechanics, two-athlete matches, technique controllers, fatigue,
AI opponent, validation framework — plus a three.js web demo.

- `biomechanics_simulator/` — the engine (SI units, 1 kHz fixed step).
  Tests: `python -m pytest tests` (142 passing).
  Web demo: `uvicorn web.server:app`, then open http://127.0.0.1:8000.
- `research/` — evidence base: R1 skeletal kinematics, R2 muscle-tendon,
  R3 hand/contact specs, parameter database, audits, validation inputs.
  Every number is tagged EMPIRICAL / MODEL_DERIVED / PROVISIONAL / ASSUMPTION
  / UNKNOWN. No technique or strength multipliers exist anywhere.

Status: internally consistent and uncertainty-propagating; capped at
Partially Validated pending sport-specific (D-01) data. Demo outcomes are
illustrative, never validation.
