# FOREARM_ROTATION_IMPLEMENTATION_STATUS

## What was built (scaffold only — no numerical muscles)
- `mvp/biomech/forearm.py`: `RotationActuator` ABC (optional `elbow_theta` coupling
  channel), `ForearmRotationJoint` (+80°/−87° hard stops from P010/P011 upper ends;
  ±50° soft restraint from P018), `ForearmRotationDynamics` (1-DOF Euler hinge,
  gravity 0 under documented symmetric-mass assumption), `ForearmRotationSim`
  (deterministic fixed-step semi-implicit Euler + inelastic hard-stop projection).
- Inertia, damping, restraint stiffness are CONSTRUCTOR-REQUIRED (no defaults —
  UNKNOWN in corpus, nothing manufactured).
- `mvp/tests/test_forearm.py`: 10/10 pass (zero convention, ±rotation, limits,
  torque direction, units incl. degree-input rejection, determinism, dt
  sensitivity, zero activation, opposing-torque cancel, elbow compatibility).
- `coordinate_systems.md`: appended mapping subsection only (marked new; no
  evidence altered).
- Elbow subsystem: two unit-guard order hardenings (`simulation.py` validates
  before clamp so the degree guard is reachable) — valid-input behavior identical
  (scenario still 140.21°, 12/12 elbow+audit tests pass). No elbow numbers changed.

## Provisional / assumption items (rotation)
- Feasible ±50° restraint onset (P018 ASSUMPTION); gravity-0 assumption;
  asymmetric hard stops (+80/−87) as upper-end READY_WITH_UNCERTAINTY choice.
- NO provisional muscle numbers exist (none manufactured — searched, not found).

## Assumptions explicitly NOT made
No MA shape, no L(φ), no PT/supinator objects, no inertia/damping defaults,
no coupling coefficients, no technique/contact/hand content.

## Tests: 22/22 pass (12 prior + 10 forearm). No validation against human
arm-wrestling claimed (D-01 gap unchanged).

## Research blockers remaining
Fitted rotation MA coefficients (F6 workflow), rotation L(φ)/tendon/σ/vmax/θ_opt,
supinator + PQ architecture, rotational inertia/damping laws, passive curve shape,
coupling coefficients, sport rotation kinetics (D-01). Next step when data arrive:
Hill-based `RotationActuator` for PT anchored at P029/P040 (+ fitted 2-D MA),
then supinator/PQ once measured.
