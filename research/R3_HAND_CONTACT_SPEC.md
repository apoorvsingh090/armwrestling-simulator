# R3 — HAND, WRIST, GRIP & CONTACT MECHANICS (`contact` database)

Scope: wrist coupling/passive curves, soft-tissue compression, friction,
grip-to-torque transfer, table geometry. Excluded: muscle architecture (R2),
neural/EMG (R9), generic bone-name anatomy. Tags: [E] empirical ·
[M] model-derived (calibrate, not auto-valid) · [U] unknown ·
[STD] standard form. Non-arm-wrestling data is NEVER match data: tagged
`MODEL_DERIVED - REQUIRES CALIBRATION` with transfer limits stated.

// ===== 1. WRIST COMPLEX & CUPPING =====
### Wrist Coupling
- Kinematic Coupling: FE↔RUD inseparable. RUD-task secondary FE 48.3° (=75% of 55.1° primary); FE-task secondary RUD 21.2° (=20% of 108.3°); pairing = extension+radial, flexion+ulnar; max ROM near neutral; egg-shaped circumduction hull [E: Li 2005, n=10 healthy males].
- Cupping mapping: "cupping" = flexion + ulnar deviation by coupling law above (NOT pure flexion) [E-direction, M-magnitude]; midcarpal share rises in flexion/loaded-extension (R1 midcarpal ratios) [E].
- Hook-position split: radiocarpal-dominant in flexion per Kamal (scaphoid/lunate 95/70% of flexion) vs ~50/50 row/column theories [E-conflicting, carry both with sources].
- Passive Stiffness Curve: 5th-order polynomial M(θ) fit (MATLAB), K_ROM = slope @1.5–2.0 Nm; neutral zone = rotation @0.2 Nm; ROM defined @2.0 Nm [M-form: wrist-axes study]. Directional end-stiffness: 0.4 Nm/deg (radial-flexion) / 0.15 (ulnar-flexion) [E: same study]. Anchor points [E: Delp 1996, n=10 males]: passive ~0 central; 0.5 Nm @90° flex; 1.2 Nm @90° ext; ~0 radial/neutral RUD; 0.9 Nm full UD. Coefficients NOT retrieved → `REQUIRES_INTERPOLATION` from anchors above. Central linear region ±17° [E: PMC3424077]. Hysteresis loops present (connective tissue) [E].
- Yielding model: end-range slope rise + hysteresis = the "yield" mechanism; NO arm-wrestling-load yielding data → MODEL_DERIVED - REQUIRES CALIBRATION.
- Wrist strength context (guardrails, NOT inputs): flexion moment peaks 40° flex 11.1 Nm, ~50% at extremes [E: Delp1996]; radial/ulnar deviators neutral 11.0±2.0 / 9.1±2.2, full-radial 7.6/6.1, full-ulnar 6.9/2.8 Nm, radial −35% at limit [E]; flexor summed PCSA +110% extensors explains flexion dominance [E: Gonzalez1997]; wrist flexors MVC 16.1/19.2/18.5 Nm @−30/0/+30° [E: FrontBioeng]; grip coupling: wrist flexion +34% at max grip, extension −10% [E: n=12]; max grip needs 30–45° extension, min 25° [E: O'Driscoll/Lee].

### Midcarpal vs Radiocarpal
- See R1 ratios (locked). Addition: wrist defined radiocarpal+midcarpal acting TOGETHER for wide carpal motion [E: functional-kinematics review]; proximal row = muscle-free intercalated segment moving synchronously [E].

// ===== 2. ARCHES & SOFT TISSUE =====
### Metacarpal Arch Deformation
- Arc motion 24.9±6.2° on fist closure (3 methods agree, n=22) [E]; 4th/5th CMC = 1 coupled DOF [M: Buffi n=1 — FLAG]; Keir components: longitudinal 0.7–2.7°, abduction −35.8..−43.5°, transverse 18.9–29.7°; arch inclusion corrects 4th/5th MCP supination 9–33° [E: n=8].
- Under MAXIMAL crushing/shear loads: [U] NO data (arch modulation studied in reach-to-grasp only, n=8 [E: Sangole]; Sancho-Bru power-grip model validated on cylinders [M] — NOT transferable to opponent-hand grip). → crushing-grip deformation = CALIBRATION STUB (neutral, flagged), as R1 directs.

### Palmar/Fingertip Compliance (effective-MA modifier input)
- Fingertip pulp: viscoelastic, rate-dependent, hysteresis, nonlinear; compliant <1N, stiffens rapidly; pads FULLY COMPRESSED >4N [E: Serina 1997 n=20; Latash/Zatsiorsky]. FE form: nonlinear-elastic + linear-viscous, Rayleigh β≈0.40e-3 s soft tissue [M: Wu 2006]. Toe→steep transition at 4–5% confined / 6–7% unconfined strain; compressibility non-negligible in 3D fingertip loading [E/M: Wu 2002].
- Palmar tissue (in-vivo, large deformation, FIRST dataset): large-deformation stiffness >50% above small-deformation stiffness; peak force 2–2.75× high-rate vs quasistatic; CV 39–110% (HIGH variability — carry as distribution, never a point); damping highest in thickest tissue; 3mm indenter, 31% compression [E: PLOS 2021].
- Forefinger spec (n=117): two-stage elasticity + transition displacement; age/gender independent [E]. Numerical tables: extraction target (not retrieved) → `REQUIRES_INTERPOLATION`.
- Opponent-force effective-MA shift from flesh compression: [U] NO coupled flesh+lever data → UNKNOWN, do not model (interface slot: penetration depth → MA correction, unwired).

// ===== 3. CONTACT INTERFACES =====
```json
{"friction_law": "|Ft| <= mu*Fn (Coulomb cone) [STD]; Stribeck velocity form per E-05 (form kept, parameters U)",
 "skin_skin": {"status": "MODEL_DERIVED - REQUIRES CALIBRATION (no skin-on-skin match data exist)",
  "proxies_E": [
   {"pair": "fingertip/glass-ish", "mu": "~0.25 dry / ~1.4 wet (0.5N, 0.8cm/s); shear stress 13MPa dry / 5MPa wet [E: Beilstein wrist-skin]"},
   {"pair": "finger/various", "mu": "0.13 polycotton – 1.16 silicone dry; wet 0.76–1.03 [E: Merrick n=40]"},
   {"pair": "finger/sandpaper#320": "0.61±0.10 dyn [E]; 0.96±0.09 (4N) [E: fingertip study]"},
   {"law": "mu = k*NF^(n-1), n≈0.66 (load-dependent fall ~46% over 1–20N) [E: finger-glass/rubber-hose studies]"},
   {"palm_vs_forearm": "palm CoF ~25% higher [E: paper study]"},
   {"moisture": "wet >2× dry; up to 10× occluded; R²>0.72 linear moisture–CoF within-subject [E: multiple]; ridges auto-regulate to converged hydration (PNAS) [E]; hydrodynamic floor ~0.0015 smooth+wet [E: calculation]"},
   {"chalk_MgCO3": "CONTESTED: decreases CoF (Li2001, dries+granular layer) vs helps dry fingertips + consistency (Clarke2024) vs nulls — NO arm-wrestling value; DO NOT encode a chalk bonus [E-conflict → U for our use]"}]},
 "skin_table": {"status": "MODEL_DERIVED - REQUIRES CALIBRATION",
  "proxies_E": [
   {"palmar/grabrails": "dry≈wet (n.s.); soapy << dry/wet; textured best soapy, smooth best dry; gender/age/size n.s. (n=30) [E: O'Meara]"},
   {"polyurethane": "PU-coated fleece mimics skin DRY sliding [E: Derler/Gerhardt — material-design pointer, not a number]"},
   {"rubber": "tire-compound data N/A to pads; skin-vs-hose variance 0.23 between-subject [E: CDC hose study]"},
   {"pad_material": "[U] vinyl/rexin dense-foam CoF unmeasured → UNKNOWN"}]},
 "friction_cone_math": {"cone": "|Ft|<=mu*Fn, stick if inside [STD:Coulomb]", "anisotropy": "finger CoF direction-dependent vs curvature radius (longitudinal data only) [E: CDC hose — transverse UNKNOWN]",
  "patches": "3-patch positions P068-P070 ASSUMPTION (kept); pressure distribution D-03 MISSING"}}
```

### Contact Model Recommendation
- Normal: Hunt–Crossley `F = k·δ^n + λ·δ^n·δ̇` (n≈1.5 Hertzian) [STD-form] — parameters k/λ/n per interface: [U] ALL. Rationale: continuous force + velocity-dependent damping kills restitution chatter at 1 kHz semi-implicit Euler (matches MVP integrator); Hertzian-only rejected (no damping → bounce); linear penalty rejected (wrong stiffening vs Serina/PLOS nonlinearity).
- Tangential: Coulomb cone + Stribeck regularization = E-05 (already the corpus form) [STD-form, params U].
- Skin micro-contact: Persson theory w/ σf≈13/5 MPa as area-scale prior [M: Beilstein] — optional upgrade path, not wired.
- Stick–slip: Franklin rigs observed NO stick-slip for skin under these protocols [E] — do not invent judder; slip = cone violation only.

// ===== 4. GRIP-TO-TORQUE (containment, NO technique multipliers) =====
- Geometry rule [FIRST-PRINCIPLES]: applied torque = F × lever from opponent's joint; Top-Roll (distal phalanges) vs Hook (PIP/wrist) differ ONLY by application point on the SAME hand model — NO bonus factors, ever.
- Finger joint-moment ordering: DIP/PIP max at ~31mm cylinder; long>index>ring>little (large cylinders), long>little>ring>index (≤31mm); MCP moment rises with diameter [M: Wu-2023 grip model].
- Crimp/pulley mechanism (ANALOGY ONLY): tendon-pulley friction ≤18% grip force; bowstringing ×20 moment-arm effect in crimp; A2 load ×36 vs slope grip [E: Schweizer climbing — NOT arm-wrestling; transfer FORBIDDEN without re-validation].
- Finger-extension failure threshold: [U] NO forcible-opening torque data (mallet/jersey mechanisms are clinical injury descriptions, not thresholds). → UNKNOWN, never gate outcomes on it.
- Thumb webbing/thenar lock: 40% thenar share = F3 expert/dynamometry CONTEXT (not a force value); opposition = anteposition+adduction+auto-pronation chain [E: descriptive anatomy]; webbing forces: [U].
- Grip strength corroboration: M 462±61 / F 211±58 N [E: n=12 — matches P071 442/215]; use as order-of-magnitude guardrail for grip-map Fmax ONLY.

// ===== 5. TABLE CONSTRAINTS (geometry locked, forces open) =====
```json
{"table_WAF": {"top_in": "36x26 (91.4x66.0cm); heights 40 stand / 28 sit (101.6/71.1cm) [E: WAF 2024 rules]",
 "elbow_pad": "7x7x2in (17.8cm² x 5.1cm) dense foam, vinyl/rexin, 2in from edge, 1/2in overlap [E: WAF]; translation constraint: elbow CENTER stays on pad (foul otherwise) [E: rules]",
 "touch_pad": "10x4in (25.4x10.2cm), angled per placement spec [E: WAF]",
 "peg": "1in dia x 6in high (2.5x15.2cm) @13in mid-edge, 1in inset; free hand MUST grip (foul on loss) [E: WAF]",
 "start_pose": "wrists STRAIGHT, shoulders square, grip palm-to-palm center, thumb knuckles visible, fist-gap biceps-forearm [E: AAA/IFA rules — initial conditions, NOT ROM data]",
 "neutral_zone": "10-to-2-o'clock clock face; straps on in-zone slip [E: AAA rules — slip-event protocol pointer]",
 "permitted": "stickum/rosin/chalk [E: rules — permission is NOT a friction value]",
 "forces": {"pad_compression": "[U]", "pad_mu": "[U]", "peg_reactions": "[U]", "humerus_translation_limit": "pad boundary as POSITION constraint [M-form]; stiffness [U]"}}}
```

// ===== FITTING DIRECTIVES =====
1. Friction tables enter as moisture×material×load grids with the power-law load falloff; single-μ values FORBIDDEN anywhere in code or GUI.
2. Chalk enters ONLY as a moisture-state modifier with contested sign — default OFF, sensitivity flag ON.
3. Passive wrist curves: interpolate Delp anchors + 5th-order FORM (coefficients fit at build time from retrieved curves, ±-envelopes from SDs); cupping simulated via Li-coupling + oblique axis (R1), never a "cupping torque".
4. Soft tissue: two-stage + rate-scaling form; PLOS CVs carried as distributions; >4N pad-bottoming flag for contact solver (fully-compressed pads transmit directly [E: Serina]).
5. Top-Roll vs Hook = contact-patch placement ONLY. Any force multiplier = build-breaking violation (MASTER §16).
6. Table: geometry + rule constraints wired; ALL force parameters constructor-required (forearm.py pattern), no defaults.
