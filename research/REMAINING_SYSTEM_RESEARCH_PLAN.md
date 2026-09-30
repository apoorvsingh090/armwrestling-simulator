# REMAINING SYSTEM RESEARCH PLAN — what science is still required

Purpose (not realism): determine exactly what scientific information is required
to eventually build a first-principles arm-wrestling simulator. No numbers are
invented below; every value carries a P-ID or an explicit UNKNOWN/ASSUMPTION tag.
Evidence classes: EMPIRICAL / MODEL_DERIVED / FIRST_PRINCIPLES / PROVISIONAL /
ASSUMPTION / UNKNOWN. Corpus = Research 1–7; conflicts C-##; deferred D-##.

Current foundation (respected, not re-litigated): elbow 1-DOF Hill MVP (PROV-01…09,
22 tests pass with forearm scaffold) + forearm 1-DOF interface/kinematic scaffold
(no numerical muscles). Sport validation unavailable (D-01); provisionals are never
empirical; OpenSim/Holzbaur parameters are NOT auto-validated for arm wrestling;
a running simulation is NOT biological validation.

Per-subsystem key: each of A–Q answers the same 22 questions (numbered).
Q22 is a hard gate: what must NOT be built yet.

---

## A. FOREARM PRONATION/SUPINATION (scaffold exists — `mvp/biomech/forearm.py`)

1. DOFs: 1 (pivot, radius about ulna) — S (F4/F7). No further DOFs evidenced.
2. Structures: PRUJ + DRUJ functional unit; annular ligament; TFCC (all qualitative, F7).
3. Bones: radius (rotates) + ulna (reference); humerus as parent (S).
4. Joints: PRUJ + DRUJ; radiocapitellar context. Axis micro-motion ±5° coupled abd/add (F4, REFERENCE, deferred).
5. Muscles: pronators PT (numbers: §A6) + PQ (named only); supinators biceps (role S, rotation numbers U) + supinator muscle (named only); brachioradialis orientation-dependent (no rotation numbers).
6. Architecture: PT PCSA 1.1 cm² + Lopt 5.5 cm EMPIRICAL (P029, n=10 cadaveric). EVERYTHING else UNKNOWN: PQ/supinator PCSA+Lopt+pennation; PT pennation/slack/vmax/FL/FV; biceps supination-side parameters.
7. Moment arms: ONE discrete anchor — PT peak 4.9 cm EMPIRICAL (P040, "strongly elbow-coupled"). NO functions, NO coefficients (C-12, E-12 absent #1).
8. MA configuration dependence: SUPPORTED qualitatively (biceps flexion MA ↑ when supinated; supination MA ↓ with extension; F6 mandates 2-D fit) — coefficients UNKNOWN.
9. MTU length equations: UNKNOWN (no L(φ); E-12 coupling required once MAs fitted).
10. Passive torque: existence only (P012 +3–5° margin EMPIRICAL); NO curve shape (UNKNOWN).
11. Inertia about longitudinal axis: UNKNOWN (no default manufactured).
12. Damping: UNKNOWN (no default manufactured).
13. Limits: anatomical +80/−87 READY_WITH_UNCERTAINTY (P010/P011, C-03/C-04); feasible ±50 ASSUMPTION (P018); measured UNKNOWN (C-18).
14. Coordinates: DONE (spec §7 + coordinate_systems.md mapping; neutral-zero, +pronation, SI rad).
15. Coupling: elbow↔rotation MA coupling SUPPORTED (§8 of rotation spec); coefficients UNKNOWN; `elbow_theta` channel already in interface.
16. Contact/friction: n/a (no contact in this DOF).
17. Required experiments: tendon-excursion MA surfaces over (elbow × pronation) grids (F6 protocol); PT/PQ/supinator architecture (dissection + laser diffraction as in [92]); rotation passive torque–angle curves; rotational inertia (imaging + identification).
18. Sport-specific: rotation torques/angles/EMG in matches (D-01; only P080 pattern exists).
19. Supported now: kinematics, E-03 torque form, PT anchors, coupling directions.
20. UNKNOWN: §A6-remainder, §A7-functions, §A9–A12, sport kinetics.
21. Safe as interface/scaffold: DONE (RotationActuator ABC, joint, dynamics, sim — all wired to stubs in tests).
22. MUST NOT: PT/supinator muscle objects, any MA shape, L(φ), inertia/damping/restraint defaults, technique torque roles.

## B. WRIST FLEXION/EXTENSION

1. DOFs: 1 of an irreducible 2-DOF ellipsoid (P016 obliquity 26.6° couples FE↔RUD — two independent 1-DOF hinges would VIOLATE measured coupling).
2. Structures: radiocarpal joint; carpus (single rigid body = MODEL_DERIVED simplification, F4); TFCC loads UNKNOWN (D-06).
3. Bones: radius + carpus/metacarpals (lumped digits per F3 "safe simplification" ASSUMPTION).
4. Joints: radiocarpal; midcarpal lumped (no data).
5. Muscles: FCR, FCU, ECU, ECRL, ECRB, APL (+ finger flexors in techniques, descriptive F8).
6. Architecture: NO PCSA/Lopt/pennation/slack/vmax/FL/FV for any wrist muscle in corpus → ALL UNKNOWN. (Only functional MAs exist, §B7.)
7. Moment arms: functional means+SDs EMPIRICAL (P042 FCR 12.2±2.1 FE / −10.2±2.5 RUD; P043 FCU 11.3±2.1 / 11.7±4.2; P044 ECU −4.0±0.9 / 23.7±3.3; P045 ECRL −6.6±3.0 / −17.2±3.6; P046 ECRB −10.8±2.8 / −10.0±2.2; P047 APL 6.8±1.9 / −23.6±2.5 mm) with MRI-vs-functional gaps (S with stated gaps). NO continuous functions.
8. MA configuration dependence: ECU varies with pronation (F6, qualitative); full surface for ECU UNKNOWN (D-06/F6 limits); Chen protocol must be EXTENDED over pronation (D-06).
9. MTU length equations: UNKNOWN (same E-12 requirement).
10. Passive torque: UNKNOWN for wrist (no curves; obliquity implies coupled passive field, unmeasured).
11. Inertia (hand about wrist): UNKNOWN.
12. Damping: UNKNOWN.
13. Limits: anatomical 80 flex / 70 ext EMPIRICAL ACTIVE_ROM (P013/P014); feasible subset UNKNOWN-as-written (C-20 anomaly: F7 lists "40° extension, 40° pronation…" at the wrist — pronation at the wrist is anatomically anomalous; carry as flagged REFERENCE_ONLY, requires source check).
14. Coordinates: ISB wrist frame S (F4/F7); 26.6° obliquity S (implement axis-oblique or orthogonalized-with-logged-limitation, ASSUMPTION either way).
15. Coupling: wrist↔forearm (ECU/pronation; S direction, U magnitude); wrist FE↔RUD (P016, S angle); S(θ_wrist) grip scaling −30% magnitude EMPIRICAL with ASSUMED inverted-bell shape (P073).
16. Contact/friction: S(θ) + R_i feed hand contact (see H); S shape UNKNOWN.
17. Required experiments: wrist-simulator MA sweeps over (FE × RUD × pronation) extending Chen; passive torque–angle fields; hand inertia; C-20 source resolution.
18. Sport-specific: wrist flexion/supination attack kinematics + FCU/FCR EMG beyond P080 pattern (D-01); cupping/rising loads (D-06/D-10).
19. Supported: ROM, obliquity angle, functional MA anchors + SDs, grip-loss magnitude, ISB frames.
20. UNKNOWN: all wrist muscle architecture/tendon/dynamics constants, MA functions, passive fields, inertia/damping, feasible subset.
21. Safe now: 2-DOF coupled-kinematics interface (angle pair + obliquity constant P016) + actuator ABC mirroring RotationActuator; NO torques.
22. MUST NOT: wrist muscle objects, MA shapes, S(θ) shape commitment, rigid-hand load predictions, "cupping torque" quantities.

## C. WRIST RADIAL/ULNAR DEVIATION

1–5. Same joint/bones/muscles as B (second axis of the same ellipsoid; same muscle set, RUD columns of P042–P047).
6. Architecture: UNKNOWN (same gap as B; shared muscle objects eventually serve both axes).
7. Moment arms: RUD columns of P042–P047 (S anchors with SDs); no functions.
8. Dependence: P016 coupling both directions; ECU full pronation surface UNKNOWN.
9. MTU lengths: UNKNOWN (shared with B; one length law per muscle spans both axes).
10–12. Passive/inertia/damping: UNKNOWN (shared plant with B).
13. Limits: radial 20–25 / ulnar 30–35 EMPIRICAL (P015); feasible UNKNOWN (C-20).
14. Coordinates: same ISB frame; deviation zero = 3rd metacarpal aligned (S).
15. Coupling: inseparable from B (P016) + forearm (ECU) + grip S(θ).
16–18. As B (S(θ) magnitude P073; sport cupping/rising data missing).
19. Supported: RUD anchors + SDs, deviation ROM, obliquity.
20. UNKNOWN: functions, architecture, passive, dynamics constants.
21. Safe now: NOTHING separate — implement jointly with B as one 2-DOF interface (implementing C alone as a 1-DOF hinge would bake in a P016 violation).
22. MUST NOT: independent deviation hinge; deviation torque claims.

## D. HAND/PALM/FINGER MECHANICS

1. DOFs: MCP flexion + IP hinges per ISB definitions (S as DEFINITIONS only); mechanics unmeasured. Count TBD by articulation decision (deferred).
2. Structures: intrinsic-hand muscles (roles UNKNOWN, D-06); thenar share 40% (F3 expert/dynamometry CONTEXT, not a design value); finger-extensor antagonist role in EMG (F4, qualitative); TFCC loading UNKNOWN.
3. Bones: metacarpals + phalanges (geometry absent).
4. Joints: MCP/IP (definitions only); carpus rigid (MODEL_DERIVED simplification).
5. Muscles: FDS (in F4 table, several cells "Not Available"); intrinsics unlisted; NO architecture numbers → ALL UNKNOWN.
6. Architecture: UNKNOWN in full (PCSA/Lopt/pennation/slack/vmax/FL/FV).
7–9. MAs/lengths: UNKNOWN (no finger MA data; thumb force paths UNKNOWN D-06).
10. Passive: containment mechanics UNKNOWN (D-06).
11–12. Inertia/damping of digits: UNKNOWN.
13. Limits: no finger ROM data in corpus → UNKNOWN.
14. Coordinates: ISB MCP/IP definitions S; Y-along-metacarpal wrist frame exists (§7 hand).
15. Coupling: grip↔wrist posture S(θ) (magnitude S, shape A); finger pressure battle for top-roll (descriptive F8, NOT mechanics).
16. Contact: finger-resolved pressure REQUIRED for H (missing; D-03/D-06).
17. Required experiments: finger-resolved dynamometry; thumb kinematics; MCP/IP containment mechanics; TFCC load behavior.
18. Sport-specific: finger-pressure battle data, slip-out events with pressure maps (all missing).
19. Supported: rigid-hand + 3-patch lumped model as explicitly-labeled ASSUMPTION (F3); patch positions P068–P070 ASSUMPTION; R_i splits P072 ASSUMPTION; direction effect 42% (F3 context).
20. UNKNOWN: everything finger-level; S(θ) law; patch-resolved distribution.
21. Safe now: NOTHING beyond the existing labeled 3-patch placeholder (already the documented limit); articulated-hand interface only when D-06 data arrive.
22. MUST NOT: finger torques, thumb-cupping torques, slip/failure predictions, "crushing grip" force claims.

## E. SHOULDER/SCAPULAR MECHANICS

1. DOFs: GH 3-rotor ball-and-socket (S); clavicle SC/AC glides (locked/rhythm-prescribed ASSUMPTION); scapulothoracic functional articulation, NOT synovial (S, F4).
2. Structures: rotator cuff (dynamic stability 25–30% head contact, F7 qualitative — stability BOUNDARY unknown); pec/lat/subscap/teres as IR torque generators (F4/F8, framing complementary C-21).
3. Bones: humerus (P022 30.5±2.1 cm Indian cohort; P024 distal morphology Chinese CT; P025 head ⌀42.3 mm Indian n=50 — all population-specific, never universal), clavicle, scapula.
4. Joints: GH + AC + SC + scapulothoracic functional.
5. Muscles: PM/lat/subscap/teres/biceps/deltoid (F4 table; several cells unavailable); subscap Fmax 1306.9 N MODEL_DERIVED small-n fit (P033); lat pennation 25° incomplete (P034 REFERENCE_ONLY); deltoid PCSA 22±6 + penn 16±2 EMPIRICAL (P035).
6. Architecture: fragmentary (P033–P035 only); GH-muscle slack/vmax/FL/FV UNKNOWN.
7. MAs: subscap IR peak 27 mm (P048); rest UNKNOWN; NO functions.
8. Dependence: posture-conditioned ROM (C-05: F4 conditioned S, F7 generic REFERENCE_ONLY).
9. Lengths: UNKNOWN.
10. Passive: cuff-stability boundary UNKNOWN (D-10); shoulder passive torque–angle exists only as general-context method (F5), no arm-wrestling values.
11–12. Inertia/damping: humerus mass/inertia MODEL_DERIVED baseline (P019/P020, generic male, needs scaling P090 ≤20% error); GH damping UNKNOWN.
13. Limits: anatomical flex 0–170/ext 0–30/abd 0–170/ER 0–90/IR 0–80 ACTIVE_ROM conditioned (P001–P005); feasible arm-wrestling envelope UNKNOWN (D-10); start posture ~45° flexion = scenario CONTEXT (P088), not a constraint.
14. Coordinates: ISB GH frames S; humerus origin conflict C-13 (adopted head-center = IMPLEMENTATION CONVENTION); Euler-sequence sensitivity 50° (F4 [32] — sequence must be fixed/logged).
15. Coupling: scapulohumeral rhythm principle S, quantitative law UNKNOWN (D-10); shoulder-driven attacks excluded from MVP scope.
16. Contact: n/a (no contact at shoulder; table elbow-pad contact belongs to I).
17. Required experiments: GH/IR MA surfaces; cuff muscle architecture in task postures; scapular-rhythm law for the task; load-dependent stability envelopes; IR torque–angle under compression/torsion.
18. Sport-specific: shoulder-commitment/back-pressure kinetics + full-body chain (D-11; tennis 51–55% NOT transferable).
19. Supported: 7-DOF Holzbaur reference architecture (F2); GH ROM + frames; fragmentary architecture; scaling pipelines (manual + AddBiomechanics bilevel, F2).
20. UNKNOWN: stability envelopes, rhythm law, most MAs/architecture, feasible envelope, kinetic-chain split.
21. Safe now: 3-DOF GH kinematics interface (angles + conditioned limits + fixed sequence); locked-scapula ASSUMPTION carried; NO torques.
22. MUST NOT: shoulder torque drivers, "shoulder-commitment power" quantities, stability-limited ROM claims, back/side-pressure mechanics.

## F. MUSCLE-TENDON ARCHITECTURE (cross-cutting)

Required per-muscle set {PCSA, Lopt, pennation, slack, vmax, FL, FV}: corpus HAS
{PCSA+Lopt for biceps-long/brachioradialis/PT/triceps-long (P026–P029, n=10 cadaveric);
brachialis/subscap Fmax+Lopt+slack small-n fits (P032/P033); lat/deltoid fragments
(P034/P035)} and LACKS everything else (equations.md absent #2). Specific tension:
NO corpus value (PROV-01 flagged). FL form bell + FV hyperbolic S as FORMS (F1/F2/F4/F7);
rigid-tendon 2–54× speedup with ~20% Fmax MAE MODEL_DERIVED (P060, C-09 fork);
damping: only linear 2.5 Ns/m framework value (P059, NOT joint damping);
Huxley/extended-Hill offline branch with NON-HUMAN rabbit rates (F7, reference only).
411. Individualisation: CV 10–20% MA perturbation principle (P049, EMPIRICAL).
419. Supported: E-10/E-11 forms, Zajac E-08 + ranges, named gaps.
420. UNKNOWN: per-muscle σ/vmax/SEE/PEE/SDE/slack/pennation-dynamics (D-05).
421. Safe: reference/rigid branch scaffolding as built; new muscles enter ONLY as
    named-head equivalents with corpus anchors or as provider-interface stubs.
422. MUST NOT: specific-tension defaults presented as data; SEE/SDE curves; dynamic pennation; tendon-energy tactics (X-05/D-06).

## G. PASSIVE JOINT/CONNECTIVE-TISSUE MECHANICS

Required: passive torque–angle curves per DOF + ligament force–length laws +
zero-load lengths + cartilage behavior. Present: elbow restraint as-written P021
(MODEL_DERIVED, surrogate PROV-09 in use); forearm +3–5° adder (P012, margin only);
ligament tensile strengths as CONTEXT (elbow anterior band 261±71 N; radial
collateral 233±116 N — strengths, NOT laws); shoulder passive-curve METHOD only
(F5 general context). Forms FIRST-PRINCIPLES (elastic/damping), parameters
UNKNOWN (D-07/D-10). Safe: restraint-function scaffolding with caller-supplied
constants (elbow + forearm pattern). MUST NOT: ligament/cartilage failure rules,
injury thresholds, dislocation modeling, "stability-limited" ROM numbers.

## H. HAND-TO-HAND CONTACT

Required: 3-patch (or finer) normal+friction wrenches summed by E-04 (form
FIRST-PRINCIPLES + ASSUMED geometry); Stribeck pair law E-05 (form EMPIRICAL,
parameters UNKNOWN); grip map E-06 (Fmax EMPIRICAL task-adjacent P071 442/215 N;
S shape + R_i 0.4/0.53/0.07 ASSUMPTION; −30% magnitude EMPIRICAL P073).
Moment arms r-vectors posture-dependent (SUPPORTED principle; patch values
P068–P070 ASSUMPTION). Friction: dry skin-skin μs 0.5–0.7 reviews vs 0.25 palmar
study vs catalog 0.6/0.5 ASSUMED (C-07 — target interfaces UNKNOWN); vs assumed
0.022 m/s finger-glass proxy, CRITICAL GAP (C-08/P067 ε ASSUMPTION). Omitted
phenomena named: LuGre/Dahl hysteresis, stick-slip (F3 limits). Solver paradigm:
MuJoCo compliant contact <1 ms QP precedent (F3, paradigm evidence, NOT a
friction measurement); solref/solimp + torsional/rolling 0.01–0.02 mapping (F3 §4,
MODEL_DERIVED config). Required experiments: tribometer Stribeck curves at match
loads/moisture (D-02); instrumented grip/posture dynamometry + HM/ABC calibration
(D-03); patch-resolved pressure (D-06). Sport data: ALL missing (slip events,
pressure maps, hand forces). Safe now: NOTHING numerical — E-05/E-04/E-06 forms
documented; placeholders (P061–P067 bands) exist in DB as flagged ASSUMPTION/U,
never wired to dynamics. MUST NOT: slip/grip/match-outcome claims; single-μ GUI
values as measurements; technique-dependent friction.

## I. TABLE CONTACT/CONSTRAINTS

Required: flat hard horizontal plane ASSUMPTION (F3); table material slots
(K/D, friction triple per F3 §4 mapping — MODEL_DERIVED config, values absent);
skin-table proxies glass/steel/fabric (flagged proxies: dry 0.25–0.5, wet 0.7–1.4
ASSUMED, C-07). Elbow-pad contact: NO force data. Required experiments: actual
competition surface properties; pad/edge geometry effects; chalk/sweat dynamics
(D-02); table reaction forces in matches (D-01 counterpart). Safe: plane-geometry
interface + per-session material parameter slots (values UNKNOWN). MUST NOT:
table-friction defaults as data; pad-force predictions; "posting" force mechanics.

## J. OPPONENT/DUAL-ARM SYSTEM

Required: second competitor beyond patch-wrench I/O is EXCLUDED by scope
(D-06/D-11, MASTER §21, X-05). Supported: single-hand force input driving
placeholders (U-03); FSM ramp→hold→release scenario scripts as TEST PATTERNS
(not claims). Required: opponent interaction forces + full-body kinetics (D-01/D-11).
Safe: patch-wrench input port (forces in, no opponent model). MUST NOT: opponent
AI/policy, MPC/RL (X-05, D-14; RL excluded phase 1), second-arm dynamics,
"opponent difficulty" parameters.

## K. NEUROMUSCULAR CONTROL

Required: FSM phase logic S (F1 states Preparation/Ramp-Up/Steady-Hold/Release;
F2 technique-phase format; F8 Setup/Loading/Attack/Hold/Transition/Counter);
E-07 inverse-dynamics + Σu² + null-space co-contraction MODEL-DERIVED method;
SDN noise form E-09 with k_noise UNKNOWN; delays P056 25 ms lumped
(+P057/P058 framework ASSUMPTIONS); PD/feedforward execution (F2); no-RL phase 1
(F1/F2); optimal control as OFFLINE tool. Missing: gains, recruitment order,
coordination patterns, k_noise fits, 4CCr arm-muscle rates (D-08); hardware +9.6 Hz
bypass figure REFERENCE_ONLY (C-10 branch logged). Controller layering C-11 is
terminology (mapped, no physics conflict). Safe: FSM scaffolding (hold/ramp/release
minimum) + delay/noise TOGGLES for validation; prescribed excitations (as MVP).
MUST NOT: human-like coordination claims, learned policies, "technique controllers"
with torque authority, bilaterally-coupled opponent control.

## L. FATIGUE

Required: 4CCr central/peripheral separation S as CONCEPT (qualitative
task-weighting isometric→central / concentric→peripheral; recovery asymmetry
minutes-vs-hours, F1) + Fmax-derate SLOT in extended Hill (F7). ALL rate/recovery
constants for arm muscles UNKNOWN (D-09); NO fatigue in MVP default (MASTER §15).
Required experiments: sustained-MVC + intermittent-duty protocols on elbow/wrist/
pronation muscles with central/peripheral separation. Safe: optional derate
placeholder ONLY for long-bout demos, labeled ASSUMPTION (currently OFF).
MUST NOT: fatigue-driven outcomes, recovery predictions, "endurance" athlete
parameters.

## M. ARM-WRESTLING-SPECIFIC KINEMATICS (see dedicated section below)

Required: competitive joint angles + angular velocities (+ scapular/hand
articulation) across techniques/phases. Present: NONE measured (D-01; P086
excludes phones as kinematics source — 12–30° errors vs <5° threshold).
Adjacent: P088 posture context (~45° shoulder start, qualitative); F8 phase
tables (descriptive, NOT joint-angle time series). Safe: scenario scripts as
test patterns; event/sync roles for video. MUST NOT: ADL arcs labeled as
measured match ROM (C-18); no technique pose asserted as data.

## N. ARM-WRESTLING-SPECIFIC KINETICS (see dedicated section below)

Required: joint torques, hand forces, grip forces, table reactions, opponent
interaction forces, pressure distributions. Present: NONE sport-measured (D-01/
D-02/D-03); P083 residual gates are gait-derived (C-22, sanity gates only);
P084 ±2 SD gate applies to fitted MAs, not to kinetics. Safe: validation
harness R-08 (metrics E-14 + P087 guides as REFERENCE bands, never pass/fail).
MUST NOT: torque/force predictions presented as human values; "pass" promoted
to Validated (cap: Partially, F5).

## O. ARM-WRESTLING-SPECIFIC EMG (see dedicated section below)

Required: muscle activation/EMG across techniques/phases. Present: P080 pattern
(PT 37.56 / brachioradialis 29.93 / biceps 17.6 %MVC — ranking target ONLY) +
finger-extensor antagonist role (F4 qualitative) + EMD ~100 ms alignment target
(P085). Missing: 15-technique EMG, timings/magnitudes, kinetic-chain split
(D-01/D-08/D-11). Safe: recruitment-order pattern check (MVP acceptance #3),
cross-correlation lag validation. MUST NOT: EMG→force inference; technique EMG
as torque evidence.

## P. INDIVIDUAL/SUBJECT SCALING

Required: segment scaling (manual factors + AddBiomechanics bilevel, F2 S as
METHODS); population distributions (D-12 UNKNOWN — means/SDs only, no joint
distributions); sex/ethnicity effects S as PRINCIPLE (P022–P025 cohorts);
training correlations context (P036/P037); MA CV perturbation (P049).
Present: humerus mass/inertia baselines (P019/P020, generic male, rescale per
subject); 20% generic-scaling error (P090) + 180% MT-swap sensitivity (P089)
as uncertainty MANDATES. MVP offers 2–3 labeled presets (grip scales P071 + CV
perturbation, all flagged) — ASSUMPTION scaffolding. Safe: scaling pipelines +
preset slots with cohort labels; never a universal "average human" (MASTER §6).
MUST NOT: Tier2/3 PCSA as defaults (X-03); elite presets; bone-adaptation
presets (D-04); "elite +20%" multipliers (no evidence).

## Q. INJURY/FAILURE MECHANICS

Required: rate-dependent tissue laws + validated FE + prospective injury linkage
(D-07 — all absent). Present: humeral torsion stress equations E-13 (MODEL_DERIVED
predictions: 50–71 Nm band, 60 MPa peak, 115 mm site + EMPIRICAL location
corroboration); material E/ν as-used values (P074); FE band P075/P076 + location
P077 as REFERENCE_ONLY context. Status: DO NOT IMPLEMENT YET (X-01). Safe:
NOTHING (not even scaffolded damage flags — excluded to prevent scope creep into
clinical claims). MUST NOT: fracture prediction, damage rules, ligament failure,
tendon-energy tactics, any clinical/training advice output (MASTER §21).

---

## CRITICAL ARCHITECTURAL ANALYSIS — is 1-DOF-per-joint enough?

Current architecture: decoupled scalar 1-DOF hinges + scalar MA providers +
rigid-tendon Hill + prescribed excitations + semi-implicit Euler. Verdict: valid
for the elbow thread and the rotation scaffold, INSUFFICIENT for the final
simulator. Required generalizations (each traced):

- 3D rigid bodies (position + orientation per segment): REQUIRED by contact —
  E-04 patch sums need world-frame r-vectors recomputed each step (SUPPORTED
  principle, F3); table plane constraints need poses; opponent wrench needs
  frames. Scalar angles cannot express these.
- Multiple coupled rotational DOFs: GH is anatomically 3-rotor (S); wrist is an
  irreducible coupled 2-DOF ellipsoid (P016 — two 1-DOF hinges would contradict
  measurement); elbow↔pronation MA coupling is SUPPORTED (§8 rotation spec; F6
  mandates 2-D fits), so the MA layer must become multi-input even where joints
  stay 1-DOF.
- Translational DOFs: P009 documents flexion-axis translation/rotation during
  motion (hinge approximate); PRUJ/DRUJ coupled micro-motion ±5° (F4). Needed for
  full-fidelity axis realism — AFTER rotations are correct, not before.
- Scapular/shoulder-girdle motion: segments exist (clavicle strut, AC/SC joints);
  quantitative rhythm UNKNOWN (D-10) — architecture must RESERVE the coupling
  (locked-or-prescribed ASSUMPTION carried), not implement it.
- Radius/ulna relative motion: ulna-fixed rotation is the current ASSUMPTION;
  true axis needs both-bone kinematics (deferred with axis micro-motion).
- Wrist coupling: as above — 2-DOF joint object with obliquity, not two hinges.
- Hand/finger articulation: MCP/IP hinge DEFINITIONS exist (ISB); mechanics
  absent (D-06) — reserve articulation slots in the hand frame, implement nothing.

Earliest generalization point: the WRIST (B/C) — its implementation requires a
coupled 2-DOF joint object (P016 forbids the 1-DOF-per-axis pattern), and the
CONTACT system (H) requires 3D segment poses. Between now and then, the current
architecture remains sufficient for: fitted 1-D/2-D MA providers, passive-curve
providers, single-muscle additions via actuator ABCs, GH 3-angle KINEMATICS
interface, and all scaffold/interface work. DO NOT implement the generalization
yet (task constraint) — but all new interfaces must accept vector-valued joint
states (q as array-like) so the generalization is non-breaking. The elbow and
rotation modules already isolate angle I/O behind joint objects, which is the
seam the generalization will exploit.

## ARM-WRESTLING-SPECIFIC RESEARCH (data obtainable ONLY from the sport)

| # | Quantity | Status | Evidence / gap |
|---|---|---|---|
| S1 | Competitive joint angles (all joints, techniques, phases) | MISSING | D-01; P086 excludes phones |
| S2 | Angular velocities | MISSING | D-01 |
| S3 | Joint torques | MISSING | D-01; P083 gates are gait-derived, not sport data |
| S4 | Muscle activation/EMG (timings + magnitudes) | PARTIALLY (pattern only) | P080 ranking; 15-technique EMG missing |
| S5 | Grip forces (total + patch-resolved) | PARTIALLY (totals) | P071 totals task-adjacent; distribution D-03 missing |
| S6 | Hand (opponent-interface) forces | MISSING | D-01 |
| S7 | Table reaction forces (pad + surface) | MISSING | D-02/I-League gap |
| S8 | Opponent interaction forces | MISSING | D-11; excluded scope |
| S9 | Pressure/contact distributions | MISSING | D-03/D-06 |
| S10 | Technique-specific kinematics (hook/top-roll/press time series) | MISSING | F8 has phases + objectives, NO time series |
| S11 | Technique-specific kinetics | MISSING | F8 objectives are qualitative targets (hard rule: never gains) |
| S12 | Smoothness/strategy targets | PARTIALLY | P081 MJ band (candidate target, not technique-resolved) |
| S13 | Holding-phase isometric norms | PARTIALLY | P082 with plane/gravity mismatch labels |
| S14 | Winner/loser posture context | PARTIALLY | P088 qualitative (IR + isometric vs eccentric) |

Nothing missing may be inferred from adjacent data; each MISSING row needs
purpose-built measurement (D-01 protocol: marker mocap + instrumented table +
EMG + synced video per F5 template).

## RESEARCH PRIORITY (implementation dependency, NOT scientific importance)

- P0 (blocks basic architecture): multi-DOF/3D kinematics framework DECISION
  (vector-q interfaces; coupled wrist object design; pose-carrying segments) —
  must be settled before B/C/E/H code; rotation MA-fit pipeline readiness
  (F6 workflow + Holzbaur export access) before numerical rotation muscles.
- P1 (before numerical implementation): rotation 2-D MA coefficients + PT tendon/
  dynamics constants (A); wrist MA surfaces + architecture for ≥1 muscle (B/C);
  passive torque–angle curves elbow→wrist (G); GH MA + cuff architecture minimum (E).
- P2 (before realistic contact): target-interface Stribeck laws (H; D-02);
  patch-resolved grip + S(θ) law (H/D; D-03); table surface + pad properties (I);
  finger-resolved mechanics minimum (D; D-06); 3D pose pipeline (architecture).
- P3 (before validation): D-01 sport dataset (kinematics/kinetics/EMG S1–S11);
  residual/metric acceptance per F5; phone exclusion maintained (P086).
- P4 (future refinement): fatigue rates (L; D-09); k_noise/gains/coordination
  (K; D-08); individualisation distributions (P; D-12); scapular rhythm +
  stability envelopes (E/G; D-10); kinetic-chain split (J; D-11); Huxley
  cross-checks; MPC/learned control (D-14, post-validation only); injury
  constitutive laws (Q; D-07 — implementability gate stays CLOSED until then).

Closing rule (unchanged): before writing the next line of biomechanical
simulation code, the questions in `NEXT_RESEARCH_BATCH.md` are answered in
dependency order; provisionals stay provisional; no simulation output is
biological validation.
