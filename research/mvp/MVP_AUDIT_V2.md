# MVP_AUDIT_V2 — rigorous audit of the single-arm elbow MVP

Scope: ONLY the existing implementation in `mvp/` (no new subsystems added).
Spec authorities: `MASTER_BIOMECHANICS_SPEC.md`, `parameters.json`, `equations.md`,
`research_conflicts.md`, `IMPLEMENTATION_READINESS.md`, `IMPLEMENTATION_STATUS.md`.
Baseline scenario (80°, u_bic=0.8/u_tri=0.2, 3 s → 140.21°) is a NUMERICAL
BEHAVIOUR DEMONSTRATION ONLY — never cited below as validation data.

Corrections applied during this audit (all first-principles / accuracy, zero
recalibration — scenario output bit-identical at 140.21°):
- C1: moment-arm docstring "within 0.5%" → measured 1.34% (documentation accuracy).
- C2: `MomentArmModel` ABC added; `MomentArmProvisional` subclasses it; simulation
  depends on the interface (AUDIT 2 recommendation, proven by substitution test).
- C3: inelastic hard-stop velocity projection (AUDIT 6 latent bug), +3 tests.
  Suite: 12/12 pass (9 original + 3 audit).

---

## AUDIT 1 — TRACEABILITY (every runtime numerical parameter)

"Validated?" = NO for every row: no sport-specific dataset exists (D-01); nothing
below has passed a validation gate. Component precedents (P060, fitting RMS) are
not validations of these values.

| Runtime value | Source ID | Evidence type | Status | Validated? | Units |
|---|---|---|---|---|---|
| anat. limits 0 / 145° | P006 | EMPIRICAL_MEASUREMENT | EMPIRICAL | NO | deg→rad (SI) |
| feasible 30 / 130° | P017 | ASSUMPTION | ASSUMPTION | NO | deg→rad |
| biceps PCSA 4.6 cm², Lopt 0.232 m | P026 | EMPIRICAL_MEASUREMENT | EMPIRICAL | NO | m² / m (SI) |
| triceps PCSA 10.3 cm², Lopt 0.454 m | P027 | EMPIRICAL_MEASUREMENT | EMPIRICAL | NO | m² / m (as-written, flagged long) |
| biceps peak MA 0.047 m | P038 | EMPIRICAL_MEASUREMENT | EMPIRICAL (anchor only) | NO | m (SI) |
| triceps peak MA 0.023 m | P041 | EMPIRICAL_MEASUREMENT | EMPIRICAL (anchor only) | NO | m |
| tau_a 0.03 (range 0.01–0.05) | P052 | EMPIRICAL_MEASUREMENT | EMPIRICAL | NO | s |
| tau_d 0.04 | P053 | EMPIRICAL_MEASUREMENT | EMPIRICAL | NO | s |
| beta 0.5 (range 0.1–1.0) | P054 | MODEL_DERIVED | MODEL_DERIVED | NO | — |
| q0 0.01 (range 0.001–0.05) | P055 | MODEL_DERIVED | MODEL_DERIVED | NO | — |
| P021 as-written 100 / 0.001745 | P021 | MODEL_DERIVED | MODEL_DERIVED (DB only, NOT integrated) | NO | Nm/deg, Nms/deg |
| sigma 50 (→Fmax 230/515 N) | PROV-01 | (absent #2) | PROVISIONAL | NO | N/cm² |
| FL width 0.30·Lopt | PROV-02 | (absent #2) | PROVISIONAL | NO | m |
| v_max 10·Lopt/s (2.32 / 4.54) | PROV-03 | (absent #2) | PROVISIONAL | NO | m/s |
| theta_opt 90° | PROV-04 | (absent) | PROVISIONAL | NO | rad |
| MA shape coeffs (0.65/0.35; 0.70/0.30/0.3) | PROV-05 detail | — | IMPLEMENTATION ASSUMPTION | NO | — (dimensionless shape) |
| inertia 0.06 | PROV-06 | — | PROVISIONAL | NO | kg·m² |
| forearm mass 1.5 / COM 0.18 | PROV-07 | — | PROVISIONAL | NO | kg / m |
| joint damping 0.3 | PROV-08 | — | PROVISIONAL (NOT P059) | NO | Nm·s/rad |
| restraint k 15 / c 1.0 | PROV-09 | — | PROVISIONAL (surrogate for P021) | NO | Nm/rad, Nms/rad |
| g 9.80665 | FIRST-PRINCIPLES | FIRST-PRINCIPLES | constant | n/a | m/s² |
| FV clamp [0, 1.5]; q clamp [0,1] | — | — | IMPLEMENTATION ASSUMPTION (bounds) | NO | — |
| dt 0.001; excitations 0.8/0.2; theta0 80° | — | — | NUMERICAL CHOICE / SCENARIO INPUT (not biomechanics) | n/a | s / — / rad |

Untraced-to-DB runtime numbers (all declared ASSUMPTION/PROVISIONAL, none silent):
MA shape coefficients, FV clamp bounds, gravity-geometry choice, integrator choice.
No strength/technique/elite multiplier exists anywhere (verified by grep-equivalent
review of muscle.py/dynamics.py/simulation.py).

## AUDIT 2 — MOMENT ARM (C1 provisional layer)

- Anchors (empirical, peak values only, angles NOT given): P038 4.7 cm, P041 2.3 cm.
- Form: MA_bic = 0.047·(0.65+0.35·sin θ); MA_tri = 0.023·(0.70+0.30·sin(θ+0.3)).
- Units: m in / m out. Convention: clinical 0 = extension, flexion+, radians.
- Valid domain 5–140° (F6 grid); `is_extrapolated()` flags outside; evaluation
  continues (flag-only — trace has no flag column yet; see §7).
- Derivatives: C∞ (sin-based). Measured max|dMA/dθ| bic = 0.0164 m/rad;
  finite-difference C1 check passes at 20/80/130°; max|d²| bounded (0.0164).
- Artificial extrema: YES, by construction — biceps peak placed exactly at 90°
  (peak ANGLE is assumed; corpus gives values, not angles); triceps peaks at
  72.8° with exactly the anchor value, evaluating 1.34% below peak at 90°
  (docstring corrected from "0.5%"). No other extrema on 0–145°.
- NOT empirically validated (stated in module docstring + model_status.md).
- Replacement interface IMPLEMENTED (`MomentArmModel` ABC: biceps/triceps/
  is_extrapolated): substitution proven by `test_moment_arm_interface_substitution`
  (constant-stub runs unmodified dynamics). Future lookup / interpolated /
  fitted E-12 implementations subclass the ABC — no muscle/joint/dynamics edits.

## AUDIT 3 — MUSCLE LENGTH

- L(θ) = Lopt + MA_peak·(θ_opt−θ): PROVISIONAL LINEAR GEOMETRY SURROGATE.
  Status NOT upgraded by this audit.
- Dimensional check: m + m·(rad−rad) = m ✓ (radian dimensionless).
  vCE = ±MA·ω: m·rad/s = m/s ✓. F: a[—]·N·[—]·[—] = N ✓.
  τ = m·N = Nm ✓. α = Nm/(kg·m²) = rad/s² ✓.
- E-12 inconsistency (documented, deferred): E-12 defines ma = ∂L/∂θ, but L uses
  constant MA_peak while torque uses MA(θ). Estimated effect: at full extension
  fL_lin ≈ 0.570 vs fL_integrated ≈ 0.652 (~14% relative force difference at the
  extreme; ~0% at θ_opt; small mid-range). Consistent coupling requires injecting
  the MA model into length computation — listed as required correction R2 (§7),
  NOT applied here (would change numerics without research-backed shape).

## AUDIT 4 — MUSCLE FORCE (F = a·Fmax·fL·fv)

- Activation bounds: simulation passes ODE-clamped q∈[0,1]; `force()` itself does
  not clamp out-of-range input (API note, not a runtime path — §6).
- FL: Gaussian, max exactly 1 at Lopt, symmetric falloff, <0.05 at 5σ ✓.
- FV: 1−v/vmax; concentric (v>0) reduces ✓; v≥vmax clamps 0 ✓;
  lengthening gives >1 clamped at 1.5 (NO eccentric realism — matches F7 minimal
  scope; 1.5 bound is assumption, corpus-silent).
- Sign convention: vCE_bic = +MA·ω (flexion shortens biceps ✓);
  vCE_tri = −MA·ω (flexion lengthens triceps ✓). Verified by torque-direction test.
- Units N ✓; plausible magnitudes (peak isometric bic ≈ 230·fL N).
- Stability: exp() bounded; no division by zero (vmax, σ>0 enforced by construction).
- Silently assumed: NONE — Gaussian symmetry (E-11 as specified), clamp bounds,
  single-head equivalents, and missing-heads UNKNOWN are all documented in
  muscle.py docstring + model_status.md.

## AUDIT 5 — ACTIVATION (Zajac E-08)

- Input clamp [0,1] ✓, state clamp [0,1] ✓, tau selected on clamped values ✓.
- Constants: tau_a P052 range default 0.03; tau_d P053 0.04; beta P054 0.5;
  q0 P055 0.01 — all within corpus ranges.
- Equilibrium (closed form, beta term): q* = (u/τ+βq0)/(1/τ+β):
  u=1 → q*≈0.985 (NOT 1.0 — property of the stated E-08 equation, not a bug);
  u=0 → q*≈0.0002. Tests consistent (saturate >0.95, rest ≤0.05).
- Timestep: explicit Euler, dt/τ ≤ 0.067 even at dt=2 ms — stable, verified by
  sweep (activation contributes no divergence at any tested dt).
- Deterministic, no randomness ✓ (repeatability test passes).

## AUDIT 6 — JOINT DYNAMICS (τ = muscle + gravity + restraint − damping; α = τ/I)

- Signs: biceps +flexion, triceps −, gravity −mgd·sinθ, restraint opposes
  violation, damping opposes velocity ✓ (direction tests).
- Convention/units: radians throughout (DEG2RAD at definition; degree-input guard
  in length path); I kg·m², c/k Nm·s(rad)/Nm/rad, gravity kg·m/s²·m = Nm ✓.
- Gravity geometry: upper arm fixed vertical-down; τ=0 hanging, max at 90° ✓
  for the STATED geometry (assumption, documented).
- Boundary: anatomical hard clamp + feasible soft restraint. LATENT BUG FOUND AND
  FIXED (C3): pre-fix probe showed the joint pinned at 0°/145° while retaining
  steady outward velocity (−0.77/+2.40 rad/s) — unphysical motion-into-wall state
  that position-only clamping hides. Fix: inelastic projection (zero outward
  normal velocity at hard stops, restitution 0 — no bounce invented). Post-fix:
  pinned states carry ω=0; baseline scenario unaffected (never reaches hard stops).

## AUDIT 7 — P021 (exact treatment)

- Original: elbow restraint peak stiffness 100 Nm/deg + damping 0.001745 Nm·s/deg
  (Holzbaur via Rankin; MODEL_DERIVED, fitted elastic restraint).
- Converted: 100×57.2958 = 5729.6 Nm/rad; 0.001745×57.2958 = 0.10 Nms/rad.
- Meaning: peak of a fitted nonlinear limit-restraint, not a linear working stiffness.
- Not used directly because: (a) 1° of violation → 100 Nm exceeds max voluntary
  elbow torque (~68 Nm implied by P082), i.e. implausible as a linear law;
  (b) it would dominate all muscle torques (~8 Nm) and reduce the MVP to a
  restraint demonstration. Surrogate PROV-09 (15/1.0) is an IMPLEMENTATION
  ASSUMPTION, never presented as empirical (parameters.py + model_status.md +
  joint.py docstring all state the deviation). Original retained in DB ✓.

## AUDIT 8 — NUMERICAL VALIDATION (dt 2 / 1 / 0.5 / 0.25 ms, 3 s scenario)

Reference 0.25 ms; common-grid pointwise maxima:

| dt | max\|Δθ\| | max\|Δω\| | max\|Δτ\| | where | pre-restraint max\|Δθ\| / max\|Δω\| | final θ |
|---|---|---|---|---|---|---|
| 2 ms | 0.775° | 0.139 rad/s | 6.08 Nm | all maxima at t≈0.273–0.274 s = RESTRAINT ENGAGEMENT (baseline crosses 130° at t=0.274 s) | 0.769° / 0.0558 | 140.212° |
| 1 ms | 0.358° | 0.090 rad/s | 6.00 Nm | same localization | 0.355° / 0.0260 | 140.212° |
| 0.5 ms | 0.148° | 0.025 rad/s | 0.055 Nm (at t=0.0003 s, activation transient) | engagement | 0.147° / 0.0114 | 140.212° |

Interpretation (not PASS/FAIL): smooth-phase convergence is clean first-order
(diffs ≈ halve with dt); all grids agree on final state to 0.001°. The ~6 Nm
pointwise torque diffs are engagement-transient artifacts: the piecewise restraint
(including impact-damping −c·ω ≈ −5.9 Nm on first contact, a PROV-09 property)
switches one step apart between grids — expected for explicit switching, not
instability. Production dt=1 ms is stable with smooth-phase error ≈0.36° vs
0.25 ms. No blow-up at any dt.

## AUDIT 9 — PARAMETER SENSITIVITY (OAT −20% / base / +20%; final θ, peak\|ω\|)

Baseline: final 140.212°, peak\|ω\| 5.960 rad/s. (Scenario saturates against the
feasible restraint, so final θ largely reports restraint equilibrium — stated,
not hidden; peak ω carries the muscle/dynamic sensitivity.)

| Param (±20%) | −20% (final, peak) | base | +20% (final, peak) |
|---|---|---|---|
| Fmax (σ) | 137.08°, 4.472 | 140.21°, 5.960 | 143.08°, 7.179 |
| sigma_FL | 138.34°, 5.745 | same | 141.41°, 6.078 |
| v_max | 140.21°, 5.681 | same | 140.21°, 6.153 |
| MA amplitude | 137.08°, 4.647 | same | 143.08°, 6.901 |
| MA shape (var. part) | 140.54°, 5.967 | same | 139.89°, 5.953 |
| inertia | 140.21°, 6.241 | same | 140.21°, 5.712 |
| damping | 140.21°, 6.391 | same | 140.21°, 5.552 |
| restraint k | 142.45°, 5.960 | same | 138.66°, 5.960 |

Reading (sensitivity, NOT calibration — no values selected or changed):
most influential on peak velocity: Fmax and MA amplitude (±20% → ∓25%/+20% peak ω);
inertia/damping move peak ω ∓5–7%; v_max moves peak ω ±4–5% with final θ fixed
(scenario is FL/activation-dominated, brief high-velocity phase); MA shape as
defined (peak-preserving) is negligible by construction; restraint k moves final
θ ±2° with zero peak-ω effect (engagement occurs after the velocity peak).
Scripts: `audits/audit_v2_numbers.py`, `audit_v2_dt_detail.py`,
`audit_v2_probe.py`, `audit_v2_stop_probe.py` (re-runnable).

## AUDIT 10 — VERDICT

1. Verified: activation ODE behavior; FL/FV shapes; torque directions/signs;
   unit/dimensional consistency of every term; restraint directionality;
   determinism (bit-identical); dt stability 0.25–2 ms with first-order smooth
   convergence; P021 handling; no hidden multipliers (code-reviewed).
2. Internally consistent: SI + clinical convention enforced (incl. input guard);
   E-02/E-03/E-08/E-10/E-11 forms as specified; MA C1 smooth, positive, 35%
   variation (P050-compliant); gravity/restraint/damping signs and units cohere.
   Exception: E-12 length coupling (see 4/7).
3. Numerically sensitive: peak ω most sensitive to Fmax and MA amplitude
   (both PROVISIONAL chains) — the two quantities the corpus does NOT provide
   (absent #1/#2). This correctly blocks any VALIDATED torque claim.
4. Provisional: PROV-01…09 (sigma, FL width, vmax, theta_opt, MA shape, inertia,
   mass/COM, damping, restraint surrogate) + linear length surrogate — all labeled.
5. Unsupported: ARM_WRESTLING_MEASURED_ROM, MA coefficients, friction/contact,
   fatigue, EMG patterns, technique/elite multipliers — none implemented ✓ (req. 10).
6. Potential bugs: (a) FIXED — hard-stop velocity retention; (b) FIXED — 0.5% doc
   inaccuracy; (c) noted — `force()` accepts unclamped activation (unreachable at
   runtime; hardening deferred, §7 R3); (d) noted — trace lacks extrapolation flag.
7. Required corrections:
   - R0 DONE (C1–C3 + 3 tests; scenario output unchanged at 140.21°).
   - R1 (before contact work): add `extrapolated` column/flag to trace outputs.
   - R2 (before torque-credibility claims): MA-consistent fiber length via the
     ABC interface (E-12), validated against the ±2 SD gate once fitted MAs exist.
   - R3 (minor): clamp-or-raise on `force()` activation input.
   - FORBIDDEN: retuning provisionals to "look right" (would be calibration).
8. Ready for next subsystem? YES — conditionally: (i) provisionals stay labeled
   and swept, never defaults-as-truth; (ii) MA replacement goes through
   `MomentArmModel`; (iii) R1/R2 ride with the next subsystem that needs them;
   (iv) scenario output is never cited as validation; (v) VALIDATED status remains
   unreachable before D-01 data. Foundation is internally correct; its uncertainty
   is where the corpus says it should be.

## ADDENDUM � forearm rotation subsystem (references only; no prior content altered)

- Spec: research/FOREARM_ROTATION_SPEC.md (��1�12) � parameters: research/FOREARM_ROTATION_PARAMETERS.md � build status: research/FOREARM_ROTATION_IMPLEMENTATION_STATUS.md.
- Decision: interface + kinematic scaffold ONLY (one discrete MA anchor P040, zero MA functions/geometry/supinator numbers ? nothing numerical manufactured).
- Code: mvp/biomech/forearm.py (RotationActuator ABC with elbow_theta coupling channel; joint +80/-87 deg P010/P011; dynamics with caller-supplied I/c, gravity 0); mvp/tests/test_forearm.py 10/10.
- Elbow cross-check: 12/12 prior tests pass; scenario still 140.21 deg; only elbow edits are unit-guard order hardenings (valid-input behavior identical).
- Open items carried: R1/R2 (unchanged) + rotation R-series in the rotation implementation status (extrapolation flag, MA-consistent length, fitted 2-D MA, inertia/damping measurement, D-01 sport kinetics).

