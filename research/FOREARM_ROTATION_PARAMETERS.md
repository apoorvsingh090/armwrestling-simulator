# FOREARM_ROTATION_PARAMETERS — rotation-relevant parameter register

Canonical source remains `parameters.json`. Every row below is traced; readiness
classes match §11 of `FOREARM_ROTATION_SPEC.md`. No new empirical IDs are created
(no measurements exist to register). Scaffold-only quantities (inertia, damping,
restraint stiffness for rotation) are explicitly NOT in the research database and
therefore have NO parameter IDs and NO defaults in code.

| ID | Parameter | Value | Unit | Evidence | Population | Readiness | Notes |
|---|---|---|---|---|---|---|---|
| P010 | forearm_pronation_rom | mean 76, max 80 | deg | EMPIRICAL (cuff, elbow 90°) | GENERAL_HUMAN | READY_WITH_UNCERTAINTY | ACTIVE_ROM; C-03; hard stop +80 (upper end) |
| P011 | forearm_supination_rom | mean 80, max 87 | deg | EMPIRICAL (cuff) | GENERAL_HUMAN | READY_WITH_UNCERTAINTY | ACTIVE_ROM; C-04; hard stop −87 (upper end) |
| P012 | forearm_passive_over_active | 3–5 | deg | EMPIRICAL (laxity lit.) | GENERAL_HUMAN | READY_WITH_UNCERTAINTY | PASSIVE_ROM adder; margin only, no curve |
| P018 | forearm_feasible_rom | −50…+50 | deg | ASSUMPTION (ADL) | GENERAL_HUMAN | ASSUMPTION | +pron/−sup; restraint onset only; measured UNKNOWN |
| P029 | pronator_teres PCSA / Lopt | 1.1 / 5.5 | cm² / cm | EMPIRICAL (cadaveric n=10) | GENERAL_HUMAN | READY (anchors) | Tier1 baseline; single-head-equivalent future use |
| P030 | PT PCSA athletic tier2 | 1.1–1.32 | cm² | ASSUMPTION (+20%) | STRENGTH_TRAINED | ASSUMPTION | research file's own assumption; never default |
| P031 | PT PCSA arm-wrestler tier3 | 1.32–1.65 | cm² | ASSUMPTION (+20–25%) | ARM_WRESTLER | ASSUMPTION | double-extrapolated; hypothetical configs only |
| P040 | PT peak pronation MA | 4.9 | cm | EMPIRICAL (tendon excursion) | GENERAL_HUMAN | READY (anchor) | single sample of ma(elbow, pronation); elbow-coupled |
| P049 | MA coefficient of variation | 10–20 | % | EMPIRICAL (compilation) | GENERAL_HUMAN | READY (principle) | applies to FUTURE fitted rotation coefficients |
| P080 | PT EMG hook tasks | 37.56 | %MVC | EMPIRICAL (sEMG) | ARM_WRESTLER | READY (pattern) | recruitment pattern only; NOT torque |
| P008 | carrying angle (context) | 11–14 | deg | EMPIRICAL | GENERAL_HUMAN | REFERENCE_ONLY | axis-orientation context for full model |
| P009 | flexion-axis varus (context) | 3.1±1.9 | deg | EMPIRICAL (fluoroscopy) | GENERAL_HUMAN | REFERENCE_ONLY | hinge-approximation error documented |
| — | rotation MA functions/coeffs | — | — | — | — | NEEDS_RESEARCH | F6 workflow specified; coefficients absent |
| — | rotation L(φ)/v(φ), tendon, σ/vmax/θ_opt | — | — | — | — | UNKNOWN | absent; interface-only |
| — | supinator + PQ architecture | — | — | — | — | UNKNOWN | named only (F6/F8) |
| — | rotational inertia / damping / restraint k,c | — | — | — | — | UNKNOWN (no ID, no default) | caller-supplied in scaffold; NOT from corpus |

Conventions: neutral-zero φ, +pronation/−supination, SI radians internally
(C-14 resolution). ARM_WRESTLING_MEASURED_ROM: UNKNOWN (C-18).
