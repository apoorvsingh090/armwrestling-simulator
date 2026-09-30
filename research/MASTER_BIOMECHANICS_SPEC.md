# MASTER_BIOMECHANICS_SPEC — Evidence-Controlled Arm-Wrestling Simulator Specification

Conventions: **S** = SUPPORTED BY RESEARCH (corpus measurement/standard) · **M** = MODEL DERIVED
(fitted/computed from research inputs) · **A** = IMPLEMENTATION ASSUMPTION (chosen here, labeled) ·
**U** = UNKNOWN (corpus does not establish). Parameter IDs (P###) → parameters.json.
Conflicts (C-##) → research_conflicts.md. Deferred (D-##) → deferred_topics.md.

No techniques-as-modifiers and no population multipliers appear as empirical facts anywhere below.

---

## 1. Scope
- **S:** Upper-limb biomechanics for a one-arm interactive simulator: skeleton, joints, Hill-type
  muscles, C1 moment arms, activation, contact/friction, validation-gated credibility (F1–F8).
- **M:** MVP thread (§-scoped in IMPLEMENTATION_READINESS.md): segments → elbow hinge →
  biceps/triceps → activation → force → MA → torque → Euler dynamics.
- **A:** Thorax-fixed single arm; rigid-tendon + ODE-activation default branches; 3-patch rigid hand;
  ADL-bounded feasible ROM placeholders.
- **U:** Everything sport-measured (D-01–D-03); elite tissue data (D-04/D-05); injury rules (D-07);
  human-like coordination (D-08); fatigue rates (D-09).

## 2. Evidence hierarchy
- **S:** Three independent axes (C-15): POPULATION tier — general/athletic/arm-wrestler (F4);
  EVIDENCE-RELEVANCE — sport-specific → isometric → dynamic → clinical (F5, F8);
  MEASUREMENT tier — in-vivo loaded → loaded cadaver → passive cadaver → computational model (F6).
  Evidence types restricted to EMPIRICAL_MEASUREMENT, MODEL_DERIVED, FIRST_PRINCIPLES,
  EXPERT_OBSERVATION, ASSUMPTION, UNKNOWN.
- **M:** Validation gates: residuals P083, MA ±2 SD P084, metric guides P087, labels
  Validated/Partially/Unvalidated (F2/F5).
- **A:** ADL arcs as feasible-ROM placeholders (P017/P018); catalog friction placeholders (P061–P067).
- **U:** All target-interface and in-competition quantities (D-01–D-03).

## 3. Skeletal model
- **S:** Segments humerus/ulna/radius/scapula/clavicle/hand with ISB landmark definitions (F4);
  7-DOF Holzbaur chain as reference architecture (F2); humeral mass ~1.997 kg P019.
- **M:** Inertia tensor P020; scaled subject variants via manual or AddBiomechanics pipeline (F2);
  generic-scaling error up to 20% P090.
- **A:** Thorax-fixed MVP; clavicle/scapula locked or rhythm-prescribed; carpus single rigid body.
- **U:** Subject-specific geometry without new imaging (D-04/D-12); quantitative scapular rhythm (D-10).

## 4. Joint model
- **S:** GH 3-rotor ball-and-socket; elbow ~1-DOF hinge (varus 3.1±1.9° P009, carrying angle P008,
  Euler sensitivity 50° — hinge is approximate); radioulnar 1-DOF rotation; wrist 2-DOF ellipsoid
  with 26.6° axis obliquity P016; ligament stabilizers with tensile strengths P078/P079.
- **M:** Elbow elastic restraint P021; ADL feasible placeholders P017/P018.
- **A:** Pure-hinge elbow + pure-1-DOF forearm for MVP; orthogonalized wrist if obliquity deferred
  (logged); no dislocation modeling.
- **U:** Load-dependent stability envelopes GH/wrist (D-10); ligament force–length laws (D-07).

## 5. Coordinate systems
- **S:** ISB landmark frames for ulna/radius/wrist (F4); GH 3-angle decomposition + sequence
  sensitivity (F4/F7); wrist-center definition (F4).
- **M:** Holzbaur/OpenSim frame implementations (F2/F6).
- **A:** Adopted unified convention — head-center humerus origin; clinical zeros (0°=extension,
  neutral forearm/wrist); right-handed; rad/m; quaternion-internal with logged JCS conversion
  (C-01/C-13/C-14 resolutions). Full per-bone tables in coordinate_systems.md.
- **U:** "The" research-mandated humerus origin (C-13); native-grid angle conventions pre-transform (C-14).

## 6. Anthropometry
- **S:** Humerus length 30.5±2.1 cm P022; midshaft circ 6.2±0.8 cm P023; distal morphology P024;
  humeral-head ⌀42.3 mm P025 (all population-specific: Indian/Chinese cohorts; sex/ethnicity effects stated).
- **M:** Scaled masses/inertias; 10% bone-size Tier2 illustration is file-stated assumption (F4 table).
- **A:** Single-cohort defaults only with cohort label; never a universal "average human."
- **U:** Arm-wrestler segment distributions (D-04/D-12).

## 7. Muscle model
- **S:** Hill CE/PEE/SEE/SDE structure with FL (bell) + FV (hyperbolic) dependencies (F1/F2/F4/F7);
  rigid-tendon 2–54× speedup with ~20% Fmax MAE P060; damped-equilibrium + SDE rationale (F1).
- **M:** Reference branch E-10; minimal branch E-11; Huxley/extended-Hill offline branch (F7, rates P-rabbit cited as non-human reference).
- **A:** MVP = minimal rigid-tendon + ODE activation (E-08+E-10/E-11 hybrid as scoped in readiness file);
  excitation-bypass fallback logged with transient loss (C-10).
- **U:** Per-muscle σ, v_max, SEE/PEE curves, slack beyond P032/P033 (equations.md absent-list #2).

## 8. Muscle geometry (origins, paths, wrapping)
- **S:** Origin/insertion/line-of-action table for PM/lat/subscap/teres/biceps/brachialis/
  brachioradialis/PT/PQ/FCR/FDS (F4 — several PCSA cells "Not Available," preserved as such).
- **M:** Holzbaur 50-actuator paths + wrapping spheres as export source for MA fitting (F2/F6);
  MoBL-ARMS cross-validation role (F2/F4).
- **A:** Path simplifications needed for real-time wrapping (logged per muscle).
- **U:** снаряжение: subject-specific paths without imaging (D-04).

## 9. Moment arms
- **S:** Peak anchors P038–P041; wrist functionals P042–P047 with MRI-vs-functional gaps;
  subscap IR peak P048; posture-dependence mandates (P049/P050/P051: CV 10–20%, ≥30%/95°, 35% error).
- **M:** Fit-quality precedent RMS <0.757%, <10 µs eval (F6/Harba); agreement gate ±2 SD P084.
- **A:** Polynomial-vs-Hermite choice per muscle; boundary clamping; CV-based coefficient perturbation.
- **U:** ALL coefficients until fitted (E-12 absent #1); ECU full pronation surface; elderly-shoulder transfer; pronator-quadratus data (D-06/F6 limits).

## 10. Tendons
- **S:** Tendon-slack calibration-sensitivity principle (F4: slack is a calibration parameter);
  10 N-loaded excursion method as quality benchmark (F6/Kuechle).
- **M:** Two Holzbaur slack values P032/P033 (small-n fits).
- **A:** Rigid-tendon MVP equality L_MTU=L_CE (C-09 scope); SEE/SDE only in reference branch.
- **U:** Compliance, damping, slack for all other muscles; dynamic pennation (D-05).

## 11. Hand/wrist
- **S:** Wrist ROM P013–P015 + obliquity P016; grip maxima P071; −30% posture magnitude P073;
  42% direction effect + 40% thenar share (F3, expert/dynamometry context); EMG finger-extensor
  antagonist role (F4).
- **M:** Stribeck pair E-05; grip map E-06; patch sums E-04.
- **A:** Rigid hand + 3 patches P068–P070; R_i splits P072; S(θ) shape; μ/vs/ε placeholders P061–P067.
- **U:** Finger-level mechanics, thumb force paths, TFCC loading, S(θ) law (D-02/D-03/D-06).

## 12. Contact mechanics
- **S:** First-principles sums E-03/E-04; MuJoCo compliant-contact behavior (<1 ms QP precedent, F3)
  as solver-paradigm evidence; LuGre/Dahl phenomena named as omitted (F3 limits).
- **M:** solref/solimp + torsional/rolling 0.01–0.02 configuration mapping (F3 §4).
- **A:** Compliant-solver paradigm choice; warm-start/polynomial-approx optimizations; custom
  Stribeck plugin ( GUIs expose single μ — F3).
- **U:** Target-interface laws (D-02); stick-slip/hysteresis; impulse-solver port behavior.

## 13. Table constraints
- **S:** Table is the assumed flat, hard, horizontal contact plane (F3); skin-table proxies are
  glass/steel/fabric (flagged proxies, not table data).
- **M:** Table material "physics material" slots (K/D, friction triple) per F3 §4 mapping.
- **A:** Flat-rigid table; single material parameter set per session; moisture band selected per bout.
- **U:** Actual competition surface properties; pad/edge geometry effects; chalk/sweat dynamics (D-02).

## 14. Neural control
- **S:** FSM phase logic with named states (F1: Preparation/Ramp-Up/Steady-Hold/Release; F2: technique
  phase format; F8: Setup/Loading/Attack/Hold/Transition/Counter); optimization E-07 with Σu² cost;
  null-space co-contraction principle; SDN form E-09; delays P056–P058; no-RL-for-phase-1 (F1/F2);
  optimal control as offline tool (F1/F2).
- **M:** F1↔F2 layer map (C-11); PD/feedforward execution (F2); 4CCr conceptual integration (F1).
- **A:** Chosen FSM graph for MVP (hold + ramp + release minimum); toggleable delays/noise for validation.
- **U:** Gains, recruitment, k_noise, coordination patterns, MPC/learned extensions (D-08/D-14).

## 15. Fatigue
- **S:** 4CCr central/peripheral separation with qualitative task-weighting (isometric→central,
  concentric→peripheral) and recovery asymmetry minutes-vs-hours (F1); Fmax-reduction modeling
  slot in extended Hill (F7).
- **M:** None fitted in corpus.
- **A:** Optional Fmax-derate placeholder ONLY if long-bout demos require it, labeled assumption.
- **U:** All rate/recovery constants for arm muscles (D-09). No fatigue in MVP default.

## 16. Arm-wrestling techniques
- **S:** Descriptive + inferred-control-objective models for hook/top roll/press/cupping/rising/
  containment/posting/back/side/shoulder-commitment (F8); phase tables; evidence tiers T1–T4;
  EMG role rankings; posture context P088; MJ baseline P081 as control-strategy target.
- **M:** Technique→FSM-phase translation schema (F2 format + F8 objectives).
- **A:** MVP scenario scripts (neutral start → ramp → hold → release) as test patterns, not claims.
- **U:** All technique-specific torques/timings/magnitudes; 15-technique EMG; kinetic-chain split (D-01/D-11).
  HARD RULE: techniques NEVER compile to force/torque/success modifiers.

## 17. Individualisation
- **S:** Scaling pipelines (manual segment-length factors; AddBiomechanics bilevel optimization, F2);
  MA CV 10–20% P049; sex/ethnicity morphology effects (F4); training-correlation context P036/P037.
- **M:** Tier2/3 PCSA assumption chain P030/P031 (labeled ASSUMPTION, hypothetical-config use only).
- **A:** MVP offers 2–3 labeled presets (general male/female grip scales P071 + CV perturbation), all flagged.
- **U:** True population distributions; elite presets as defaults (FORBIDDEN); bone-adaptation presets (D-04/D-12).

## 18. Uncertainty
- **S:** GUM Type A/B propagation; aleatoric vs epistemic split (F4); 180% MT-sensitivity P089;
  20% scaling error P090; HM+ABC + physics-aware sim-to-real + conformal-PRE procedure (F3);
  regression/sensitivity/p-box when no consensus (F5).
- **M:** Residual + ±2 SD + metric-suite gates (P083/P084/P087).
- **A:** Assumed input distributions where corpus gives ranges without shape (uniform default, logged).
- **U:** Posterior distributions for contact/grip/MA-coefficient parameters (need D-01–D-03 data).

## 19. Validation
- **S:** Structured test format (REAL→SIM→METRIC→CRITERION + evidence table + mismatch doc, F5);
  Tier1–Tier4 evidence ladder; phone restrictions P086; BHaM n=30 context (F2); EMD P085;
  isometric norms P082 with plane/gravity mismatch labels.
- **M:** MVP acceptance set (residuals, MA ±2 SD on fitted functions, EMG-pattern match, MJ band,
  grip-scale match) — see IMPLEMENTATION_READINESS.md.
- **A:** nRMSE 10–15% working guide where no consensus (P087), never a universal pass.
- **U:** Any "Validated" label on sport-specific dynamics before D-01 data (cap at Partially Validated).

## 20. Known limitations
1. Hinge/orthogonal simplifications vs measured axis complexity (P008/P009/P016). 2. Rigid-tendon
   ~20% force error + no elastic phenomena (P060). 3. Minimal-model no-eccentric/no-transient gaps
   per branch (C-10). 4. Contact/friction placeholders (C-07/C-08). 5. Small-n/elders/cadaver
   transfer limits (P026–P048 sample metadata). 6. Generic-scaling 20% + MT-swap 180% sensitivities
   (P089/P090). 7. FSM brittleness to novelty (F1). 8. Hardware-dependent real-time (F1/F7).
   9. Phone kinematics excluded (P086). 10. No injury rules (D-07). 11. Single-arm, thorax-fixed scope.

## 21. Deferred components
D-01 dataset · D-02 friction laws · D-03 grip distribution/S(θ) · D-04 elite tissue ·
D-05 tendons · D-06 hand detail · D-07 injury rules · D-08 control fitting · D-09 fatigue rates ·
D-10 stability envelopes · D-11 kinetic chain · D-12 distributions · D-13 phone kinematics ·
D-14 MPC/learning. Plus: multi-arm (two-competitor) interaction dynamics beyond patch wrenches; graphics/audio;
any clinical/training advice output.
