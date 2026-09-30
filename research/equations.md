# Equations — Only What the Research Supports or Requires

Status per equation: FIRST-PRINCIPLES (Newton/Euler/geometry) / EMPIRICAL-or-MODEL-DERIVED
(form + parameters from corpus) / IMPLEMENTATION ASSUMPTION (chosen branch or placeholder form).
Nothing here is invented: forms the corpus does not give (e.g., fitted MA polynomial
coefficients, S(θ) shape, 4CCr rate constants) are listed as REQUIRED-BUT-ABSENT.

---

## E-01. Rigid-body translation — ΣF = ma — FIRST-PRINCIPLES
- **Equation:** `Σ F_i = m·a`
- **Variables/units:** F_i muscle/ligament/contact/gravity forces (N); m segment mass (kg, P019 + scaling); a COM acceleration (m/s²).
- **Interpretation:** linear dynamics of each segment (humerus/ulna/radius/hand).
- **Source:** F4 § equations (Newton–Euler joint equilibrium); standard mechanics.
- **Status:** FIRST-PRINCIPLES. Masses are MODEL_DERIVED baselines needing subject scaling (P019/P020/P090).

## E-02. Rigid-body rotation — Euler — FIRST-PRINCIPLES
- **Equation:** `Σ (r_i × F_i) + τ_ext = I·α + ω × (I·ω)`
- **Variables/units:** r_i moment arms/position vectors (m); τ_ext external torque (Nm); I inertia tensor (kg·m², P020); α angular acceleration, ω angular velocity (rad/s², rad/s).
- **Interpretation:** joint rotational dynamics; the solver core for elbow/forearm-track MVP.
- **Source:** F4 § equations.
- **Status:** FIRST-PRINCIPLES. I is MODEL_DERIVED; residuals gated by P083.

## E-03. Torque from force — τ = r × F — FIRST-PRINCIPLES
- **Equation:** `τ = r × F`, magnitude `T = r·F·sinθ`
- **Variables/units:** r lever/position vector (m); F force (N); θ force–lever angle; T/τ torque (Nm).
- **Interpretation:** hand-force→joint-torque conversion; contact-patch summation; leverage principle behind all techniques (F8: shortening/lengthening effective levers).
- **Source:** F3 (τ_contact sum); F8 (T = r·F·sinθ); F4 (joint equilibrium).
- **Status:** FIRST-PRINCIPLES. r-vectors are posture-dependent (SUPPORTED); patch r's are ASSUMPTION (P068–P070).

## E-04. Contact-torque summation — Σ(r_i × F_i) — FIRST-PRINCIPLES + ASSUMED GEOMETRY
- **Equation:** `τ_contact = r_palm × F_palm + r_fingers × F_fingers + r_thumb × F_thumb`; `F_n,total = Σ F_n,i`
- **Variables/units:** r_i (m, P068–P070); F_i = normal + friction vectors (N).
- **Interpretation:** net hand wrench from 3 lumped patches.
- **Source:** F3 §§2–3.
- **Status:** form FIRST-PRINCIPLES (static equilibrium); 3-patch lumping + positions ASSUMPTION; force splits ASSUMPTION (P072).

## E-05. Regularized Stribeck friction (pair) — EMPIRICAL FORM, ASSUMED PARAMETERS
- **Equations:** `F_t = −μ(|v_t|)·F_n·v_t/(|v_t|+ε)`; `μ(|v_t|) = μk + (μs−μk)·exp(−|v_t|/vs)`
- **Variables/units:** F_n normal (N); v_t tangential velocity (m/s); μs/μk dimensionless; vs (m/s); ε (m/s).
- **Interpretation:** velocity-dependent skin friction with C¹ regularization (linear-interp/tanh alternatives noted; adopted form per F3).
- **Source:** F3 §1.
- **Status:** form EMPIRICAL/MODEL-DERIVED (literature-backed); μs/μk/vs for target interfaces ASSUMPTION/UNKNOWN (P061–P066); ε ASSUMPTION (P067).

## E-06. Grip→normal-force mapping — IMPLEMENTATION ASSUMPTION (magnitude partially empirical)
- **Equation:** `F_n,total = G_input · F_max_individual · S(θ_wrist)`; `F_n,i = F_n,total · R_i`
- **Variables/units:** G_input 0–1; F_max_individual (N, P071 442/215); S dimensionless wrist scaling (assumed inverted-bell); R_i splits (P072: 0.4/0.53/0.07).
- **Interpretation:** intent + posture → patch normal forces feeding E-05/E-04.
- **Source:** F3 §3.
- **Status:** F_max_individual EMPIRICAL (task-adjacent dynamometry); S shape + R_i ASSUMPTION; −30% posture magnitude EMPIRICAL with assumed shape (P073).

## E-07. Inverse dynamics + redundancy optimization — MODEL-DERIVED METHOD
- **Equations:** `τ_net = M(q)·q̈ + C(q,q̇)`; `minimize Σ u_i²` s.t. torque match; null-space co-contraction augmentation.
- **Variables/units:** q joint angles (rad); M mass matrix; C Coriolis/centrifugal; u_i excitations 0–1.
- **Interpretation:** desired motion → net torques → unique muscle-excitation distribution; co-contraction via moment-arm null space (F1) / PD-feedforward execution (F2).
- **Source:** F1 §§3–4; F2 mid-level (static optimization preferred over CMC on cost grounds).
- **Status:** MODEL-DERIVED method choice; validity conditioned on model accuracy (masses, MAs) — stated sensitivity in F1/F2.

## E-08. Activation dynamics ODE (Zajac branch) — EMPIRICAL/MODEL-DERIVED
- **Equation:** `dq_Z/dt = (σ − q_Z)/τ + β·(q_0 − q_Z)` (split-τ_a/τ_d variant accepted)
- **Variables/units:** σ excitation 0–1; q_Z activation; τ/τ_a/τ_d (s, P052/P053); β (P054); q_0 (P055).
- **Interpretation:** excitation–contraction lag; mandatory for realistic transients and EMD (~100 ms, P085).
- **Source:** F1 § core models.
- **Status:** EMPIRICAL time constants + MODEL-DERIVED form. Alternative excitation-bypass branch (F7, E = activation) is an IMPLEMENTATION ASSUMPTION with documented transient loss (C-10).

## E-09. Signal-dependent sensory noise — MODEL-DERIVED FORM, UNCALIBRATED GAIN
- **Equation:** `s_noisy = s_true + k_noise·s_true·R`, R ~ N(0,1)
- **Variables/units:** per-channel (angles, velocities, forces); k_noise dimensionless, fit via CMA-ES (no corpus value).
- **Interpretation:** scale-dependent neural/sensor noise → force unsteadiness, co-contraction adaptation.
- **Source:** F1 § sensory.
- **Status:** form MODEL-DERIVED; k_noise UNKNOWN until identified; delays P056–P058 as stated.

## E-10. Hill-type active force (reference branch) — EMPIRICAL FORM
- **Equation:** `F_active = F_max · f_l(l_f) · f_v(v_f)` (× activation a or excitation E per branch)
- **Variables/units:** F_max (N, P032/P033); f_l, f_v dimensionless; l_f (m), v_f (m/s).
- **Interpretation:** length/velocity-scaled muscle force; MVP torque source with MA functions.
- **Source:** F4 § equations; F2/F1 Hill descriptions.
- **Status:** EMPIRICAL form; per-muscle F_max MODEL_DERIVED (small-n fits) or EMPIRICAL (PCSA chain, P026–P029).

## E-11. Minimal-model FL/FV pair (real-time branch) — IMPLEMENTATION ASSUMPTION
- **Equations:** `f_L = exp(−0.5·((L_CE − L_opt)/σ)²)`; `f_v = 1 − v_CE/v_max`; `F_total = E·f_L·f_v·F_max`; `L_MTU = L_CE` (rigid tendon)
- **Variables/units:** lengths (m), velocities (m/s), σ width (m), v_max (m/s).
- **Interpretation:** cheapest stable force law for >500 Hz; valid near-isometric only; no eccentric realism; ~20% Fmax MAE (P060).
- **Source:** F7 § minimal model.
- **Status:** IMPLEMENTATION ASSUMPTION (symmetric-FL, linear-FV, infinite-stiffness choices). σ and v_max per muscle are REQUIRED-BUT-ABSENT in corpus (no values given) — must come from cited-model calibration or new fitting, then validated offline.

## E-12. Moment-arm function form — REQUIRED FORM, COEFFICIENTS ABSENT
- **Equation:** `ma = ∂L_MT/∂θ`; implemented as `ma = f(θ_1..θ_n)` multivariate polynomial (or cubic-Hermite lookup) with C¹ guarantee, validity range, and boundary clamping.
- **Variables/units:** ma (m); θ (rad).
- **Interpretation:** posture-dependent torque conversion; constant-MA error ~35% (P051) forbids constants.
- **Source:** F6 (definition, workflow, validity/clamping/CV requirements).
- **Status:** form + method MODEL-DERIVED/required; COEFFICIENTS UNKNOWN (must be fitted from Holzbaur exports anchored to P038–P048; RMS <0.757% precedent, P-reference F6/Harba).

## E-13. Humeral torsion stress (injury branch only) — EMPIRICAL/MODEL-DERIVED, NOT FOR MVP
- **Equations:** `τ_shear = T·r/J`; `J = π/32·(D⁴−d⁴)`; failure when shear exceeds ultimate (corpus: predicted 50–71 Nm band, 60 MPa peak, 115 mm site).
- **Variables/units:** T torque (Nm); r radius, D/d diameters (m/mm); J polar moment (m⁴); stress (MPa).
- **Interpretation:** distal-third spiral-fracture mechanism (D/d hypothesis).
- **Source:** F4 § injury.
- **Status:** MODEL-DERIVED predictions + EMPIRICAL location corroboration; material E/ν as-used values (P074). DO NOT implement as a damage rule (deferred; needs constitutive validation).

## E-14. Validation metrics — FIRST-PRINCIPLES STATISTICS, corpus-guided use
- **Equations:** RMSE; nRMSE (% of range/mean); Bland-Altman LoA = bias ±1.96·SD; ICC variance-ratio (absolute-agreement); cross-correlation lag; DTW warping distance.
- **Interpretation:** amplitude (RMSE/nRMSE), bias (Bland-Altman), reliability (ICC), timing (x-corr/DTW) decomposition of sim-vs-experiment error.
- **Source:** F5 § metrics; F2 (residual/±2 SD/marker criteria, P083/P084).
- **Status:** FIRST-PRINCIPLES methods; acceptance guides P087 (nRMSE 10–15% band, ICC bands, 5.9–11.2% precedent) are REFERENCE, not universal pass/fail.

## REQUIRED-BUT-ABSENT (do not invent; fit or measure)

1. MA polynomial coefficients + per-function validity ranges (fit per F6 workflow; gate ±2 SD, P084).
2. Per-muscle σ (FL width), v_max, and (reference branch) PEE/SEE/SDE curves + tendon-slack values beyond P032/P033.
3. S(θ_wrist) functional form + R_i values under arm-wrestling postures (measure: instrumented dynamometer; calibrate HM/ABC).
4. μs/μk/vs for skin–skin and skin–table under match loads/moisture (measure: tribometer; system-ID per F3).
5. k_noise per channel; 4CCr/fatigue rate constants for arm muscles; ligament force–length laws + zero-load lengths; cartilage constitutive laws.
6. GH/wrist feasible-ROM stability boundaries; in-competition kinematics/kinetics/EMG (the dataset gap underlying all of the above).

## Explicitly EXCLUDED from simulator equations

- Technique-as-modifier equations (e.g., "top roll ×1.2"): FORBIDDEN — techniques emerge from E-06→E-12 control/activation strategies (F8 control objectives are qualitative targets, not gains).
- Population multiplier equations (e.g., "elite ×1.2"): FORBIDDEN as empirical — Tier2/3 scalings exist only as labeled ASSUMPTIONS (P030/P031) for hypothetical configs with sensitivity analysis.
- Injury-threshold pass/fail rules: EXCLUDED by the validation framework's own design (F5).
