# VALIDATION REPORT — arm-wrestling simulator (physics engine)

Thresholds 20%/50% PROVISIONAL; MA/ROM rows are pipeline-fidelity (circular by construction, declared); force rows expose the R2 bundle-map conflict; torque data MISSING.

## 1. Internal consistency
- qp_balance: **PASS** — max torque residual 1.65e-12
- fatigue_equilibrium: **PASS** — rel err 1.62e-05
- passive_conservatism: **PASS** — max |dV/dth + tau| 2.12e-11
- newton_unit: **PASS** — exact antisymmetry
- dissipative_bound: **PASS** — max energy growth 0.00e+00

## 2. Moment arms
- biceps_peak: **PASS** (rel err 0.000) — E:P038 anchor; pipeline-fidelity (circular), not independent validation
- triceps_peak: **PASS** (rel err 0.000) — E:P041 anchor; circular (see above)
- brd_peak: **PASS** (rel err 0.000) — E:P039 anchor; circular

## 3. ROM
- elbow: **PASS** (rel err 0.000) — E:P006; circular (stops built from it)
- forearm: **PASS** (rel err 0.000) — E:P010/P011 upper ends; circular
- wrist_fe: **PASS** (rel err 0.000) — E:P013/P014; circular
- wrist_rud: **PASS** (rel err 0.000) — E:P015; circular

## 4. Forces
- biceps_long: **FAIL** (rel err 1.112) — FAIL exposes R2 bundle-map conflict (Seth vs PCSA x PROV-01)
- brachioradialis: **PASS** (rel err 0.000) — PASS is circular (derived the same way)
- pronator_teres: **PASS** (rel err 0.000) — PASS is circular (derived the same way)
- triceps_long: **FAIL** (rel err 2.069) — FAIL exposes R2 bundle-map conflict

## 5. Plausibility findings
- WARNING [pin_time] pin at 0.167s < 0.5s (test-rig fast)

## 6. Sensitivity / Monte Carlo
- sensitivity: see tests/test_sensitivity.py
- monte carlo: see tests/test_monte_carlo.py

## 7. Known limitations
- No sport-specific validation data (D-01 cap: Partially Validated at best).
- MA/ROM rows are circular (same anchors built the tables).
- Torque references missing; friction/fatigue rates provisional.
- OAT ignores interactions; MC at MVP scale (see test files).
