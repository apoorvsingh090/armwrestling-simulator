# R2 — MTU ARCHITECTURE, PATHS & MOMENT ARMS (`mtus` database)

Scope: architecture + geometry + MA functions + tendon/FL/FV standard curves ONLY.
Excluded: neural/EMG (R9), fatigue (R10), bone/injury (R11), coaching.
Tags: [E] EMPIRICAL · [M] MODEL_DERIVED (needs calibration, NOT auto-validated) ·
[U] UNKNOWN · [STD] standard-form reference value (cite + verify before use).
No polynomial coefficients invented anywhere; discrete points flagged
`REQUIRES_INTERPOLATION`; undocumented geometry flagged
`MODEL_DERIVED - REQUIRES CALIBRATION`.

// ===== REFERENCE DATASETS (provenance, use with tags) =====
```json
{"datasets": [
 {"id": "HOLZ2005", "ref": "Holzbaur/Murray/Delp 2005, Ann Biomed Eng 33:829-840",
  "content": "15-DOF upper limb, 50 compartments; Hill 4-params (Lopt, Fpeak, slack, pennation); PCSA=volume/normalized-Lopt (sarcomere 2.7um); Fpeak=PCSA×specific-tension; fibers renormalized 2.7um; MAs from Murray-2002 scaling; ma_ave tabulated for sensitivity",
  "arch_sources": "Langenderfer2004, Murray2000, An, Lieber, Jacobson", "tag": "M"},
 {"id": "MURR1995", "ref": "Murray/Delp/Buchanan 1995, J Biomech 28:513-525 (n=2 specimens + computer model)",
  "content": "FE + pron/sup MAs (BRD, BIC, BRA, PT, TRI) via tendon displacement; elbow 0-130°, forearm -90sup..+70pro; radius rotates about radial-head/distal-ulna axis, ulna fixed; polynomial fits of displacement (derivatives=MAs)",
  "tag": "E-points, M-fits"},
 {"id": "MURR2000", "ref": "Murray/Buchanan/Delp 2000, J Biomech 33:943-952 (n=10 specimens)",
  "content": "fascicle/sarcomere/pennation/mass + tendon displacement; Lopt normalized to 2.8um sarcomere; BIC-long excursion 56% Lopt (12.8cm) vs TRI-long 28% (12.7cm); MAs 4.7 vs 2.3cm; PCSA uncorrelated w/ peak MA or bone lengths",
  "tag": "E"},
 {"id": "LIEB1992", "ref": "Lieber et al. 1992, J Hand Surg 17:787-798 (n=154 muscles, 21 forearm muscles, laser diffraction)",
  "content": "mass/fiber-length/pennation/sarcomere → PCSA + FL/ML ratios; BRD vs PT: equal mass, BRD PCSA = 1/3 PT (long/small-pennation vs short/pennated)",
  "tag": "E"},
 {"id": "GARN2001", "ref": "Garner/Pandy 2001, Visible Human, 42 bundles/26 groups",
  "content": "line-segment paths from VH images; per-muscle numbers NOT retrieved in this pass → extraction target (thesis tables / OpenSim upperlimb .osim)",
  "tag": "M-pointer"},
 {"id": "SETH2019", "ref": "Seth et al. 2019, Front Neurorobot (Klein Breteler/van der Helm bundles)",
  "content": "shoulder-bundle Fmax/Lopt/slack/pennation table (see Subscap/Biceps/Triceps rows); 2%-increment Lopt/slack calibration behavior documented → calibration FLAG on these rows",
  "tag": "M"},
 {"id": "HAUG2001", "ref": "Haugstvedt/Berger/Berglund 2001, Acta Orthop 72:629-634 (n=8 cadaveric, elbow 90°)",
  "content": "rotation TORQUES at 10° steps -90..+90 (not MAs): BIC+supinator supinate (BIC 4× pronated); PT + PQ-superficial/deep active throughout, peak near neutral; ECU/FCU minor, sign-flip at extremes",
  "tag": "E-torque-shape"},
 {"id": "IBAN2014", "ref": "Ibanez-Gimeno et al. 2014, PLoS ONE 9:e90319 (skeletal model + 3D imaging)",
  "content": "PT rotational efficiency Erot surface: max near neutral each elbow angle; +18% extension(180°)→flexion(40°); max-Erot locus -11°pro → +6°sup; Fp 86-99% of F",
  "tag": "M-surface"},
 {"id": "BREM2006", "ref": "Bremer et al. 2006, Clin Biomech 21:683-691 (3 elbow angles)",
  "content": "forearm-rotator MAs; biceps best supinator at 90° elbow flexion",
  "tag": "E"}
]}
```

// ===== STANDARD HILL CONSTANTS (reference values, verify before use) =====
```json
{"tendon": {"strain_at_Fmax": "0.033 [STD:Zajac1989]", "fail_strain": "0.10 @ 3.5Fmax [STD:Zajac1989]",
 "stress_at_Fmax_MPa": "32 [STD:Zajac1989]; in-vivo TA 25MPa/2.5%/1.2GPa [E:Maganaris; generic 15-30MPa, 2%, 1.2GPa Ker/Zajac]",
 "normalized_modulus": "37.5 [STD:Zajac1989]", "elbow_wrist_flexor_specific_k": "[U] NO flexor-specific stiffness retrieved — MODEL_DERIVED - REQUIRES CALIBRATION; use Zajac generic interim, flagged"},
 "specific_tension_N_per_cm2": {"Ker1988": "30 [STD]", "Arnold-gait": "61 [M:lower-limb]", "arm_value": "[U] none retrieved — PROV-01 (50) UNCHANGED, do not touch"},
 "sarcomere_opt_um": {"Holzbaur": "2.7 [M]", "Murray2000": "2.8 [E-human]"},
 "vmax_Lopt_per_s": {"Thelen-running": "15 [M:lower-limb]", "arm_value": "[U] — PROV-03 (10) UNCHANGED"},
 "passive_curve": {"form": "exponential f_p=p1(exp(p2(x-xp))-1) [STD:Zajac1989]", "eps0": "1.1-1.8 (Zajac:1.8) [STD:Epstein-Herzog/Zajac]",
  "alt_form": "Fpassive=b1*exp(b2*Dl), b1/b2 muscle-dependent (Woittiez) [STD-form, params U]"},
 "FL_FV_basis": {"active_FL": "GHJ sarcomere (Gordon 1966) [STD]", "splines": "natural cubic (Zajac) [STD]",
  "compliance_rule": "compliance = slack/Lopt ratio [STD:Zajac1989]", "slack_method": "Manal&Buchanan2004 numerical [M-pointer]"},
 "whip_yield": "[U] no tendon-elasticity 'whip' data for arm-wrestling loads — UNKNOWN, do not model"}
```

// ===== MTU ENTRIES =====
// Legend: E=empirical point · M=model row (calibrate) · U=unknown · I=requires interpolation
### Pectoralis Major
- Architecture: PCSA/Lopt/pennation/slack/Fmax: [U] not retrieved (Holzbaur Table 1 extraction target).
- Path: Origin: clavicle/sternum/ribs→humerus (standard anatomy, map to R1 thorax/humerus frames). Insertion: bicipital groove. Wrapping: humeral-head wrap: MODEL_DERIVED - REQUIRES CALIBRATION (OpenSim upperlimb .osim extraction).
- MA: shoulder functions: [U] (Hoffmann 2022 3D-MA method exists for cuff/deltoid — extraction target, not retrieved).
- Variance: [U].

### Latissimus Dorsi
- Architecture: pennation 25° single value, rest incomplete [P034 — REFERENCE_ONLY, do not build from this].
- Path: Origin: thorax→humerus. Wrapping: MODEL_DERIVED - REQUIRES CALIBRATION.
- MA: [U]. Variance: [U].

### Subscapularis
- Architecture: Fmax 1306.9N, Lopt 8.7cm, pennation 20°, slack 3.3cm [M:P032-source-class — Holzbaur small-n fit; Seth bundles differ in grouping — CONFLICT: reconcile bundle maps before use].
- Path: Origin: scapula→humerus (map R1). Wrapping: humeral-head: MODEL_DERIVED - REQUIRES CALIBRATION.
- MA: IR peak 27.0mm inferior [E:P048]; functions [U]. Blemker-3D vs line-segment discrepancy warning applies (fiber-sign flips seen in cuff) [M-caveat].
- Variance: [U].

### Biceps Long / Short
- Architecture: Long: PCSA 4.6cm², Lopt 23.2cm [E:P026/MURR2000]; Short: [U] (Holzbaur Table 1 extraction target). Seth rows [M]: Long 485.8N/0.1412m/0.257m/0°, Brevis 693N/0.1264m/0.212m/0° (calibration-flagged).
- Path: Origin: supraglenoid (long, via bicipital canal — transverse humeral ligament) / coracoid (short). Insertion: radial tuberosity. Wrapping: radial-head wrap for supination path: MODEL_DERIVED - REQUIRES CALIBRATION.
- MA functions (E-points, REQUIRES_INTERPOLATION — NO coefficients published):
  - Flexion: peaks EXTENDED + larger SUPINATED [MURR1995]; model peaks 100–120° elbow [MURR1995-model]; anchor 4.7cm [E:P038].
  - Supination: peak between neutral and 55° pronation, minimum near 60° supination, falls past neutral [Favre-review]; female specimen ~1.1cm (supinated), model 1.3cm (most pronated) [MURR1995 — specimen/model discrepancy NOTE]; decreases with elbow extension [MURR1995]; best at 90° elbow [BREM2006]; biceps 4× supination torque pronated vs supinated [E-torque:HAUG2001]; rupture → −60% supination strength neutral [L:clinical].
  - Lookup seed (elbow 90°, from HAUG2001 torque-shape + MURR1995 MA-shape — SHAPES ONLY, magnitudes per-specimen): sup-MA maximal neutral..55°pro, minimal 60°sup.
- Variance: PCSA uncorrelated w/ peak MA or bone lengths [E:MURR2000]; excursion 56% Lopt [E].

### Brachialis
- Architecture: Fmax 1177.4N, Lopt 8.6cm, slack 5.4cm [M:P032 Holzbaur fit]; pure flexor, supination-independent [MURR1995].
- Path: Origin: distal humerus→ulna. Wrapping: none (deep, straight): MODEL_DERIVED - REQUIRES CALIBRATION (verify).
- MA: flexion, forearm-independent [MURR1995]; discrete values: Holzbaur Table 1 extraction target. REQUIRES_INTERPOLATION.
- Variance: [U].

### Brachioradialis
- Architecture: PCSA 1.2cm², Lopt 17.7cm [E:P028, C-06 disputed vs larger [37]-unresolved]; BRD PCSA = 1/3 PT at equal mass [E:LIEB1992]; published ranges Lopt 14.2–23.9 / PCSA 0.5–3.4 (Amis/An/Brand/Lieber/Veeger compilations) [E:MURR2000-Table3].
- Path: Origin: humerus→radius (distal). Via-points: MODEL_DERIVED - REQUIRES CALIBRATION.
- MA: flexion peak 7.7cm [E:P039]; rotation: pronation-MA when supinated / supination-MA when pronated (returns to neutral), small magnitudes [MURR1995].
- Variance: ranges above.

### Pronator Teres
- Architecture: PCSA 1.1cm², Lopt 5.5cm [E:P029/MURR2000-class]; pennation/slack/Fmax: [U] (Holzbaur Table 1 extraction target). P030/P031 scaling = ASSUMPTION (never defaults).
- Path: Origin: medial epicondyle + coronoid (humeral/ulnar heads). Insertion: mid-lateral radius. Via-points: MODEL_DERIVED - REQUIRES CALIBRATION. O/I digitized in Veeger1997 (5 specimens) — extraction target.
- MA functions (E-points, REQUIRES_INTERPOLATION):
  - Pronation: peaks NEAR NEUTRAL [MURR1995]; magnitudes DISAGREE: male ~0.5 / female ~0.75 / model ~1.2cm [MURR1995 — use range, never a point]; anchor 4.9cm is the FLEXION-context peak [E:P040 — do not conflate with rotation MA]; model flexion-MA peak ~75° [MURR1995-model].
  - Efficiency surface: Erot max near neutral each elbow angle; +18% ext→flex; locus −11°pro→+6°sup; Fp 86–99% F [M:IBAN2014].
  - Torque-shape: PT + PQ active throughout −90..+90, most efficient near neutral [E-torque:HAUG2001, elbow 90°, 10° steps].
- Variance: magnitude disagreement above IS the variance statement.

### Pronator Quadratus
- Architecture: [U] (LIEB1992 includes PQ in n=154 set — NUMBERS NOT RETRIEVED, extraction target). Anatomy [E]: distal-1/4 ulna oblique ridge → distal-1/4 radius lateral/anterior; deep flat quadrilateral, parallel fibers; superficial + deep heads [E:Choung n=20 forearms; AJR].
- Path: as anatomy above (map R1 ulna/radius frames). Via-points: none (flat sheet): MODEL_DERIVED - REQUIRES CALIBRATION (verify).
- MA: rotation torque-shape via HAUG2001 (superficial + deep heads, active throughout, peak near neutral) [E-torque-shape]; MA magnitudes: [U].
- Variance: [U].

### Supinator
- Architecture: [U] (not in retrieved tables — extraction target: Holzbaur Table 1).
- Path: Origin: ulna/humerus→radius (wraps proximal radius). Wrapping (radial-head/proximal-radius wrap): MODEL_DERIVED - REQUIRES CALIBRATION.
- MA: "key rotator" qualitative [F6]; supinates with biceps, 1/4 biceps torque scale implied by HAUG2001 ratio [E-torque-ratio, elbow 90° only]; magnitudes: [U].
- Variance: [U].

### FCR / FCU / ECR (ECRL+ECRB) / ECU
- Architecture: wrist flexor/extensor set in LIEB1990 (Lieber/Fazeli/Botte) — NUMBERS NOT RETRIEVED, extraction target. FDP 410mm² reference row exists in tapping-study table [M:CDC2013 citing Chao/Holzbaur/Asakawa — pointer only].
- Path: forearm→carpus/MC bases (standard anatomy, map R1). Retinaculum/pulley via-points: MODEL_DERIVED - REQUIRES CALIBRATION.
- MA: functional anchors P042–P047 (mm ± SD, MRI-vs-functional gaps) [E]; Gonzalez1997: flexor summed PCSA +110% extensors → flexion moment dominance [E-model]; Delp1996 wrist moments radial 11.0±2.0 / ulnar 9.5±2.2 Nm neutral + passive 0.5/1.2/0.9 Nm end-range [E-functional context, kinetics-adjacent — usable ONLY as order-of-magnitude guardrails, never as muscle inputs].
- Variance: SDs in P042–P047.

### Triceps (Long / Lateral / Medial)
- Architecture: Long: PCSA 10.3cm², Lopt 45.4cm [E:P027 — 45.4cm flagged long, preserved]; Seth long row [M]: 1580.6N/0.0969m/0.241m/10° (BUNDLE-MAP CONFLICT with P027 single-head values — reconcile before use). Lateral/medial: [U] (Holzbaur Table 1 extraction target). All compartments share elbow MA [HOLZ2005].
- Path: Origin: infraglenoid (long) / humerus (lateral+medial) → olecranon. Via-points: MODEL_DERIVED - REQUIRES CALIBRATION.
- MA: extension, shoulder-coupled (smaller overhead) [F6]; anchor 2.3cm [E:P041]; excursion 28% Lopt over 90° (narrow operator) [E:MURR2000].
- Variance: [U].

// ===== FITTING DIRECTIVES (coding agent) =====
1. Ingest order: [E] anchors → [M] rows (flagged) → lookup tables → [U] stays null (constructor-required, as forearm.py pattern).
2. MA fitting: interpolate MURR1995/HAUG2001/IBAN2014 discrete shapes ONLY as SHAPE PRIORS with ±-envelope from specimen disagreement (PT 0.5–1.2cm); never fit a point value as truth.
3. Tendon: Zajac generic (3.3%/32MPa/modulus 37.5) as MODEL_DERIVED interim for ALL tendons; per-tendon k: REQUIRES CALIBRATION.
4. Specific tension: PROV-01 UNCHANGED (Ker-30 noted as STD alternative — switching values = calibration, FORBIDDEN in this pass).
5. Bundle-map conflicts (Seth vs Holzbaur vs single-head P027) must be reconciled (document mapping) before any Fmax enters `mtus`.
6. Shoulder line-segment vs 3D-fiber discrepancy (Blemker: sign flips) → shoulder MAs carry model-form uncertainty; never present Holzbaur shoulder MAs as measurements.
