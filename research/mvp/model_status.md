# Model-status report — MVP single-arm elbow

Authoritative spec: `parameters.json`, `equations.md`,
`MASTER_BIOMECHANICS_SPEC.md`, `IMPLEMENTATION_READINESS.md`,
`research_conflicts.md` in `C:\Users\Apoorv\Downloads\research\`.

## EMPIRICAL (directly from corpus measurements)
- Elbow anatomical ROM 0..145 deg, clinical 0 = full extension (P006).
- Biceps long-head PCSA 4.6 cm², Lopt 23.2 cm (P026, cadaveric n=10).
- Triceps long-head PCSA 10.3 cm², Lopt 45.4 cm (P027, preserved as-written; flagged long).
- Biceps peak MA 4.7 cm, triceps peak MA 2.3 cm (P038/P041, peak anchors only).
- Activation taus: tau_a 0.01..0.05 s, tau_d 0.04 s (P052/P053).
- MA variation >=30% over ROM mandates angle-dependent MA (P050).
- Rigid-body forms E-01/E-02/E-03, Hill form E-10, Zajac ODE E-08, minimal FL/FV E-11 form.

## MODEL_DERIVED (fitted/computed from research inputs)
- Zajac beta 0.5 (range 0.1..1.0, P054), q0 0.01 (range 0.001..0.05, P055).
- P021 restraint values as-written (100 Nm/deg); preserved in DB, NOT used directly.
- Humerus mass/inertia P019/P020 documented; NOT consumed by single-hinge MVP
  (forearm inertia is provisional instead — see below).

## PROVISIONAL (clearly marked; NOT validated; sensitivity required)
- PROV-01 specific tension 50 N/cm² → Fmax bic 230 N / tri 515 N.
- PROV-02 FL width 0.30·Lopt. PROV-03 v_max 10·Lopt/s.
- PROV-04 theta_opt 90 deg (angle of Lopt).
- PROV-05 MA sin-interpolation shape; anchors empirical, shape NOT validated;
  validity 5..140 deg, evaluation outside flagged EXTRAPOLATED.
- PROV-06 forearm+hand inertia 0.06 kg·m² about elbow.
- PROV-07 forearm mass 1.5 kg / COM 0.18 m (gravity torque only).
- PROV-08 joint damping 0.3 Nms/rad (NOT P059).
- PROV-09 restraint k=15 Nm/rad / c=1.0 Nms/rad (stable surrogate for P021).
- Muscle length law L = Lopt + MA_peak·(theta_opt − theta) (linear surrogate).

## ASSUMPTION (implementation choices, labeled)
- Thorax + upper arm fixed; single 1-DOF pure hinge (varus/carrying/translation deferred).
- Feasible placeholder 30..130 deg (P017, ADL-derived) as soft-restraint onset;
  never reported as measured.
- Semi-implicit Euler at 1 kHz; rigid tendon L_MTU = L_CE (C-09 branch A).
- ODE-activation default; excitation-bypass available only as fallback (C-10).
- Each muscle object = named long head only (missing heads UNKNOWN, not invented).

## UNKNOWN (corpus does not establish; NOT implemented)
- ARM_WRESTLING_MEASURED_ROM for every joint (C-18).
- Continuous MA polynomial coefficients (E-12 absent #1; F6 workflow pending).
- Per-muscle sigma_FL, v_max, SEE/PEE curves, slack beyond P032/P033.
- Friction coefficients, competition kinematics, fatigue rates, EMG patterns,
  technique multipliers, elite multipliers (req. 10 — all excluded).
- Subject-specific geometry, GH/wrist stability envelopes, ligament laws.

## Full parameter table
| ID | Parameter | Value | Status | Notes |
|---|---|---|---|---|
| P006 | elbow_flexion_rom_aaos | 0..145 deg | EMPIRICAL | ACTIVE_ROM general human. Anatomical hard stops. |
| P017 | elbow_feasible_rom_placeholder | 30..130 deg | ASSUMPTION | ADL-derived placeholder. ARM_WRESTLING_MEASURED_ROM UNKNOWN. |
| P026 | biceps_long_head PCSA / Lopt | 4.6 cm^2 / 23.2 cm | EMPIRICAL | Cadaveric n=10. Long head only. |
| P027 | triceps_long_head PCSA / Lopt | 10.3 cm^2 / 45.4 cm | EMPIRICAL | Preserved as-written; 45.4 cm unusually long, flagged not corrected. |
| P038 | biceps peak flexion MA | 4.7 cm | EMPIRICAL | Peak anchor only. |
| P041 | triceps peak extension MA | 2.3 cm | EMPIRICAL | Peak anchor only. |
| P052/P053 | tau_a / tau_d | 0.01..0.05 / 0.04 s | EMPIRICAL | Defaults tau_a=0.03, tau_d=0.04. |
| P054/P055 | beta / q0 | 0.1..1.0 / 0.001..0.05 | MODEL_DERIVED | Zajac-form params. Defaults 0.5 / 0.01. |
| P050 | MA variation over ROM | >=30% | EMPIRICAL | Mandates angle-dependent MA; forbids constants. |
| P021 | elbow restraint 100 Nm/deg | 100 Nm/deg + 0.001745 Nms/deg | MODEL_DERIVED | In DB as-written; NOT used directly (intractable). MVP k=15 Nm/rad PROVISIONAL. |
| PROV-01 | specific tension sigma | 50 N/cm^2 | PROVISIONAL | NOT from corpus (absent #2). Gives Fmax bic=230 N, tri=515 N. |
| PROV-02 | FL width sigma_FL | 0.30*Lopt | PROVISIONAL | Corpus absent. |
| PROV-03 | v_max | 10*Lopt/s | PROVISIONAL | Corpus absent. |
| PROV-04 | theta_opt (L=Lopt angle) | 90 deg | PROVISIONAL | Corpus absent. |
| PROV-05 | MA shape (interp. layer) | sin-based C1 | PROVISIONAL | Anchors empirical; shape NOT validated. |
| PROV-06 | forearm+hand inertia about elbow | 0.06 kg*m^2 | PROVISIONAL | NOT from corpus. Blocks VALIDATED claim. |
| PROV-07 | forearm mass / COM | 1.5 kg / 0.18 m | PROVISIONAL | Gravity torque only. |
| PROV-08 | joint damping c | 0.3 Nms/rad | PROVISIONAL | NOT P059 (different quantity). |
| PROV-09 | restraint k/c (used) | 15 Nm/rad / 1.0 Nms/rad | PROVISIONAL | Stable surrogate for P021. |
| UNK-01 | ARM_WRESTLING_MEASURED_ROM | none | UNKNOWN | No in-competition goniometry (C-18). |
| UNK-02 | MA polynomial coefficients | none | UNKNOWN | Must be fitted per F6 workflow (E-12). |
| UNK-03 | fatigue rates / EMG patterns / friction / elite multipliers | none | UNKNOWN | Explicitly NOT implemented (req. 10). |
