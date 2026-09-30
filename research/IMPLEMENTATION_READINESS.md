# IMPLEMENTATION_READINESS — What Can Be Built, and What Must Wait

No graphics. No game-modifier techniques. No simulator code in this spec — only readiness judgments.

---

## READY (build now; research-backed with stated bounds)

- **R-01 Rigid-body dynamics core:** E-01/E-02/E-03 with humerus mass P019 + inertia P020 and
  subject-scaling pipeline (manual + AddBiomechanics-style bilevel; P090 motivates it).
- **R-02 Elbow hinge + restraints:** 1-DOF hinge (0°=extension convention, C-01), anatomical
  0–145° P006, elastic restraint P021, functional placeholder 30–130° P017 (labeled A).
- **R-03 Forearm rotation + wrist 2-DOF:** anatomical bounds P010/P011/P013–P015, passive adder
  P012, obliquity noted P016; task placeholders P018 + flagged wrist subset (C-18/C-20).
- **R-04 Hill reference force law:** E-10 with Fmax P032/P033 and PCSA chain P026–P029 (+CV P049).
- **R-05 ODE activation:** E-08 with P052–P055; EMD-aware sequencing P085.
- **R-06 C1 moment-arm architecture:** E-12 scaffolding (polynomial/Hermite + validity + clamping),
  fitted against anchors P038–P048, gated by ±2 SD P084. (Coefficients arrive from the F6
  workflow — the pipeline is ready, the numbers follow it.)
- **R-07 Inverse-dynamics + Σu² optimization + null-space co-contraction:** E-07 with FSM
  phase scaffolding (hold/ramp/release) and delay/noise toggle (P056–P058, E-09 form).
- **R-08 Validation harness:** metric suite + guides P087, residual gates P083, test template
  (REAL→SIM→METRIC→CRITERION + evidence table), labels Validated/Partially/Unvalidated.
- **R-09 EMG-pattern + smoothness targets:** recruitment ranking P080 (pattern only), MJ band P081,
  isometric norms P082 with mismatch labels.

## READY WITH UNCERTAINTY (build behind flags; ranges + sensitivity mandatory)

- **U-01 Rigid-tendon minimal branch:** E-11 with ~20% Fmax MAE P060; σ/v_max from cited-model
  calibration (absent in corpus — log source); cross-checked offline vs reference branch.
- **U-02 Excitation-bypass fallback:** C-10 branch; document transient/fatigue loss; hardware-specific
  +9.6 Hz is reference only.
- **U-03 Contact/friction placeholders:** Stribeck form E-05 with bands P061–P067 (all flagged A/U);
  3 patches P068–P070; R_i P072; S(θ) with −30% magnitude P073 but assumed shape; grip scales P071.
- **U-04 Population presets:** general male/female grip scales + CV perturbation; Tier2/3 chains
  P030/P031 for hypothetical configs only, never defaults.
- **U-05 Bone/ligament context values:** E/ν P074, strengths P078/P079 as restraint/injury-branch
  context — not damage criteria.
- **U-06 Shoulder 3-DOF with task envelope UNKNOWN:** anatomical bounds P001–P005; start posture
  P088 as scenario context; stability-limited motion flagged (D-10).

## NEEDS MORE RESEARCH (scaffold interfaces now; values later)

- **N-01 Fitted MA coefficients** (F6 workflow + D-01 postures).
- **N-02 Measured Stribeck laws** for both interfaces (D-02).
- **N-03 Patch-resolved grip distribution + S(θ) law** (D-03).
- **N-04 Arm-muscle tendon/MTU dynamics** incl. slack, compliance, dynamic pennation (D-05).
- **N-05 Fatigue rate/recovery constants** (D-09).
- **N-06 Stability envelopes** GH/wrist + scapular rhythm (D-10).
- **N-07 Control gains/coordination/k_noise fits** (D-08).
- **N-08 Population distributions** for individualisation (D-12).

## DO NOT IMPLEMENT YET (explicitly forbidden until evidence exists)

- **X-01 Injury/fracture prediction or damage rules** (FE band P075/P076, location P077 stay REFERENCE_ONLY; D-07).
- **X-02 Technique force/torque/success modifiers** of any kind (F8 objectives are control targets; §16 hard rule).
- **X-03 Elite population multipliers as defaults** (P030/P031 hypothetical-only).
- **X-04 Phone-derived joint kinematics** as validation data (P086 exclusion).
- **X-05 MPC/RL/online learning controllers** (D-14; RL excluded phase 1).
- **X-06 Ligament/cartilage failure, tendon-energy tactics, lower-body drive, second competitor
  beyond patch-wrench I/O** (D-06/D-07/D-11 + §21).

---

## Smallest scientifically defensible MVP (no graphics)

**One arm (thorax-fixed) → skeletal segments (P019/P020) → elbow 1-DOF hinge (R-02) →
biceps/triceps force sources (P026/P027/P032 + P038/P041 anchors) → ODE activation (R-05) →
Hill force E-10 → posture-dependent C1 MA (R-06; single-DOF polynomials first, coefficients
from F6 workflow) → joint torque E-03 → Euler dynamics E-01/E-02 → validation harness (R-08)
checking residuals (P083), MA ±2 SD (P084), EMG pattern (P080), and MJ band (P081).**

Scope locks: rigid-tendon + ODE-activation defaults (U-01 logged, U-02 available as fallback);
FSM limited to ramp→hold→release isometric scenario at 45°-start-like posture (P088 context);
contact module present only as flagged placeholders (U-03) driving a single-hand force input —
no slip-outcome or match-result claims. Uncertainty: CV perturbation (P049) + slack sensitivity
(P089 motivation) on every reported torque. Anything outside this thread (shoulder-driven attacks,
wrist-coupled gripping, fatigue, injury, techniques-as-behavior) is scaffolded, not claimed.

## MVP acceptance (all must pass for "Partially Validated" holding-phase claim)

1. Residuals within P083 on isometric-hold scenarios.
2. Fitted elbow MA functions within ±2 SD of P038/P041 anchors across 5–140° (P084).
3. Simulated recruitment order matches P080 pattern (PT > brachioradialis > biceps %MVC ranking).
4. MJ within P081 band for ramp–hold transitions.
5. Torque output distribution (CV + slack sweep) reported, never a point torque.
6. Every number traceable to P### + source file + reference; every assumption labeled; no
   technique/population modifiers present in code or config.
