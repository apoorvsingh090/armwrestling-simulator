# FOREARM_ROTATION_SPEC — research extraction for pronation/supination

Source corpus: Research 1–7 in `C:\Users\Apoorv\Downloads\research\`
(8 files; "F4" = Rigorous Biomechanical Specification, "F6" = C1 Moment Arms,
"F7" = Hill-Type/Real-Time + Joint Specification, "F8" = Biomechanics of Victory,
"F5" = Validation Framework, others as cited). Parameter IDs → `parameters.json`.
Conflicts → `research_conflicts.md` (C-03/C-04/C-14/C-18). No values invented below;
every number carries a P-ID or is explicitly marked UNKNOWN/ASSUMPTION.

Status key: **S** = SUPPORTED BY RESEARCH · **M** = MODEL DERIVED ·
**A** = IMPLEMENTATION ASSUMPTION · **U** = UNKNOWN.

---

## 1. BONY STRUCTURE

- **S:** Forearm rotation is produced at the proximal and distal radioulnar joints
  (PRUJ + DRUJ) acting as a single functional unit: 1-DOF pivot — "longitudinal
  rotation of radius around ulna" (F4 joint table; F7 § Radioulnar Joint).
- **S:** Ulna is the stable reference (hinge partner at the elbow; ISB ulna frame,
  F4/F7). Radius rotates about a longitudinal axis; in the MVP the ulna is treated
  as fixed to the elbow subsystem and the radius/hand rotates (A — see §7).
- **S (qualitative, no numeric laws):** PRUJ stability via annular ligament; DRUJ
  stability via triangular fibrocartilage complex, TFCC (F7, citing upper-limb
  biomechanics sources). No force–length or laxity laws for these structures exist
  in the corpus → stability envelopes UNKNOWN (D-10).
- **S (context):** Elbow flexion axis itself is complex — carrying angle 11° male /
  14° female (P008), mean flexion-axis varus 3.1±1.9° (P009, dual fluoroscopy) —
  so a fixed, orthogonal rotation axis is an approximation (A; same hinge-approximation
  class as the elbow MVP).
- **S:** F4 origin/insertion/line-of-action table includes pronator teres (PT) and
  pronator quadratus (PQ) geometry entries (MASTER §8) — qualitative path existence,
  several PCSA cells "Not Available"; NO numeric rotation moment arms beyond P040.

## 2. DOF — pronation/supination

- **S:** One primary rotational DOF (F7; F4 joint table: pivot, 1 DOF).
- **S:** Zero = neutral forearm posture, defined ISB-style as elbow flexed 90° with
  thumb pointing toward the shoulder (F4 neutral-position row; F7 ISB exposition).
- **A (adopted, resolving C-14):** neutral-zero with **pronation positive,
  supination negative**, radians SI internally. Raw-source conventions
  ("0°=supination" F6 grids; "mid-prone 0°" Chen) must be transformed on import —
  same rule as the elbow MVP.
- **S (ACTIVE_ROM, general human, wrist-cuff device at 90° elbow flexion —
  the more reliable method per F4):** pronation mean 76°, range 76–80° (P010);
  supination mean 80°, range 80–87° (P011). Conflicts C-03/C-04 (method dependence).
- **S:** Passive exceeds active by 3–5° (P012, PASSIVE_ROM adder, ligament-laxity literature).
- **A:** Feasible placeholder ±50° (P018, ADL-derived; TASK_SPECIFIC_ROM placeholder).
- **U:** ARM_WRESTLING_MEASURED_ROM for rotation (C-18 — no in-competition goniometry).
- Adopted stops: anatomical hard stops at +80° pronation / −87° supination
  (upper ends of P010/P011 ranges, P012 noted as the passive margin);
  soft-restraint onset at feasible ±50° (P018). See §11 for readiness classes.

## 3. MUSCLES (only what the corpus gives — gaps preserved, not filled)

| Role | Muscle | PCSA | Lopt | Tendon | Moment arm | Force/activation | Status |
|---|---|---|---|---|---|---|---|
| Pronation | Pronator teres | 1.1 cm² (P029, cadaveric n=10) | 5.5 cm (P029) | none in corpus | peak 4.9 cm (P040) | EMG 37.56% MVC pattern only (P080) | S anchors; rest U |
| Pronation | Pronator quadratus | none | none | none | none | named active in defense (F8, descriptive) | U (named only) |
| Pronation | (wrist/finger flexors assist in techniques) | — | — | — | — | descriptive (F8) | not rotation actuators |
| Supination | Biceps brachii | (elbow IDs P026) | (elbow IDs P026) | none | QUALITATIVE only: supination MA exists (Murray), decreases as elbow extends (F6, F8) — NO numeric value | hook-EMG pattern (P080, flexion context) | role S; rotation numbers U |
| Supination | Supinator muscle | none | none | none | none | "key rotator" (F6, qualitative) | U (named only) |
| Variable | Brachioradialis | 1.2 cm² (P028, C-06 disputed) | 17.7 cm (P028) | none | flexion peak 7.7 cm (P039); action "varies with forearm orientation" (F6, no numbers) | EMG 29.93% (P080) | rotation contribution U |

- General activation constants P052–P055 are not forearm-muscle-specific; no
  forearm EMD beyond the general ~100 ms P085. Tendon slack/compliance for every
  rotation muscle is UNKNOWN (D-05; only P032/P033 exist, for other muscles).
- P030/P031 (PT athletic/arm-wrestler PCSA scaling) are the research files' own
  ASSUMPTIONS — carried as ASSUMPTION, never defaults, no elite multipliers.

## 4. MOMENT ARMS (do not manufacture a function)

Corpus provides for rotation:
- (a) ONE discrete anchor: PT peak pronation MA 4.9 cm (P040), explicitly
  "strongly elbow-coupled" — a 2-D quantity `ma(elbow, pronation)` sampled once.
- (b) Qualitative directional facts: biceps supination MA decreases with elbow
  extension; biceps flexion MA larger when supinated with peak at a more extended
  elbow (Murray et al. via F6/F8); ECU varies with pronation (F6, wrist context).
- (c) Method + requirement: tendon-excursion cadaveric method; F6 workflow
  (Holzbaur-export + AICc polynomial/Hermite fit, C1, validity 5–140° elbow /
  5–160° pronation grids, ±2 SD gate P084) — the pipeline is specified, the
  COEFFICIENTS are absent (E-12 absent #1, C-12).

There are NO angle-dependent rotation functions and NO fitted coefficients in
Research 1–7. Per the task constraint, NO sinusoidal (or any) shape is
manufactured here — unlike the elbow MVP's PROV-05, rotation gets an interface
only (§12). CV principle P049 (10–20%) will apply to future fitted coefficients.

## 5. MUSCLE GEOMETRY — UNKNOWN

No `L(phi)`, no `dL/dphi`, no fiber-velocity law for pronation/supination exists
in the corpus → all UNKNOWN. Consequence: the elbow length surrogate
(`L = Lopt + MA_peak·(θ_opt−θ)`, MVP_AUDIT_V2 R2) has NO rotation counterpart;
a rotation length law may only be introduced together with a fitted/measured MA
function via E-12 (`ma = ∂L/∂θ`), exactly as R2 requires for the elbow.

## 6. TORQUE — first principles, existing architecture preserved

`τ_muscle = ± MA(φ[, θ_elbow]) · F` (E-03), then `Στ = I·α + ω×(I·ω)` reduced to
the 1-DOF hinge `I·α = Στ` (E-02). Sign table (φ = pronation+, radians):

| Source | Sign | Condition |
|---|---|---|
| Pronator actuator (PT/PQ-class) | + (pronation) | F ≥ 0, MA ≥ 0 |
| Supinator actuator (biceps-supination/supinator-class) | − (supination) | F ≥ 0, MA ≥ 0 |
| Passive restraint | opposes violation (beyond feasible ±50°) | P012 margin noted |
| Joint damping | −c·ω | c caller-supplied (no corpus value) |
| Gravity about rotation axis | 0 in scaffold | longitudinal axis + symmetric-mass assumption (A); hand-offset gravity U/deferred |

Pipeline unchanged: Muscle → Force → Moment arm → Joint torque → Joint dynamics.
Rotation consumes/produces the same SI quantities (rad, m, N, Nm) as the elbow.

## 7. COORDINATE SYSTEM (minimal extension of coordinate_systems.md)

- Axis: forearm longitudinal axis = ulna +Y (proximal), per ISB ulna frame (F4);
  neutral posture: axes of the forearm intermediate frame aligned with ulna frame,
  origin at radius origin (F7 ISB exposition). IMPLEMENTATION CONVENTION (A):
  rotation scalar φ about +Y_ulna, φ=0 neutral, +φ = pronation (right-hand rule
  about +Y gives palm-rotation sense documented in code), SI radians internally,
  degrees only at I/O. Parent segment: ulna (elbow subsystem output);
  child: radius/hand (future hand subsystem input). DOFs: 1. A quaternion/JCS
  note identical to the elbow MVP applies (engine may use quaternions internally;
  φ is the anatomical joint coordinate). Appendix: a pointer subsection was added
  to `coordinate_systems.md` (§ Forearm rotation) — marked as new, no existing
  evidence altered.

## 8. COUPLING (elbow flexion ↔ pronation/supination)

Coupling is SUPPORTED qualitatively — independence must NOT be assumed:
- (i) Biceps flexion MA is larger when supinated; its peak sits at a more
  extended elbow position (Murray via F6/F8).
- (ii) Biceps supination MA decreases as the elbow extends (F6/F8).
- (iii) PT peak MA is "strongly elbow-coupled" (P040 notes).
- (iv) ECU MA varies with pronation (F6); F6 mandates `ma = f(θ_elbow, θ_pronation)`.
NO coupling coefficients exist → scaffold carries an optional `elbow_theta`
channel in the actuator interface (default None = uncoupled evaluation) so a
future 2-D MA can be consumed without changing joint/dynamics code. The elbow
MVP's MA functions do NOT yet take φ (documented limitation; symmetric with R2).

## 9. INDIVIDUALISATION

- Future only: CV 10–20% coefficient perturbation (P049) once fitted rotation
  MAs exist; population/sex ROM differences noted qualitatively (P008-style;
  no rotation-specific distributions in corpus).
- P030/P031 PT scaling chain is ASSUMPTION (double-extrapolated) — reference
  only, never defaults. No arm-wrestler multipliers introduced (same rule as MVP).

## 10. ARM-WRESTLING RELEVANCE (separated, no technique→torque conversion)

- Measured sport-specific: PT sEMG 37.56% MVC during hook/top-roll dynamics
  (P080) — recruitment PATTERN only, not torque; no sport rotation torques/angles.
- General biomechanics: cuff ROM norms (P010/P011), Murray MA-dependence (F6),
  100° functional rotation arc (F5-Tier4, ADL-derived).
- Expert observation: winner's shoulder internal rotation "translates into
  forearm pronation"; loser "forced into extreme supination" (F7/F8 narrative).
- Assumption: feasible ±50° (P018); ADL arcs as match placeholders (F7 conclusion).
- Technique descriptions (hook supination attack, top-roll pronation pressure,
  PQ/extensor counter) remain CONTROL/ACTIVATION strategies (F8 objectives) —
  NO torque bonuses, NO modifiers (hard rule, MASTER §16).

## 11. IMPLEMENTATION READINESS (per-parameter classes)

| Item | Class | Basis |
|---|---|---|
| Rotation kinematics: 1-DOF pivot, neutral zero, +pronation | READY | S (F4/F7 ISB) |
| Anatomical stops +80°/−87° (P010/P011 upper ends) | READY_WITH_UNCERTAINTY | S ranges, method-dependent (C-03/C-04); upper-end choice documented |
| Passive +3–5° margin (P012) | READY_WITH_UNCERTAINTY | S existence, no curve shape |
| Feasible ±50° restraint onset (P018) | ASSUMPTION (placeholder) | A, ADL-derived |
| E-03 torque form + 1-DOF Euler reduction | READY | FIRST-PRINCIPLES |
| PT PCSA/Lopt anchors (P029) | READY (as anchors) | S, small-n cadaveric |
| PT peak MA 4.9 cm (P040) | READY (as anchor) | S, single sample point of a 2-D function |
| Rotation MA functions / coefficients | NEEDS_RESEARCH | absent (E-12 #1, F6 workflow specified) |
| Rotation muscle geometry L(φ)/v(φ) | UNKNOWN | absent (§5) |
| Supinator / PQ architecture, all rotation tendon data | UNKNOWN | absent (D-05) |
| Per-muscle σ, v_max, θ_opt for rotation | UNKNOWN | absent (eq. absent #2) |
| Rotational inertia about longitudinal axis | UNKNOWN | absent — NO default manufactured |
| Rotation damping / passive curve shape | UNKNOWN | absent — NO defaults manufactured |
| Elbow↔rotation coupling coefficients | NEEDS_RESEARCH | direction S, numbers absent (§8) |
| Sport rotation torques/angles | UNKNOWN | D-01 gap |

## 12. DECISION — interface + kinematic scaffold ONLY

Evidence is INSUFFICIENT for numerical rotation muscles (one discrete MA anchor,
zero MA functions, zero rotation geometry, zero supinator/PQ numbers, zero
inertia/damping). Therefore, per the task constraint: NO PT/supinator muscle
objects, NO MA shape, NO length law, NO dynamics defaults are manufactured.
Built instead: `ForearmRotationJoint` (limits/clamp/restraint with
caller-supplied stiffness), `ForearmRotationDynamics` (caller-supplied inertia
and damping — constructor-required, no defaults), `RotationActuator` provider
interface (optional elbow channel for future 2-D coupling), and a deterministic
fixed-step rotation simulator. Muscle-capable providers can be added later
without touching joint/dynamics code. Elbow subsystem files are UNCHANGED
(verified: 12/12 elbow tests pass, scenario still 140.21°).
