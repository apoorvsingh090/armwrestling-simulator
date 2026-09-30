# Research Conflicts — Arm-Wrestling Corpus

Rule followed: no winner is chosen because a value "looks reasonable".
Where evidence is insufficient the handling is UNKNOWN.
Severity: HIGH = blocks or redirects implementation; MED = changes ranges/handling; LOW = bookkeeping.

---

## C-01. Elbow zero / angle convention — HIGH
- **Parameter:** elbow flexion/extension zero.
- **Source A (F4):** full extension = 0°, flexion positive to ~130–154° (AAOS/clinical convention).
- **Source B (F7):** zero = 90° of elbow flexion (ISB/JCS exposition as written in F7).
- **Population/method/quality:** A = clinical goniometry norm, high for reporting; B = standards-text exposition, medium (wording may conflate JCS zero with a mid-range reference; no arm-wrestling measurement decides it).
- **Possible reason:** different conventions (clinical vs ISB-text description); possible imprecise wording in F7.
- **Handling:** UNKNOWN until a single convention is adopted. RECOMMENDATION (convention, not empirical claim): adopt clinical 0°=full-extension convention for all simulator I/O and document the transform to any ISB internal frame. Do not mix F4 tables with F7 zero text without conversion.

## C-02. Elbow flexion anatomical maximum — MED
- **A (F4 text):** 130–154° active (passive slightly beyond).
- **B (F4 table, F7):** 0–145° (AAOS).
- **C (F6 grid):** export range 5–140°.
- **Population/method:** general-human goniometry vs AAOS norm vs modeling grid limit. Quality medium–high; no arm-wrestler sample.
- **Reason:** active vs passive vs norm vs computational clipping; population/method mix.
- **Handling:** IMPLEMENT_WITH_RANGE. Use 0–145° as anatomical reference; clamp model-generated MA functions to measured/grid validity (5–140° for F6-derived polynomials). Task ROM narrower (see C-18).

## C-03. Forearm pronation range — MED
- **A (F4 cuff device):** mean ~76° pronation.
- **B (F4 table):** 0–80° pronation (elbow 90°).
- **C (F7):** 80° pronation.
- **Population/method:** general adults; cuff (more reliable per F4) vs goniometer norms. Quality medium.
- **Reason:** device/method + elbow-posture differences; F4 itself notes goniometer −50/+50 wider/looser protocol.
- **Handling:** IMPLEMENT_WITH_RANGE 76–80° anatomical; task-feasible 50° (C-18). Mark method dependence.

## C-04. Forearm supination range — MED
- **A (F4 cuff):** mean ~80°. **B (F4 table):** 0–87°. **C (F7):** 85°.
- Same population/method/quality notes as C-03.
- **Handling:** IMPLEMENT_WITH_RANGE 80–87° anatomical; task-feasible 50°.

## C-05. Glenohumeral ROM headline numbers — MED
- **A (F4):** flex 0–170 / ext 0–30 / abd 0–170 / ER 0–90 / IR 0–80 (active, position-dependent).
- **B (F7):** ~180 flex/ext, 90 abd/add, 90 IR/ER (generic anatomical summary).
- **Quality:** A higher (conditioned measurements); B lower (unconditioned summary).
- **Reason:** measurement posture conditioning vs generic summary.
- **Handling:** REFERENCE_ONLY for B; IMPLEMENT_WITH_RANGE using A with posture conditions. GH feasible ROM for arm wrestling is UNKNOWN in both (see C-18).

## C-06. Brachioradialis PCSA — MED
- **A (F4 [92], n=10 cadaveric):** 1.2 cm² (fiber 17.7 cm).
- **B (F4 [37], cited as larger):** larger value, exact number not given in-file.
- **Quality:** A medium (small cadaveric n, method stated); B UNKNOWN (cannot adjudicate without the number/method).
- **Reason:** specimen/method/normalization differences (F4's own warning on FCSA-vs-PCSA confusion and un-rescaled fibers).
- **Handling:** IMPLEMENT_WITH_RANGE using A with CV 10–20% (per F6 variability); flag B as unresolved. Do not average.

## C-07. Friction coefficients across interfaces — HIGH
- **Values in play:** dry skin-skin μs 0.5–0.7 / μk ~0.5 (reviews); palm 0.62±0.22; palmar study 0.25 dry / 0.35 moist; wrist-on-glass ~0.25 dry / ~1.4 wet; skin-table ASSUMED 0.25–0.5 dry, 0.7–1.4 wet; catalog MU_STATIC 0.6 / MU_KINETIC 0.5 (ASSUMED).
- **Populations/methods:** general skin tribology, varied sites/loads/moisture; proxies (glass/steel/fabric) for the table. Quality for the TARGET interfaces: none (no direct measurement).
- **Reason:** interface, moisture, load, and site dependence of skin friction (stated in F3).
- **Handling:** UNKNOWN for the target interfaces. IMPLEMENT_WITH_RANGE only as explicitly assumed placeholders (dry band + wet band), never as empirical. Mandatory future measurement (tribometer + HM/ABC per F3).

## C-08. Stribeck velocity — HIGH
- **A (F3):** assumed 0.022 m/s (finger-pad-on-glass fracture model).
- **B (implicit):** unknown for skin-skin and skin-table under arm-wrestling loads.
- **Quality:** proxy, low for target use — flagged CRITICAL GAP in-file.
- **Handling:** UNKNOWN. Placeholder only; must be system-identified (pendulum/CMA-ES per F3). No default may be presented as measured.

## C-09. Tendon treatment — HIGH (architectural fork)
- **A (F1, F7-minimal):** rigid tendon (L_MTU = L_CE); 2–54× faster, ~20% Fmax MAE.
- **B (F2, F4-agent-spec):** full 3-element Hill (CE+PEE+SEE [+SDE]) recommended for general simulation.
- **Quality:** both are modeling choices with cited benchmarks, not measurements of arm-wrestling tendons.
- **Reason:** real-time (>500 Hz) vs general-fidelity objectives.
- **Handling:** Both retained with explicit scope: rigid-tendon = real-time MVP branch (with stated MAE); compliant-tendon = offline/reference branch. Tendon slack/compliance for arm-wrestling muscles is UNKNOWN empirically. Do not present rigid-tendon forces as tendon-inclusive.

## C-10. Activation dynamics — HIGH
- **A (F1):** first-order ODE (Zajac; τ_a 0.01–0.05 s, τ_d ~0.04 s) — includes E–C delay.
- **B (F7-minimal):** excitation-driven bypass (E used directly; +9.6 Hz on test hardware) — no delay, no fatigue/potentiation/EMG transient.
- **Quality:** A = standard physiological form (literature time constants); B = measured speedup on specific hardware (narrow generalizability).
- **Reason:** fidelity vs loop-rate trade-off.
- **Handling:** IMPLEMENT both as labeled branches: ODE-activation (default for credibility) vs excitation-bypass (real-time fallback with documented loss of transients). The 9.6 Hz figure is REFERENCE_ONLY (hardware-specific).

## C-11. Controller layering — LOW (terminology, not physics)
- **A (F1):** 5 layers (sensory / FSM / force-torque-optimization / rapid-force / forward dynamics).
- **B (F2):** 3 layers (low physiological / mid supervisor / high technique).
- **Reason:** different groupings of the same functions (F1 splits sensing/activation/dynamics; F2 groups them).
- **Handling:** No conflict in substance. Map explicitly in MASTER spec (F1-L1+L4 ≈ F2-Low; F1-L2+L3 ≈ F2-Mid; F1-L5 ≈ plant; F2-High ≈ F1-FSM content extended to techniques).

## C-12. Moment-arm "values" vs "no equations" — MED (method, not number)
- **A (F4 [92]):** discrete peak MAs (brachioradialis 7.7, PT 4.9, biceps 4.7, triceps 2.3 cm).
- **B (F6 Chen/Kuechle):** functional means with SDs at fixed postures (different muscles/postures/methods).
- **C (F6 overall):** no ready polynomials exist; must be fitted from Holzbaur exports + experimental anchors.
- **Quality:** A/B medium (cadaveric, small n, stated postures); C is a correct status statement.
- **Handling:** Do not merge A and B into one "moment arm" number. IMPLEMENT_WITH_RANGE per source+posture; polynomial coefficients are UNKNOWN until fitted. Validation standard for all: ±2 SD over ROM (F2/F5).

## C-13. Humerus coordinate origin — MED
- **A (F4):** origin at medial epicondyle; Y to humeral-head sphere center.
- **B (F7):** origin at humeral-head articular center; X ant / Y sup / Z lat.
- **Quality:** both standards-text (ISB expositions), medium; no arm-wrestling data decides.
- **Handling:** UNKNOWN as "the" research-supported frame. Pick ONE convention (recommend F7 head-center for GH rotation + documented segment frames), record the transform, mark as implementation convention. See coordinate_systems.md.

## C-14. Forearm/pronation angle conventions — MED
- **F6-internal:** biceps grid "0°=Supination, 180°=Pronation" vs Chen wrist "mid-prone = 0°" vs F4/F7 "neutral = 0 (thumb to shoulder)".
- **Quality:** reporting conventions, not measurements.
- **Reason:** different source conventions collated without conversion.
- **Handling:** Convention conflict. Normalize all simulator angles to neutral-zero (pronation +, supination −) with documented transforms. Raw-source values keep their native convention in parameters.json notes.

## C-15. Population/evidence tier vocabularies — LOW
- **F4:** Tier1 general / Tier2 athletic / Tier3 arm-wrestler.
- **F8:** Tier1 sport-specific peer-review / Tier2 elite observation / Tier3 clinical / Tier4 general strength.
- **F5/F6:** hierarchies again (sport-specific → isometric → dynamic → clinical; in-vivo → loaded cadaver → passive → model).
- **Reason:** each file tiers a different axis (people vs evidence relevance vs measurement type).
- **Handling:** Keep all three axes with distinct names: POPULATION tier (F4), EVIDENCE-RELEVANCE tier (F5/F8), MEASUREMENT tier (F6). parameters.json uses population + evidence_type fields; never collapse "Tier 2" across axes.

## C-16. Validation thresholds vs no-threshold stance — LOW
- **A (F2/F5):** firm thresholds where consensus exists (residuals 5%/1%, MA ±2 SD, marker 1.5 cm, ICC bands).
- **B (F5):** regression/sensitivity/p-box where no consensus exists.
- **Reason:** complementary, not contradictory — but easy to misapply A where B is required.
- **Handling:** Thresholds apply ONLY to their stated quantities. Everything arm-wrestling-specific without consensus → procedure B. Never promote a B-case pass into "Validated" (cap at Partially/Unvalidated per F5).

## C-17. Grip-strength numbers in incompatible units/tasks — MED
- **A (F3 [55]):** MAX_GRIP_FORCE ~442 N (M) / ~215 N (F) — dynamometry, task-specific-ish.
- **B (F5 Tier2):** grip norms ~7 kg-m (M) / ~3.5 (F) — unit as written ("kg-m", sic), different task.
- **Quality:** A medium for hand-force input; B low for simulator use (unit/task ambiguous in-file).
- **Handling:** Use A for F_input scaling (population-labeled, IMPLEMENT_WITH_RANGE). B is REFERENCE_ONLY; do not convert kg-m → N without the missing lever arm. Flag unit ambiguity.

## C-18. Feasible vs anatomical ROM — HIGH
- **F4:** anatomical ROMs + qualitative arm-wrestling posture; feasible limits mostly unstated.
- **F7:** feasible = ADL arcs (elbow 30–130°, forearm ±50°, wrist functional subset) as principled placeholders; GH + wrist-secondaries flagged for measurement.
- **F5-Tier4:** functional elbow 100° arc, forearm 100° total — consistent with F7, but ADL-derived, not arm-wrestling-measured.
- **Quality:** anatomical ROM medium–high (general human); feasible ROM low (principle-based, explicitly non-measured).
- **Handling:** Anatomical ROM = SUPPORTED (general human). Feasible/task ROM = IMPLEMENTATION ASSUMPTION (ADL-bounded placeholder). ARM_WRESTLING_MEASURED_ROM = UNKNOWN for every joint (no in-competition goniometry in corpus). Never label ADL arcs as measured arm-wrestling ROM.

## C-19. Damping representation — LOW
- **A (F1):** constant c = 2.5 Ns/m (neutral default).
- **B (F7-advanced):** force/length-dependent SDE.
- **Handling:** Constant-c = real-time branch default (ASSUMPTION); dependent damping = offline branch. No empirical arm-muscle damping decides.

## C-20. Wrist feasible-motion wording — MED
- **F7 text:** "40° extension, 40° pronation, 17° radial, 40° ulnar" as the wrist functional subset (pronation listed at the wrist is anatomically anomalous — pronation is forearm rotation; likely source-text conflation).
- **F4:** wrist = 2 DOF (flex/ext, rad/uln); pronation at radioulnar joints.
- **Handling:** UNKNOWN as written. Implement wrist feasible as flexion-biased subset per F4's 2-DOF definition; carry F7's numbers only as flagged REFERENCE_ONLY with anomaly note. Requires source check / future measurement.

## C-21. Shoulder stabilizer framing — LOW
- **F7:** GH stability "maintained dynamically by cuff" (25–30% head contact) → feasible ROM muscularly limited.
- **F4/F8:** internal rotators (pec/lat/subscap/teres) as torque generators; injury via humeral torsion.
- **Handling:** Complementary. Simulator must model BOTH torque generation and stability-limited ROM; neither file quantifies the stability boundary — UNKNOWN.

## C-22. Residual-force thresholds vs arm-wrestling applicability — MED
- **Thresholds (F2/F5)** come from gait/whole-body inverse dynamics; no arm-wrestling-specific residual study in corpus.
- **Handling:** IMPLEMENT_WITH_RANGE as sanity gates for the dynamics solver; a "pass" does not validate arm-wrestling kinetics. Cap at Partially Validated without sport-specific data.

## Summary table

| # | Parameter | A | B | Handling |
|---|---|---|---|---|
| C-01 | Elbow zero | 0°=ext (F4) | 0=90°flex (F7) | UNKNOWN; adopt 0°=ext convention |
| C-02 | Elbow max | 130–154° | 145° / grid 140° | Range; clamp to validity |
| C-03/04 | Pron/sup | 76/80 | 80–87 / 85 | Range; task ±50 placeholder |
| C-05 | GH ROM | conditioned (F4) | generic (F7) | Use conditioned; rest REFERENCE |
| C-06 | Brachioradialis PCSA | 1.2 cm² | larger ([37], no #) | Range on A; B unresolved |
| C-07/08 | Friction μ, vs | bands/proxies | catalog assumes | UNKNOWN; placeholders only |
| C-09/10 | Tendon/activation | rigid/bypass | full/ODE | Labeled branches, scoped |
| C-12 | Moment arms | peaks vs functionals | no polynomials | Keep separate; coeffs UNKNOWN |
| C-13/14 | Frames/angles | head vs epicondyle; 3 zeros | — | One convention + transforms |
| C-17 | Grip | 442/215 N | 7/3.5 kg-m (sic) | A with range; B reference |
| C-18 | Feasible ROM | unstated (F4) | ADL arcs (F7) | Assumption; measured = UNKNOWN |
| C-20 | Wrist subset | 2-DOF (F4) | anomalous list (F7) | UNKNOWN; flagged reference |
