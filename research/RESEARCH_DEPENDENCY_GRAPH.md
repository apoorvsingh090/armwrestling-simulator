# RESEARCH DEPENDENCY GRAPH — implementation order, not importance

Notation: `X --> Y` = X must be answered/built before Y can be numerical.
P-levels from `REMAINING_SYSTEM_RESEARCH_PLAN.md`. Current code nodes marked [BUILT].

## Layer 0 — done (do not revisit except via listed gates)

```
[BUILT] elbow 1-DOF Hill MVP ──┐
[BUILT] forearm scaffold ──────┤
E-01/E-02/E-03, E-08, E-10/E-11 ├─> all future muscle/joint work (forms fixed)
R1/R2 (trace flag, E-12 length) ┘         (ride along, not blockers)
```

## Layer P0 — architecture decisions (no measurements needed, block everything below)

```
ARCH-1 vector-q joint-state convention ──> B/C coupled wrist object
                                        ──> E 3-DOF GH kinematics interface
                                        ──> H 3D pose-carrying segments
ARCH-2 pose (position+orientation) per segment ──> H patch r-vectors, I table plane
ARCH-3 F6 MA-fit pipeline readiness (Holzbaur export + fitter) ──> A numerical rotation
```

## Layer P1 — first numerical muscles/joints

```
A: 2-D rotation MA coeffs ──> PT RotationActuator ──> coupled elbow+rotation sim
A: PT tendon/dynamics consts ┘
G: passive curves (elbow first) ──> restraint defaults ──> replaces PROV-09
F: per-muscle sigma/vmax (≥ elbow pair) ──> replaces PROV-01/02/03
B/C: wrist MA surface (≥1 muscle) + architecture ──> coupled 2-DOF wrist object
E: GH MA + cuff architecture minimum ──> GH torque interface
```

## Layer P2 — contact

```
H: Stribeck laws (D-02) ──┐
H: grip distribution+S(θ) ├─> hand-wrench model ──> single-handDOWN force input
D: finger-resolved minimum ┘         (needs B/C wrist pose + H laws)
I: table surface/pad props ──> table constraint ──┘
ARCH-2 poses ──────────────> both ──┘
```

## Layer P3 — validation

```
D-01 sport dataset (S1–S11) ──> P083-style sport residual gates
                            ──> MA ±2SD re-check on fitted functions
                            ──> EMG-pattern + MJ checks ──> Partially Validated cap lifted
```

## Layer P4 — refinement (no edges into P0–P3; consume validated baseline)

```
L fatigue rates ──> derate placeholder ON
K gains/k_noise/coordination ──> human-like controller
P distributions ──> Monte-Carlo individualisation
E/G rhythm + stability envelopes ──> feasible-ROM laws
J kinetic-chain split ──> second-arm/shoulder-drive apportioning
Q constitutive laws ──> injury gate RE-OPENS (closed until then)
D-14 MPC/learned control (post-validation only)
```

## Critical path (shortest route to a defensible two-DOF arm)

```
ARCH-1/ARCH-3 ──> A rotation MA + PT consts ──> PT actuator ──> coupled elbow/rotation
       ──> G elbow passive ──> F elbow sigma/vmax ──> P3 D-01 ──> first Partially Validated claim
```

## Explicit non-edges (common mistakes this graph forbids)

- Techniques F8 ──X─> torque values (descriptions never become numbers).
- Tier2/3 PCSA ──X─> defaults (ASSUMPTION chain, hypothetical configs only).
- OpenSim/Holzbaur params ──X─> sport validity (re-validation required per use).
- Running sim ──X─> biological validity (no edge from any code node to any claim node).
- Phone kinematics ──X─> validation data (P086 exclusion is permanent).
