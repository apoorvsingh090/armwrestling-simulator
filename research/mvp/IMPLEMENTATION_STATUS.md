# IMPLEMENTATION_STATUS — single-arm elbow MVP

## What was implemented (`mvp/`, pure Python, no Unity)
- Fixed thorax + fixed upper arm → 1-DOF elbow hinge (clinical 0 = full extension).
- Biceps and Triceps as separate `Muscle` objects; force ONLY from
  F = a·Fmax·fL·fv (no strength/technique/elite multipliers anywhere).
- Zajac ODE activation (E-08, tau_a=0.03 / tau_d=0.04 / beta=0.5 / q0=0.01).
- Rigid-tendon minimal Hill branch (E-10/E-11, C-09 branch A).
- Provisional C1 sin-based MA interpolation anchored at P038/P041 peaks,
  validity 5..140 deg, extrapolation flagged (NOT validated — see below).
- Single-hinge Euler dynamics (E-02/E-03): tau = MA_b·F_b − MA_t·F_t +
  gravity + restraint − c·omega; semi-implicit Euler, fixed dt=1 ms.
- Clean separation: anatomical angle / MT state (L, vCE) / activation /
  force / torque / joint state (theta, omega, alpha).
- Headless scenario `scenarios/run_headless.py`: 80 deg start, u_bic=0.8,
  u_tri=0.2, 3 s → `outputs/mvp_trace.csv` (11 required columns, SI).
- Plots `scenarios/plot_results.py` → angle/omega/force/torque PNGs.
- 9 automated tests in `tests/test_mvp.py` (all pass, see below).
- `model_status.md` with EMPIRICAL / MODEL_DERIVED / PROVISIONAL /
  ASSUMPTION / UNKNOWN table.

## Provisional parameters (must be sensitivity-swept, never cited as measured)
- PROV-01 sigma 50 N/cm² → Fmax bic 230 N / tri 515 N (corpus absent #2).
- PROV-02 sigma_FL 0.30·Lopt; PROV-03 v_max 10·Lopt/s; PROV-04 theta_opt 90 deg.
- PROV-05 MA shape (anchors empirical, shape NOT validated).
- PROV-06 inertia 0.06 kg·m²; PROV-07 mass 1.5 kg / COM 0.18 m;
  PROV-08 damping 0.3 Nms/rad; PROV-09 restraint 15 Nm/rad / 1.0 Nms/rad.
- Length law L = Lopt + MA_peak·(theta_opt − theta) (linear surrogate).

## Assumptions made (all labeled in code + model_status.md)
- Thorax/upper-arm fixed; pure hinge (varus 3.1°, carrying angle, translation deferred).
- Feasible 30..130 deg (P017 ADL placeholder) = soft-restraint onset only.
- P021 as-written (100 Nm/deg) preserved in DB but NOT integrated directly
  (5729 Nm/rad intractable at 1 kHz); stable surrogate PROV-09 used instead.
- P059 (2.5 Ns/m linear) NOT reused (different quantity/units).
- Each muscle = long head only; missing heads UNKNOWN.
- Gravity geometry: upper arm vertical-down, forearm rotates in vertical plane.

## Tests: 9 passed, 0 failed (`python -m pytest tests -q`)
- test_activation_dynamics — PASS (tau_a ~63% at 30 ms, saturates, decays, rests in q0 band)
- test_force_length_behaviour — PASS (peaks at Lopt, falls off, ~0 at 5σ)
- test_force_velocity_behaviour — PASS (concentric < isometric, clamp at vmax, eccentric > iso clamped 1.5x)
- test_moment_arm_interpolation — PASS (biceps anchor exact at 90°, C1 smooth, ~35% variation, extrapolation flags)
- test_torque_direction — PASS (biceps +, triceps −)
- test_elbow_limits — PASS (clamp + restraint direction + mid-band zero)
- test_deterministic_repeatability — PASS (bit-identical reruns)
- test_timestep_sensitivity — PASS (dt 1 ms vs 0.5 ms converge < 2 deg over 2 s)
- test_dimensional_unit_consistency — PASS (Fmax arithmetic, Nm plausibility, rad/s², degree-input rejection)

## Scenario result (reference, NOT validation)
- 80 deg → settles ~140.2 deg against feasible-restraint/gravity with
  omega → 0; biceps (0.8) overcomes triceps (0.2) + gravity, as expected from
  Fmax·MA arithmetic. CSV 3001 rows; 4 PNGs in `outputs/`.

## Research blockers remaining (from corpus; cap = Partially Validated at best)
- D-01 in-competition kinematics/kinetics/EMG dataset — no sport-specific validation possible.
- Fitted MA coefficients per F6 workflow (E-12 absent #1); current interp. is placeholder.
- Per-muscle sigma_FL, v_max, SEE/PEE/slack beyond P032/P033 (absent #2).
- Target-interface friction laws (D-02), grip/S(θ) (D-03) — contact NOT implemented.
- Fatigue rates (D-09), k_noise/gains/coordination (D-08), GH/wrist envelopes (D-10).
- Forearm+hand inertia/mass/COM (no corpus values — provisional PROV-06/07).
- Residual gates P083 are gait-derived (C-22); MA ±2 SD gate P084 applies to
  fitted functions, not the provisional interpolation.

## Do-not-proceed gates (req. 16 — all respected)
Hand contact, table mechanics, opponent, techniques, fatigue, AI, Unity: NOT
started. No arm-wrestling ROM, friction, competition kinematics, fatigue rates,
EMG patterns, technique/elite multipliers invented (req. 10). No graphics beyond
headless matplotlib diagnostics (req. 14).
