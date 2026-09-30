# R1 — STRICT SKELETAL & JOINT-KINEMATIC SPECIFICATION

Scope: rigid-body segments + joint kinematics ONLY. Excluded per brief: muscle
architecture/physiology, material properties, EMG/control/fatigue, technique
coaching concepts. Primary standard: Wu et al. 2005, J Biomech 38:981–992
(DOI 10.1016/j.jbiomech.2004.05.042, PMID 15844264) — abbreviations [Wu2005].
Confidence tags: [V] = verified against primary-source excerpt in this pass;
[C] = conventional reading of [Wu2005], VERIFY against primary text before
code generation; [L] = independent literature value with source; [U] = unknown.
"UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION" = no literature value exists.

// ===== GLOBAL CONVENTIONS (JSON) =====
```json
{
  "units": {"angle": "deg (I/O), rad (engine)", "length": "mm (anatomy), m (engine)"},
  "side": "right arm; MIRROR left raw data across sagittal plane [V]",
  "rotations": "Euler angles for shoulder; Grood-Suntay JCS elsewhere [V]",
  "gimbal_rule": "GH Y-X-Y singular at 0/180 deg elevation; use AA (not AC) scapular landmark to reduce gimbal lock (Groot 1998) [V]",
  "engine_note": "quaternions internal; JCS angles for I/O + constraints [C]"
}
```

// ===== SEGMENT FRAMES =====
| Segment | Origin [V] | Y-axis [V] | X-axis [V] | Z-axis | Landmarks |
|---|---|---|---|---|---|
| Thorax | IJ region (suprasternal) [C] | vertical, superior [V] | anterior [C] | lateral-right [C] | C7, T8 spinous processes [V]; IJ, PX [C] |
| Clavicle | SC joint region [C] | up: Yc ⊥ (Xc,Zc) [V] | forward: Xc ⊥ (Zc,Yt); defined vs thorax Yt (only 2 landmarks) [V] | along clavicle SC→AC [C] | SC, AC [V] |
| Scapula | AA (angulus acromialis; figure origin at AC must move to AA) [V] | up: Ys ⊥ (Xs,Zs) [V] | TS→AA direction [C] | ⊥ plane(AI,AA,TS) [C] | AA, TS (trigonum spinae), AI (angulus inferior), AC [V] |
| Humerus opt1 | GH (rotation center; NOT bony, required for long axis) [V] | mid(EL,EM)→GH [V] | ⊥ plane per Fig.1/5 [C] | flexion-axis approx (Zh1/Zh2) [V] | GH, EL (lat. epicondyle), EM (med. epicondyle) [V] |
| Humerus opt2 | exists: motivated by EL–EM short-distance error sensitivity [V] | per [Wu2005] Note 1 [C] | — | — | USE opt2 for digitized builds; opt1 for reporting [C] |
| Ulna | midway distal-ulna↔coronoid [C, via F4] | proximal along shaft [C] | anterior→ulnar tuberosity [C] | right-handed [V: Zu right] | coronoid, US (ulnar styloid), tuberosity [C] |
| Radius | RS (radial styloid) [V] | RS→EL proximal [V] | ⊥ plane(RS,US,EL), forward [V] | ⊥ (Xr,Yr), right-handed [V] | RS, US, EL [V] |
| Forearm (intermediate) | = radius origin [V] | aligned w/ ulna Y at neutral [V] | per ulna at neutral [V] | per ulna at neutral [V] | neutral = elbow 90° sagittal, thumb→shoulder [V] |
| Carpus (cluster) | capitate center (ISB carpal example) [V] | proximal [C] | radial-side per Wu Fig [C] | right-handed [C] | capitate; scaphoid/lunate/triquetrum tracked separately if midcarpal modeled |
| Metacarpals | CMC base center per bone [C] | proximal along shaft; deviation 0 = 3rd MC ∥ Yr [V] | dorsal-palmar per Wu Fig [C] | right-handed [C] | MC bases/heads; Cooney CMC-Y: trapezial-saddle mid-ridge → trapezium/scaphoid/trapezoid junction [V] |
| Phalanges | joint centers (MCP/PIP/DIP) [C] | proximal along segment [C] | per ISB hand § [C] | right-handed [C] | condyles/trochleae [C] |

Landmark set for digitization: C7, T8, IJ, PX, SC, AC, AA, TS, AI, GH*, EL, EM,
RS, US, capitulum, trochlea, capitate, MC3 axis. (*GH = functional center.)
Digitization variance: assessed in primary validation work (83% of variant JCS
indistinguishable from ISB on repeatability) [V]; per-landmark mm values:
UNKNOWN in this pass — extract from [Wu2005] validation + Karduna 2001 before
build. Instrument proxy: electrogoniometer intrarater ICC 0.91–0.97, SEM ~2–2.6°
[L, OpenOrthop J goniometer study, n=43].

// ===== JOINT SCHEMAS =====
### Sternoclavicular (SC)
- Parent: Thorax. Child: Clavicle. DoF: 3 (protraction/retraction, elevation/depression, axial rotation) [C].
- Sequence: Karduna et al. 2000 order (consistent w/ 2-D clinical views) [V sequence-exists; exact order C].
- Frames: as above. Anatomical ROM: protraction ~15–20° / retraction ~20–30° / elevation ~40–45° [L, standard shoulder texts — VERIFY]. Feasible: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION.
- Coupled/laxity: SC posterior rotation + elevation are COMPONENT motions of scapular upward rotation (coupled, see ST) [L, PMC8204887].
- Variance: UNKNOWN in this pass.

### Acromioclavicular (AC)
- Parent: Clavicle. Child: Scapula. DoF: 3 (tilt, upward rotation, internal rotation components) [L, PMC8204887].
- Sequence: Karduna 2000 [V-exists/C-order]. Anatomical ROM: small (UR ~5–10°) [L — VERIFY]. Feasible: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION.
- Coupled/laxity: AC internal rotation ~60° re-orients SC axes and splits UR production between SC elevation vs SC posterior rotation [L, PMC8204887].
- Variance: UNKNOWN in this pass.

### Scapulothoracic (functional, NOT synovial)
- Parent: Thorax. Child: Scapula. DoF: 5 modeled (3 rotations + 2 glides on ellipsoid thorax) or rotation-only regression [C].
- Constraint model (kinematic regression, muscle-free): scapular UR / posterior tilt / external rotation = f(humeral elevation, plane). Prescription [L]: (i) first-order: Inman 2:1 (2° GH : 1° ST); (ii) reference: healthy-control means UR 26±6° @60°, 34±7° @90°, 41±9° @120° humeral elevation [L, stroke-control cohort]; pattern = progressive UR + decreased IR + anterior→posterior tilt [L, Ludewig/McClure]; (iii) production: AnyBody/de Groot-style regression of ST angles on thoracohumeral elevation (mean-rhythm fits; soft-tissue artifact caveat) [L, PMC6620199]. Reported rhythm range 1.35:1–7:1, phase- and load-dependent [L, review].
- Gimbal: use AA landmark (not AC) [V]. Feasible (arm-wrestling): UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION (low-elevation ~45° regime has negligible-UR window 30–60° per Ekstrom [L] — VERIFY in task).
- Coupled/laxity: ST UR supplies 13–20° (76–94%) of humerothoracic axial rotation via PoE coupling [L, PMC9081276]; trunk/forearm posture shifts scapular angles (pronation vs supination changes UR/tilt by ~1–2.5° [L, PMC10618017]).
- Variance: inter-subject UR SD 6–11° across 60–120° [L].

### Glenohumeral (GH)
- Parent: Scapula. Child: Humerus. DoF: 3. Euler Y–X–Y (SOLE Euler joint; Grood–Suntay floating-axis equations DO NOT APPLY — e1/e3 start parallel) [V].
- Rotations: e1 (scapular Y) = plane of elevation; e2 = elevation (NEGATIVE per ISB sign); e3 (humeral Y) = axial rotation [V+C-sign: verify sign table in code review].
- Frames: humerus opt1/opt2 above. Anatomical ROM: flex 0–180 / abd 0–180 / ER 0–90 / IR 0–80 (conditioned) [L, P001–P005/AAOS]; rotator-cuff-tear/arthroplasty patterns excluded.
- Feasible: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION (pad-constrained; ~45° start = scenario context [P088], not a constraint).
- Coupled/laxity: humeral-head radius 20–37 mm range used in sensitivity work [L, PMC6620199]; translation: UNKNOWN in this pass (functional-center assumption).
- Variance: population head-diameter/retroversion effects [P025 — geometry, not kinematics].

### Humeroulnar
- Parent: Humerus. Child: Ulna. DoF: 1 (+ coupled). JCS Z–X–Y [V]: e1 = Zh (flexion αHF + / hyperextension −) [V]; e2 = rotated Xu (βHU carrying angle) [V]; axial γHU negligible [V].
- Frames: humerus opt2 preferred for builds [C]; ulna above. Flexion axis = trochlea↔capitulum centers; capitellum flexed forward ~40°; axis internally rotated ~14°; medial trochlear ridge 6–8° valgus tilt [L, PMC8258984].
- Anatomical ROM: 0–150° flex (AAOS) [L]; 0–140° alternate norm [L, Physiopedia]; hyperextension male +5–8° [P007]. Zero: full extension = 0° [V-convention].
- Feasible: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION (table/pad setup; "rarely past 90–100°" is UNVERIFIED assertion — DO NOT CODE).
- Coupled/laxity (code as functions, not constants): carrying angle M 11–14° / F 13–16° at extension [L, Fornalski review]; valgus LOSS with flexion (dependent arm, n=7 cadaveric): Δvarus 3.9±3.4° @60°, 7.3±5.2° @90°, 8.9±7.1° @120° vs extension [L, Wilps 2025]; change concentrated 30–90°, ~0 between 0–30° [L]; continuous linear trend (n=2 post-mortem) [L]; internal axial rotation early-flexion → external late-flexion [L]; axis at trochlear center [L]. Varus–valgus laxity envelope: muscle-release deltas 0.5–1.4°, UCL-bundle 1.8–3.2° [L, in-vitro — ANGLES ONLY, no stiffness]. Abducted-arm (90° HTA) adds ~1–1.6° varus vs side [L, 2024].
- Variance: Wilps SDs above; sex effect on carrying angle [L].

### Radioulnar — PRUJ + DRUJ (radius rel. ulna, X–Z–Y order) [V-order]
- Pronation POSITIVE, supination NEGATIVE [V]. Displacement q3 = proximal/distal translation [V].
- Anatomical ROM: pronation 76–80° / supination 80–87° (cuff device, elbow 90°) [P010/P011]; DRUJ component 150–180° + 30° radiocarpal contribution disputed [L, StatPearls — VERIFY]; hand-level 260° includes carpal/metacarpal rotation [L, King 1986].
- Zero: neutral (elbow 90°, thumb→shoulder) [V]. Feasible: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION.
- Coupled/laxity (mandatory, NOT optional): NO single center of rotation; centrode near ulnar-head center, moves opposite the motion [L, King 1986]; ulna evasive semi-lunar coronal/transverse motion (initial varus shift → dorsal) [L]; sigmoid notch 1.5–1.6× ulnar-seat diameter → intrinsic dorsal-volar laxity [L, RadioGraphics]; radius head translates anterior (pronation) / posterior (supination) [L, PMC8258984]; dynamic ulnar variance 1.34±0.53 mm, max +1.52±1.56 mm gripping-in-pronation; positive variance >2.5 mm [L]; variance ↑ with pronation + firm grip + ulnar deviation, ↓ with supination [L]; TFCC fiber recruitment pattern: dorsal-superficial + deep-volar taut in pronation; volar-superficial + deep-dorsal taut in supination [L, RadioGraphics — PATTERN ONLY]; PRUJ congruency best at extremes (curvature 9.74 neutral → 14.7 mm extremes) [L, n=30 CT]; axial carpal shift 45° relaxed / 15° contracted [L].
- Variance: ulnar variance individual/lifetime variation [L]; DRUJ contact <10% surface at extremes [L].

### Radiocarpal + Midcarpal (model as TWO coupled joints, not one block)
- Radiocarpal: radius↔proximal row (scaphoid/lunate/triquetrum + TFCC disc; pisiform EXCLUDED [L, Norkin]).
- Midcarpal: proximal row↔distal row (trapezium/trapezoid/capitate/hamate); scaphoid = bridge/connecting rod; proximal row = muscle-free intercalated segment [L, functional-kinematics review].
- Motion split (code as ratios with SD): flexion — 75% radioscaphoid / 50% radiolunate; midcarpal capitatescaphoid 10±13°, capitate-lunate 22±19° [L, Kaufmann n=8 CT, total flex 68±12°]; extension — 92% / 52%; midcarpal 0±5° / 15±11° (total ext 50±12°) [L]. Scaphoid/lunate as % capitate: flex 95±20 / 70±12; ext 83±19 / 37±18; scapholunate 25±17% of flexion; lunate 46±25% < capitate, 35±31% < scaphoid [L, Kamal]. Loaded extremes: scaphoid/lunate 70/46% flex, 74/42% ext; >50% of loaded-extension motion at MIDCARPAL [L, Rainbow]. Axial load: +~4° flexion shift of scaphoid+lunate [L, 4-D CT].
- "Cupping" mapping: flexion couples with ULNAR deviation; extension with RADIAL deviation (Li 2005: RUD-task secondary FE 48.3° = 75% of 55.1°; FE-task secondary RUD 21.2° = 20% of 108.3°; max ROM near neutral; egg-shaped circumduction hull) [L, n=10]. Midcarpal share RISES in flexion/loaded-extension → cupping = flexion + ulnar deviation with midcarpal-dominant share [L-synthesis, labeled].
- Mechanical axes: oblique 26.6±4.4° to anatomical FE; max ROM 111.5±10.2° (ulnar flexion); pure flex 65.2±23.2 / pure ext 64.2±9.8; dart-thrower axis radial-extension↔ulnar-flexion [L, wrist-axes study]. Capitate FE/RUD axes NON-INTERSECTING (3.9±2.0 / 3.9±1.4 mm) → no universal joint [L, Neu/Crisco n=20]; capitate–3rdMC minimal relative motion → lumped-hand simplification SUPPORTED [L].
- Anatomical ROM: AAOS flex 80 / ext 70 / UD 30 / RD 20 [L]; alternate 60/60/20/20 [L, Physiopedia — report both]; functional (ADL): Palmer 60E/54F/40UD/17RD (n=40) [L]; Brumfield 5F/30E/10RD/15UD (n=10) [L — conflicting functional defs, task-transfer UNKNOWN].
- Feasible: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION.
- Variance: SDs above; scaphoid RUD patterns highly individual (spectrum: pure-FE-axis → pure-deviation-axis rotators) [L].

### CMC (incl. thumb) / MCP / IP
- Thumb CMC: Cooney Y-axis (trapezial-saddle mid-ridge → trapezium/scaphoid/trapezoid junction) [V]; palmar/radial abduction 60/60 AAOS [L].
- 4th/5th CMC = ONE coupled DOF for arch formation (single-subject CT functions) [L, Buffi n=1 — FLAG small-n]; metacarpal arc motion 24.9±6.2° fist closure (3 methods agree) [L, n=22].
- Arches: proximal transverse RIGID (carpal tunnel roof); distal transverse (MC heads, 2–3 stable, 4–5 mobile) + longitudinal + oblique FLEXIBLE, intrinsic-maintained, keystone at MCP [L, Hertling/Kessler; Sangole/Levin]; Keir segmented model: longitudinal 0.7–2.7°, abduction −35.8..−43.5°, transverse 18.9–29.7°; arch inclusion corrects 4th/5th MCP supination 9–33° [L, n=8].
- Digits: MCP 80 / PIP 90 / DIP 65 (AAOS) [L]; functional hand posture: wrist ext 20 + UD 10, MP 45, PIP 30–45, DIP 10–20, thumb CMC opposed/MP10/IP5 [L, Norkin/Hertling].
- Grip-deformation kinematics under MAXIMAL crushing load: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION (arch modulation studied in reach-to-grasp only [L, Sangole n=8]; Sancho-Bru power-grip model validated on cylinders [L] — NOT transferable to opponent-hand grip without re-validation).
- Feasible: UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION.

// ===== ARM-WRESTLING FEASIBLE ROM TABLE (honest version) =====
| DoF | Anatomical (source) | Feasible match ROM | Status |
|---|---|---|---|
| GH 3-rotor | P001–P005 / AAOS 180/60/180/40 | UNKNOWN | pad-constrained; calibrate |
| Elbow flex | 0–150 AAOS / 0–145 P006 | UNKNOWN ("90–100°" UNVERIFIED) | table-setup IK input |
| Pronation/supination | P010/P011 | UNKNOWN | grip-coupled; calibrate |
| Wrist FE/RUD | AAOS 80/70/30/20 | UNKNOWN | cupping-config; calibrate |
| CMC/MCP/IP | AAOS hand values | UNKNOWN | crushing-grip; calibrate |
| Scapula/clavicle | rhythm laws above | UNKNOWN (locked-or-prescribed ASSUMPTION carried) | low-elevation regime |

// ===== CODING-AGENT DIRECTIVES =====
1. Implement frames exactly as [V] rows; [C] rows need primary-text check (flagged lines above) before merge.
2. GH = Y-X-Y Euler (singular at 0/180° elevation: clamp + warn, or AA-landmark build).
3. All other joints = Grood–Suntay JCS with the listed orders (elbow Z–X–Y, radioulnar X–Z–Y); e2 = floating/rotated-distal axis.
4. Scapula = regression constraint (Inman 2:1 default; Ludewig-pattern upgrade path), NOT free bodies, until D-10 data.
5. Elbow = 1-DOF hinge + carrying-angle FUNCTION β(θ) from Wilps means (linear interp 0/30/60/90/120°, SDs as bounds) + axis-tilt constants (14° IR, 40° capitellar flexion, 6–8° trochlear valgus) as FIXED geometry.
6. Forearm = 1-DOF rotation + DRUJ translation q3(φ) from ulnar-variance data (1.34 mm full-scale) + no-fixed-center flag for future centrode upgrade.
7. Wrist = TWO coupled joints (radiocarpal + midcarpal) with split ratios + oblique-axis rotation (26.6°) + Li-coupling (flex↔ulnar, ext↔radial, max-near-neutral scaling).
8. Hand = rigid carpus + 4th/5th-CMC 1-DOF arch + MCP/PIP/DIP hinges (AAOS limits); crushing-grip deformation = CALIBRATION STUB (returns neutral, flagged).
9. Every "UNKNOWN - REQUIRES INVERSE KINEMATICS CALIBRATION" becomes a named calibration input (table/pad geometry + athlete pose priors), defaulting to SAFE anatomical mid-range, never to a guessed match value.
10. No muscle, material, control, or technique quantities in this module. Cross-imports FORBIDDEN.
