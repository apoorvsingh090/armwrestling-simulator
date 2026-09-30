# Research Audit — Arm-Wrestling Biomechanics Corpus (8 files)

All 8 source files in `C:\Users\Apoorv\Downloads\research\` were read completely.
No values below are invented. Every number traces to its source file + cited reference inside that file.
"Source [N]" means reference [N] as cited *inside that research file*, not an independent verification.

Short file keys used throughout all outputs:

- F1 = Hierarchical Controller (Finite-State Supervision + Inverse Dynamics)
- F2 = Methodological Blueprint (Validated, Interpretable Simulation)
- F3 = Physics-Based Specification (Contact Forces and Torques)
- F4 = Rigorous Biomechanical Specification (Evidence-Based Dataset)
- F5 = Tiered Validation Framework (Statistical Metrics, Evidence, Sensors)
- F6 = Moment Arms (C1-Continuous Muscle Moment Arms)
- F7 = Computational Efficiency (Hill-Type Model + Joint Specification)
- F8 = Biomechanics of Victory (Phase-Separated Torque/Leverage/Control)

---

## F1 — Hierarchical Controller for Biomechanically Realistic Interactive Simulation

**Scope:** 5-layer neuromuscular controller (sensory → FSM supervisor → inverse-dynamics/optimization → rapid-force/activation → forward dynamics). General interactive simulation, NOT arm-wrestling-specific. Compares FSC, inverse-dynamics+optimization, MPC, optimal control, RL (RL explicitly excluded for phase 1).

**Major topics:** lumped sensory delays/noise; FSM task phases (Preparation, Ramp-Up, Steady-Hold, Release); inverse dynamics + static optimization (min Σu²); null-space co-contraction; Zajac/Hatze activation; 4CCr fatigue; Hill-type forward dynamics; rigid-tendon and damped-equilibrium simplifications; reduced-DOF assumption; validation toggle for delays/noise.

**Important parameters:**
- Proprioceptive delay ~25 ms base (F1 §Sensory, refs [24][26]).
- Distal adder +25 ms (shank vs hip example — lower-limb example, not arm).
- Contact/CoP delay ~40 ms (ref [5]).
- Vestibular/visual adder +100 ms.
- SDN: `s_noisy = s_true + k_noise·s_true·R`; k_noise via optimization (CMA-ES), no fixed value given.
- Activation: Zajac `dq_Z/dt = (σ − q_Z)/τ + β·(q_0 − q_Z)`; τ_a 0.01–0.05 s; τ_d ~0.04 s; β 0.1–1.0; q_0 0.001–0.05.
- Damping c = 2.5 Ns/m default (damped equilibrium model).
- Speedups: rigid tendon 2–54×; damped equilibrium 1–29×.
- Reduced DOF 3–6; timestep 1–10 ms.

**Equations:** τ_net = M(q)q̈ + C(q,q̇); min Σu_i²; Zajac ODE; Hill CE/PEE/SEE/SDE structure (described, not fully equationized); 4CCr compartments (described qualitatively).

**Cited studies (as cited in F1):** Zajac activation; Hatze (complex alternative); 4CCr fatigue model (Frontiers Physiol 2025); Millard 2013 (muscle); tendon-rigidity speedup study; damped-equilibrium study; FSM/MPC/RL control literature; sensory-delay literature. No arm-wrestling data.

**Assumptions:** reduced 3–6 DOF model; lumped delays/noise; FSM captures high-level logic; rigid tendon valid for stiff tendons/slow motions; SDE damping 2.5 Ns/m is neutral.

**Model-derived values:** speedup factors; damping default; delay adders.

**Empirical measurements:** effectively none owned by F1; all numbers are literature imports (activation time constants, delays).

**Unsupported claims:** that lumped 25 ms + adders transfer to the arm (example given is hip vs shank); that listed speedups transfer to an arm-wrestling model (hardware/solver-dependent, acknowledged).

**Limitations (stated):** model-error sensitivity (mass/inertia/moment arms); FSM brittleness to novel perturbations; hardware-dependent real-time performance; validation against human data is hard.

**Overlaps:** F2 (FSM + inverse dynamics + optimization + Hill + fatigue + no-RL); F7 (Hill simplifications, rigid tendon, activation ODE vs excitation-driven — CONFLICT, see research_conflicts.md); F5 (validation, delays/noise toggle).

---

## F2 — Methodological Blueprint for a Validated, Interpretable Simulation

**Scope:** 3-layer OFC-inspired hierarchy (low physiological / mid finite-state supervisor / high phase-based technique) + 12-step bottom-up implementation plan + ASME V&V40 validation. Arm-wrestling-specific in intent; parameters mostly imported from general upper-limb models.

**Major topics:** Hill-type actuator with delays/noise/rate limits/co-contraction; static optimization vs CMC; PD/feedforward; technique→phase→[targets, torques, activation strategy, hand-contact objective]; hook/top-roll/press phase sketches; BHaM dataset; RMSE/Bland-Altman/residual thresholds; Holzbaur 7-DOF skeleton; AddBiomechanics scaling; restraint functions; PCSA/Fmax calibration.

**Important parameters:**
- 7 DOFs (shoulder elev, elev plane, shoulder rotation, elbow flexion, forearm rotation, wrist deviation, wrist flexion); segments clavicle/scapula/humerus/ulna/radius/proximal carpal row/hand (Holzbaur et al.).
- Humerus mass ~1.997–1.998 kg; inertia (0.01228, −0.00035, −0.00023, 0.00255, 0.00123, 0.01258) kg·m².
- Elbow restraint peak stiffness 100 Nm/deg; damping 0.001745 Nm·sec/° (Rankin et al. via Holzbaur).
- Brachialis Fmax 1177.4 N; Subscapularis 1306.9 N; Brachialis Lopt 8.6 cm / slack 5.4 cm; Subscap Lopt 8.7 cm / slack 3.3 cm; pennation Subscap 20°, Lat dorsi 25°.
- Validation: residual force <5% net external; residual torque <1%·F·COM-height; moment arms ±2 SD; marker <1.5 cm; labels Validated/Partially/Unvalidated.
- BHaM: 30 adults, kinematic/kinetic/EMG.

**Equations:** inverse dynamics (described); static optimization min Σa²; PD control (described); moment-arm validation criterion. No new equations derived.

**Cited studies:** Holzbaur et al. (upper-extremity model); McConville/Gordon (cadaveric inertia); Rankin (elbow restraint); BHaM; AddBiomechanics; ASME V&V40; GUM.

**Assumptions:** 50-actuator Holzbaur model is a valid starting point; BHaM tasks transfer to arm-wrestling sub-movements; static optimization preferred over CMC for cost reasons; full 3-element Hill recommended (CONFLICTS with F7 rigid-tendon minimal model).

**Model-derived values:** scaled masses/inertias; fitted Fmax; calibrated slack lengths.

**Empirical measurements:** BHaM (n=30); Holzbaur calibration (5 healthy young males for joint-moment fitting); cadaveric inertia sources.

**Unsupported claims:** technique decompositions (hook/top-roll/press phases) rest on a non-peer-reviewed training guide (healthstartsinthekitchen) + expert observation — correctly presented as interpretable scaffolding, not validated biomechanics.

**Limitations (stated):** no public synchronized arm-wrestling dataset (kinematics+EMG+forces) — single biggest risk; outputs without it are at best partially validated.

**Overlaps:** F1 (control layers, optimization, no-RL); F4 (Holzbaur params, PCSA, validation ±2 SD); F5 (metrics, BHaM, V&V40); F8 (technique phases).

---

## F3 — Physics-Based Specification (Contact Forces and Torques)

**Scope:** Hand interaction only: regularized Stribeck friction + 3-patch lumped contact + grip→torque mapping + MuJoCo-oriented engine-agnostic implementation + explicit data-gap catalog. No muscle/joint modeling (tendon excursion deliberately collapsed into moment-arm torque mapping).

**Major topics:** Stribeck exponential friction with tanh/ε regularization; skin-skin and skin-table coefficient review; palm/finger/thumb patches; static-equilibrium torque Σ(r×F); wrist-grip coupling S(θ); force-distribution ratios; MuJoCo compliant contact (solref/solimp); system-ID (CMA-ES pendulum), history-matching + ABC, physics-aware sim-to-real, conformal prediction.

**Important parameters:**
- Ft = −μ(|vt|)·Fn·vt/(|vt|+ε); μ(|vt|) = μk + (μs−μk)·exp(−|vt|/vs).
- Skin-skin dry: μs ~0.5–0.7, μk ~0.5 (general reviews); palm 0.62±0.22; Zhang/Mak avg kinetic 0.46±0.15; one palmar study 0.25 dry / 0.35 moist; wet >1.0.
- Skin-table: ASSUMED 0.25–0.5 dry (glass/steel proxies); wet 0.7–1.4 (proxies) — flagged MAJOR GAP.
- vs ASSUMED 0.022 m/s (finger-pad-on-glass proxy) — flagged CRITICAL GAP.
- ε ~1e-8–1e-12 (numerical).
- Patch positions (m, ASSUMED): palm (0,0,0.05); fingers (0,0.08,0.03); thumb (0.04,0.06,0.02).
- Thenar ~40% of power-grip load; finger split 1/3:1/3:2/9:1/9 (Freund 2002 via hand-arm vibration study); implemented ratios R_palm 0.4 / R_fingers 0.53 / R_thumb 0.07 (ASSUMED).
- Fn,total = G_input·Fmax_individual·S(θwrist); non-optimal wrist −30% grip; CCW fingertip +42% vs CW.
- MAX_GRIP_FORCE ~442 N male / ~215 N female (dynamometry study [55]).
- Master catalog: MU_STATIC 0.6 / MU_KINETIC 0.5 (ASSUMED); torsional/rolling 0.01–0.02; MuJoCo QP <1 ms; target <1 ms/contact solve.

**Equations:** Stribeck pair (above); Fn,total sum; τ_contact = Σ(r_i × F_i); MuJoCo penalty F_normal = −K·gap − D·gapdot; calibration objective min_θ‖f_sim(θ)−f_real‖².

**Cited studies:** bio-tribology reviews (Zhang/Mak; skin tribology); finger-pad/glass fracture-mechanics model (Vs=22 mm/s); Freund 2002 finger ratios; grip-posture study (optimal wrist, −30%); torque-direction dynamometry [55]; Lee et al. 2022 (Stribeck ID via CMA-ES); MuJoCo solver literature.

**Assumptions:** 3 patches capture net wrench; rigid flat hand; constant distribution ratios as first implementation; Gaussian-like S(θ); compliant-solver paradigm.

**Model-derived values:** patch positions; distribution ratios; MU_STATIC/KINETIC catalog entries; S(θ) shape.

**Empirical measurements:** grip maxima (442/215 N); tribology proxies; −30% posture effect; 42% direction effect; 40% thenar share. NO direct skin-skin or skin-table Stribeck measurement under arm-wrestling loads.

**Unsupported claims:** none presented as supported — gaps are explicitly flagged (the file's main virtue).

**Limitations (stated):** no pre-sliding/hysteresis/stick-slip (LuGre/Dahl omitted); no tissue compliance; no neuromuscular redundancy; solver-paradigm lock-in; all friction params tentative.

**Overlaps:** F5 (validation methods, need for instrumented dynamometry); F8 (grip/thumb/cupping mechanics); F4/F6 (wrist posture effects); F1/F2 (CMA-ES, contact-delay context).

---

## F4 — Rigorous Biomechanical Specification (Evidence-Based Dataset)

**Scope:** Skeleton/kinematics + muscle architecture + bone/ligament injury mechanics + 3-tier population hierarchy + uncertainty methodology + JSON/CSV/YAML implementation schema. The broadest file; also the source of most anatomical numbers.

**Major topics:** ISB coordinate systems; elbow/radioulnar/wrist ROM; arm-wrestling posture (shoulder ~45° flex, elbow fixed, wrist semi-supinated; winner concentric/isometric vs loser eccentric); PCSA vs anatomical vs functional CSA; sarcomere normalization (2.7 μm); moment-arm peaks; cortical-bone FE; humeral spiral-fracture torsion model; ligament strengths; Tier1/2/3 populations; GUM/Monte-Carlo/cross-validation vs OpenSim/AnyBody.

**Important parameters:**
- Shoulder active ROM: flex 0–170°, ext 0–30°, abd 0–170°, ER 0–90°, IR 0–80°.
- Elbow: active flexion 130–154° (text) / 0–145° (table, AAOS); males +5–8° hyperextension; carrying angle 11° M / 14° F; MFA varus 3.1±1.9°; Euler-sequence sensitivity up to 50°.
- Forearm: cuff-device mean 76° pron / 80° sup; table 0–80 pron / 0–87 sup (elbow 90°); goniometer −50/+50; passive +3–5°; coupled ±5°.
- Wrist: 80° flex / 70° extension active; mechanical axes oblique 26.6°.
- EMG (%MVC): biceps 17.6, brachioradialis 29.93, pronator teres 37.56.
- Architecture ([92], n=10): biceps long 23.2 cm / 4.6 cm²; triceps long 45.4 cm / 10.3 cm²; brachioradialis 17.7 cm / 1.2 cm²; pronator teres 5.5 cm / 1.1 cm². Deltoid 22±6 cm², penn 16±2°.
- Moment-arm peaks ([92]): brachioradialis 7.7 cm; pronator teres 4.9 cm; biceps long 4.7 cm; triceps long 2.3 cm.
- Bone: E 400 MPa; ν 0.3; fracture torque 50–71 Nm (FE) / 80 Nm (200 N × 0.4 m calc); peak stress 60 MPa (4–5× permitted); failure 115 mm above elbow, posteromedial; spiral fracture of distal third.
- Ligaments: MCL-ant 261±71 N; MCL-post 159±40 N; RCL 233±116 N; palmaris longus 358±88 N.
- Anthropometry: humerus length 30.5±2.1 cm, midshaft circ 6.2±0.8 cm (Indian); capitellum 21.10±2.03 mm, trochlear groove 16.63±1.96 mm (Chinese); humeral-head diameter 42.3 mm (Indian n=50, mean age 37.8); retroversion 33.5° vs 24.5° Western.
- Tiers: general corr. elbow-flexor CSA–power r=0.81; pec CSA–bench r=0.866; biceps thickness +12% after 12 wk; Tier2 +20% assumed; Tier3 +20–25% further (e.g., pronator teres 1.1 → 1.1–1.32 → 1.32–1.65 cm²) — ASSUMPTIONS.
- Sensitivity: MT-param swaps change single-muscle force up to 180%; generic scaling error up to 20%.

**Equations:** ΣF=ma; Σ(r×F)+τ_ext = Iα + ω×(Iω); F_active = Fmax·fl·fv; τ = T·r/J with J = π/32·(D⁴−d⁴); PCSA = Volume/Lopt.

**Cited studies:** ISB standards; dual-fluoroscopy MFA; wrist-axis obliquity; cadaveric architecture [92]; DTI forearm; EMG arm-wrestling studies; Pedrazzini fracture hypothesis; humeral FE studies; ligament tensile studies; Indian/Chinese osteometry/CT; tennis/gymnast bone-adaptation (analogy only); OpenSim/AnyBody; GUM.

**Assumptions:** Tier2/3 multipliers; tendon-slack-as-calibration; ligament spring laws; generic-model cross-validation transfers.

**Model-derived values:** Tier2/3 extrapolations; FE fracture torques/stresses; scaled inertia; 80 Nm hand calc.

**Empirical measurements:** ROM tables; PCSA/fiber lengths; moment-arm peaks; EMG %MVC; ligament strengths; osteometry; bone E/ν (as used in cited FE).

**Unsupported claims:** arm-wrestler bone remodeling (explicitly flagged as plausible-but-unevidenced); Tier3 architecture numbers (flagged as assumptions — must stay assumptions).

**Limitations (stated):** PCSA/FCSA confusion in literature; un-rescaled fiber lengths cause large PCSA errors; many params lack uncertainty; no elite-arm-wrestler architecture/morphology data; dynamic pennation unmeasured; ligament/cartilage laws ill-defined; control strategy out of scope.

**Overlaps:** every other file (Holzbaur/Fmax with F2; friction/posture with F3; metrics with F5; moment arms with F6; Hill/ROM with F7; techniques/posture with F8).

---

## F5 — Tiered Validation Framework

**Scope:** Validation methodology only: statistical metrics + 4-tier evidence hierarchy (sport-specific → isometric → dynamic → clinical) + smartphone-protocol appraisal + structured test template + V&V synthesis. No anatomy or muscle parameters owned.

**Major topics:** RMSE/nRMSE; Bland-Altman (bias ±1.96 SD); ICC models/benchmarks; cross-correlation/EMD; DTW; QOI/COU (ASME V&V40); regression/sensitivity when no consensus threshold; p-box outputs; event detection vs kinematics for phones.

**Important parameters:**
- nRMSE <10–15% "often good" (task-dependent); knee-torque benchmark 5.9–11.2%.
- ICC: <0.5 poor, 0.5–0.75 moderate, 0.75–0.9 good, >0.9 excellent; absolute-agreement model required.
- EMD ~100 ms for EMG→force alignment.
- Arm-wrestling Tier1: sEMG (PM/BB/PT/FCU); Fmax ICC very high, RFDmax moderate–high; Mean Jerk 3.37±0.797 m/s³.
- Tier2: peak elbow-extension torque ~55° flexion; elbow flex ~7 kg-m (M) / 3.5 (F); ext ~4 (M) / 2 (F); grip ~7 (M) / 3.5 (F) — units as given in source ("kg-m", sic).
- Tier4: functional elbow 100° arc; forearm 100° total (50/50); shoulder passive torque-angle curves.
- Phones: elbow MAE 21.5–28.9° (2D) / 16.3–26° (3D); MediaPipe elbow RMSE 12.76–14.17° (20.49° Paralympic), wrist 8.74–9.59°; OpenCap 13.81–30.02° upper limb; sub-5° threshold never met; velocity RMSD ≤0.17 m/s, R² 0.96–0.98; ≥60 fps; clap/TTL sync.

**Equations:** RMSE/nRMSE; Bland-Altman LoA = bias ±1.96 SD; ICC variance ratio; DTW warping distance (all standard forms, described not derived).

**Cited studies:** knee-torque nRMSE study; MediaPipe vs OMC; 11-model HPE evaluation; OpenCap; boxer shadow-boxing validation; isometric torque-angle studies (transverse plane, 90° humeral elevation); wheelchair-basketball force–velocity; arm-wrestling reliability studies.

**Assumptions:** isometric transverse-plane data transfers to quasi-static pinning (with documented mismatch); ballistic-task energetics transfer to the "hit"; velocity-from-video transfers (with caution); MJ transfers as control target.

**Model-derived values:** none — framework only.

**Empirical measurements:** all metric benchmarks above; MJ baseline; reliability ICCs.

**Unsupported claims:** none asserted; phone-as-kinematics explicitly rejected.

**Limitations (stated):** no gold-standard arm-wrestling dataset (kinetics + 3D kinematics + EMG); plane/gravity mismatches for Tier2–4; phone occlusion/depth ambiguity/velocity-dependent error; no injury-threshold validation (excluded by design).

**Overlaps:** F2 (V&V40, residuals, ±2 SD, BHaM); F3 (need for dynamometry, HM/ABC); F1 (EMD/delays context); F6 (moment-arm agreement standard); F8 (EMG/MJ sources).

---

## F6 — C1-Continuous Muscle Moment Arms

**Scope:** Moment-arm data compilation + C1 requirement + evidence tiers (in-vivo loaded → loaded cadaver → passive cadaver → computational model) + per-muscle findings + polynomial-fitting workflow. 16 muscles: biceps, brachialis, brachioradialis, triceps (3 heads), pronator teres, pronator quadratus, supinator, FCU, FCR, ECU, ECRL/B, APL, deltoid (3 parts), pec major (3 parts), lat dorsi (3 parts), teres major, subscapularis (3 parts).

**Major topics:** ma = ∂L/∂θ; torque-chatter from C1 violations; linear interpolation rejected; multivariate polynomials (Harba/AICc) vs cubic-Hermite lookup; unit convention rad/m; validity ranges + clamping; CV 10–20%; multi-joint dependencies (biceps–supination, triceps–shoulder, ECU–pronation).

**Important parameters:**
- Constant-MA error ~35% mean wrist-torque reduction (extreme-sensitive).
- Elbow MA vary ≥30% over 95° arc.
- Operating ranges: elbow 5–140°, forearm pronation 5–160° (Holzbaur export grid); shoulder data 2.5–120° abd/flex.
- Wrist functionals, mid-prone 0° (Chen, n=10, 49.7±10.4 y), mm: FCR 12.2±2.1 / −10.2±2.5; FCU 11.3±2.1 / 11.7±4.2; ECU −4.0±0.9 / 23.7±3.3; ECRL −6.6±3.0 / −17.2±3.6; ECRB −10.8±2.8 / −10.0±2.2; APL 6.8±1.9 / −23.6±2.5 (FE/RUD; + = flexion/ulnar).
- MRI-vs-functional gaps: ECU FE 60.9%; FCU 23.8% FE / 41.1% RUD; FCR/ECRL/ECRB n.s.
- Shoulder (Kuechle, n=8, 4M/4F, mean 87 y): inferior subscapularis IR peak 27.0 mm (sagittal flexion); pec/lat/teres largest depressor MAs; pec-major transfer drops after 30° IR.
- Fit quality RMS <0.757% (Harba); polynomial eval <10 μs.

**Equations:** ma = ∂(length)/∂θ; ma = f(θ_elbow, θ_pronation[, θ_shoulder, θ_wrist…]) multivariate polynomial (form, not coefficients — coefficients must be FITTED, not invented).

**Cited studies:** Murray et al. (elbow MA); Chen et al. (wrist tendon-excursion + MRI); Kuechle et al. (shoulder tendon-excursion, 10 N loading); Holzbaur/MoBL-ARMS; Harba et al. (autogenerated polynomials, AICc); OpenSim PolynomialPathFitter/MultivariatePolynomialFunction; rtosim splines.

**Assumptions:** Holzbaur exports anchor reality outside measured ranges; linear/polynomial pronation-fill for wrist muscles is a "reasonable first approximation"; normalization by size removes most variability.

**Model-derived values:** all polynomial recommendations (no coefficients exist in sources); 3D-fit proposals per muscle.

**Empirical measurements:** Chen wrist table; Kuechle shoulder curves; Murray elbow variations; CV 10–20%.

**Unsupported claims:** that a ready-to-use equation set exists (file correctly states it does NOT — a key finding, not a gap in the audit).

**Limitations (stated):** no Tier-1 in-vivo loaded MA at arm-wrestling extremes; cadaver mid-range only; edge-derivative errors; passive-tissue only; elderly shoulder specimens (87 y mean); pronator-quadratus data essentially absent.

**Overlaps:** F4 (peak MAs [92] vs functional MAs here — same muscles, different methods); F7 (polynomial architecture, clamping, variability); F2 (MoBL-ARMS, ±2 SD standard); F5 (agreement criterion).

---

## F7 — Computational Efficiency (Hill Model + Joint Specification)

**Scope:** Minimal real-time Hill model (>500 Hz) + offline advanced model (Huxley or extended Hill) + ISB joint specification with anatomical-vs-feasible ROM. Prescriptive for speed; explicitly trades fidelity.

**Major topics:** Hill (ODE) vs Huxley (PDE) vs phenomenological extensions; excitation-driven bypass; Gaussian FL; linear FV; rigid tendon; SDE; length-dependent activation ρ; nonlinear PEE/SEE; fatigue; GH/elbow/radioulnar/wrist JCS, zeros, ROMs, ADL-based feasible arcs, ligament constraints (MCL/LUCL/TFCC/annular).

**Important parameters:**
- F_total = E·fL·fv·Fmax (E 0–1, dimensionless).
- fL = exp(−0.5·((L−Lopt)/σ)²) (symmetric Gaussian).
- fv = 1 − v/vmax (linear, isometric-neighborhood only).
- Rigid tendon: L_MTU = L_CE; 2–54× faster; ~20% Fmax MAE.
- Excitation-driven +9.6 Hz vs activation-driven (study-specific hardware).
- Huxley rates (rabbit psoas, 20 °C): k2 440 s⁻¹, k4 56 s⁻¹, k−4 129 s⁻¹.
- GH: 3 rot DOF; origin humeral-head center; X ant / Y sup / Z lat; zero neutral; anat ~180 flex/ext, 90 abd/add, 90 IR/ER; feasible UNCERTAIN (start 45° flex + progressive IR; 25–30% head–glenoid contact).
- Elbow: 1 DOF; zero 90° flexion (THIS FILE — conflicts F4); anat 0–145°; feasible 30–130° ADL; MCL valgus limit.
- Radioulnar: 1 DOF; zero neutral (elbow 90°, thumb-to-shoulder); anat 80 pron / 85 sup; feasible 50/50 ADL.
- Wrist: 2 DOF; origin distal-radius carpal surface; zero forearm-vertical/3rd-metacarpal-aligned; anat 80 flex / 70 ext / 20–25 rad / 30–35 uln; feasible ≈40° flex-side functional subset (see conflict C-20 on ext/pron wording).

**Equations:** minimal-model triple (above); Hill hyperbola F = Fmax·vm/(vm+v) − c·v (reference); extended-model features (double-hyperbolic, ρ-term, nonlinear PEE/SEE) described qualitatively.

**Cited studies:** Hill 1938; Huxley/Niedergerke; Zahalak 1981; Millard 2013 (rigid-tendon benchmark); AnimatLab linear Hill; Lemaire (Huxley vs Hill stretch-shortening); ISB JCS; MCL/LUCL/TFCC anatomy; arm-wrestling posture study (shoulder 45°).

**Assumptions:** E ≈ Ca²⁺/instantaneous stress (ignores E–C coupling); symmetric FL; linear FV near isometric; infinite tendon stiffness; ADL arcs bound safe arm-wrestling ROM; GH stability = muscular.

**Model-derived values:** feasible-ROM arcs (principle-based, not measured); speedup/MAE trade-offs.

**Empirical measurements:** Huxley rates (non-human); benchmark speedups; anatomical ROMs; 45° start posture.

**Unsupported claims:** none asserted as measured — feasible ROMs are explicitly principle-constrained, two joints flagged for future measurement.

**Limitations (stated):** no fatigue/potentiation/EMG transients; no eccentric realism; no tendon energy/storage/oscillation damping; no length-dependent activation; absolute-force errors in dynamics.

**Overlaps:** F1 (activation ODE vs bypass CONFLICT; rigid-tendon agreement; SDE agreement); F2 (3-element Hill CONFLICT); F4 (ROM/ISB/posture — partial conflicts); F6 (polynomials/clamping); F8 (posture/muscles).

---

## F8 — Biomechanics of Victory (Phase-Separated Techniques)

**Scope:** Foundational mechanics + descriptive + theoretical (control-objective) models for hook, top roll, press, cupping, rising, containment, posting, back/side pressure, shoulder commitment. Qualitative-evidence synthesis; NO simulator numbers owned.

**Major topics:** T = r·F·sinθ; F = ma; leverage/limb-length trade-offs; kinetic chain (tennis 51–55% legs/trunk — explicitly non-arm-wrestling); EMG roles (PM static/side, PT dynamic pronation, FCU wrist, finger extensors antagonists); per-phase joint/force/muscle/grip tables; technique→control-objective inference (target config + torque directions + activation strategy + hand-contact objective); evidence tiers T1–T4.

**Important parameters:** effectively none owned. Imports: MA vary 30%/95° arc; biceps MA peak extended; kinetic-chain 51–55% (tennis, not transferable as arm-wrestling quantity); EMG qualitative rankings (see F4 for the only %MVC numbers).

**Equations:** T = r·F·sinθ; F = m·a (first-principles framing only).

**Cited studies:** EMG arm-wrestling simulations (static/dynamic); hook/top-roll/press coaching literature (Brzenk, Larratt); kinetic-chain (tennis/baseball); elbow/muscle clinical anatomy; training guides.

**Assumptions:** techniques decompose into Setup → Loading → Attack → Hold → Transition → Counter; expert observation transfers to control objectives; tennis kinetic-chain principle transfers qualitatively.

**Model-derived values:** "inferred control objectives" per technique (clearly labeled as inference, not measurement).

**Empirical measurements:** none original; Tier1 EMG cited qualitatively (muscle rankings, not joint torques).

**Unsupported claims (correctly labeled as such in-file):** any quantitative torque/activation magnitude per technique/phase; 15-technique coverage (comprehensive EMG "not available"); kinetic-chain percentages for arm wrestling ("limited"); long-arm advantage (context-dependent, per file).

**Limitations (stated):** no technique-specific dynamometry; no 3D kinetics; no timing data; inferences drawn from Tier2–4 where Tier1 missing.

**Overlaps:** F2 (phase representation format); F3 (grip/thumb/contact); F4 (posture, EMG); F1/F2 (control-objective → FSM mapping, without numeric modifiers).

---

## Cross-file topic map (where to look first)

| Topic | Primary file(s) | Supporting |
|---|---|---|
| Controller (FSM, optimization, MPC/RL) | F1 | F2 |
| Technique phases → control objectives | F8, F2 | F1 |
| Validation metrics + evidence tiers | F5 | F2 |
| Skeleton, ROM, ISB frames | F4, F7 | F2 |
| Muscle architecture (PCSA/fibers) | F4 | F2, F6 |
| Moment arms (values + C1 method) | F6 | F4 |
| Hill model + simplifications | F7, F1 | F2 |
| Activation dynamics | F1 | F7 (conflicting simplification) |
| Fatigue | F1 | F7 |
| Contact/friction/grip | F3 | F8 |
| Injury/fracture/materials | F4 | F7 (stability limits) |
| Populations/adaptation | F4 | F8 (athlete Tiers) |
| Uncertainty (GUM, MC, HM/ABC) | F4, F3, F5 | F2 |
| Phones/sensors | F5 | — |
| Implementation plan | F2 | F1, F3, F6, F7 |

## Files' own "top gaps" (their words, condensed)

- F1: hardware-dependent real-time proof; model-error propagation; FSM brittleness.
- F2: no public synchronized arm-wrestling dataset — the single biggest threat.
- F3: zero direct Stribeck measurements for either interface; zero patch-resolved force data; no quantitative wrist-coupling law; no tendon compliance data in this module.
- F4: zero elite-arm-wrestler architecture/morphology; dynamic pennation; ligament/cartilage laws; control strategy.
- F5: same dataset gap; plane/gravity mismatches; phone kinematics unfit.
- F6: zero in-vivo loaded MA at extremes; edge-derivative errors; elderly shoulders; no ready equations.
- F7: GH + wrist-secondary feasible ROMs need measurement; eccentric/fatigue/elastic phenomena absent from minimal model.
- F8: zero technique-specific joint torques/timings; 15-technique EMG incomplete.
