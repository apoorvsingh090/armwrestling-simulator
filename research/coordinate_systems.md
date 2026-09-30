# Coordinate Systems — Upper-Limb Segments for Arm-Wrestling Simulation

Status key per frame/axis: SUPPORTED BY RESEARCH (ISB text or measurement in corpus) /
MODEL DERIVED (Holzbaur/OpenSim convention) / IMPLEMENTATION ASSUMPTION (chosen here for consistency) /
UNKNOWN (corpus does not decide — flagged).

Engine note (all segments): the physics engine MAY integrate in quaternions internally
(IMPLEMENTATION ASSUMPTION — standard practice, not a research claim). All joint angles,
limits, and constraints in this spec are expressed in anatomical Joint Coordinate System (JCS)
terms for interpretation and enforcement. A fixed, documented quaternion↔JCS conversion per
joint is required; Euler-sequence choice must be recorded because sequences can shift reported
angles by up to 50° (F4 [32]).

Global conventions adopted here (IMPLEMENTATION ASSUMPTION, documented for consistency):
- Units: meters, radians (simulator I/O), kilograms, seconds. Source values in degrees/mm are
  converted at the interface; raw values keep native units in parameters.json notes.
- Angle zero standard: clinical zeros (arm anatomical position; elbow 0° = full extension;
  forearm neutral = thumb-to-shoulder; wrist neutral = 3rd metacarpal aligned). The F7 "elbow
  zero = 90° flexion" wording (conflict C-01) is NOT adopted; convert any ISB-text material
  that assumes it.
- Rotation sign: flexion/pronation positive; extension/supination negative. Pronation–supination
  neutral-zero (F6's "0°=supination" grids and Chen "mid-prone 0°" must be transformed on import).
- Handedness: right-handed frames throughout.

---

## 1. Thorax (root / parent of shoulder girdle)

- **Origin:** suprasternal (jugular) notch region per ISB thorax construction (SUPPORTED BY RESEARCH — ISB standard as cited in F4/F7).
- **Axes (ISB):** X anterior, Y superior, Z lateral (right-handed). Anatomical meaning: X = sagittal-forward, Y = axial-up, Z = frontal-lateral.
- **Parent:** world / ground. **Child:** clavicle (via SC joint), scapula functionally.
- **Rotation convention:** thorax is the reference; humeral elevation reported relative to thorax.
- **Zero/reference:** upright anatomical posture.
- **DOFs:** 0 in the arm model (fixed base; whole-body lean for kinetic-chain drive is NOT in the MVP — deferred).
- **Constraints:** none (base).
- **Status:** frame definition SUPPORTED BY RESEARCH (standard); fixing thorax for the MVP is an IMPLEMENTATION ASSUMPTION.

## 2. Clavicle

- **Origin:** sternoclavicular joint center (SUPPORTED — anatomical description F4; Holzbaur segment F2).
- **Axes:** long axis along the bone (medial→lateral), with anterior/superior secondaries per ISB-style construction. Exact axis labels: IMPLEMENTATION ASSUMPTION (corpus gives landmarks, not a full axis triple for the clavicle).
- **Parent:** thorax (SC joint). **Child:** scapula (AC joint).
- **Zero/reference:** anatomical rest length/orientation.
- **DOFs:** limited SC/AC glides/rotations; MVP: rigid or locked (IMPLEMENTATION ASSUMPTION — F4 notes clavicle acts mainly as a strut).
- **Constraints:** scapular-position coupling; no numeric limits in corpus → UNKNOWN.
- **Status:** segment existence SUPPORTED; axis triple and mobility ASSUMPTION.

## 3. Scapula

- **Origin:** acromial angle / acromion (F4: clavicle→acromion linkage; scapulothoracic gliding plane).
- **Axes:** ISB scapular plane construction (SUPPORTED as standard reference; numeric landmarks per ISB, cited F4/F7).
- **Parent:** clavicle (AC) + thorax (scapulothoracic functional articulation — NOT a true synovial joint, F4).
- **Child:** humerus (glenohumeral joint).
- **Zero/reference:** anatomical rest; scapulohumeral rhythm couples scapular orientation to humeral elevation (principle stated, no numeric law in corpus → UNKNOWN quantitatively).
- **DOFs:** MVP: locked or prescribed rhythm (IMPLEMENTATION ASSUMPTION).
- **Constraints:** glenoid contact 25–30% of humeral head (F7 [16]) — stability context, not a numeric constraint law → UNKNOWN as a formula.
- **Status:** functional role SUPPORTED; quantitative rhythm/limits UNKNOWN.

## 4. Humerus

- **Origin:** CONFLICT C-13. F4: medial epicondyle with Y to humeral-head sphere center. F7: humeral-head articular center with X anterior / Y superior / Z lateral.
- **Adopted (IMPLEMENTATION ASSUMPTION):** origin at humeral-head center; X anterior, Y superior (proximal along shaft), Z lateral, right-handed. Rationale: rotation-centered for the GH ball-and-socket; document transform to epicondyle-based reporting.
- **Anatomical meaning:** Y = shaft axis (elevation/rotation reference); X/Z = transverse plane (protraction/rotation decomposition depends on Euler sequence — record it).
- **Parent:** scapula (GH joint). **Child:** ulna + radius (elbow).
- **Rotation convention:** 3 rotational DOFs — plane of elevation, elevation (flexion/extension in scapular plane), axial rotation (IR/ER) per F7/ISB. Sequence must be fixed and logged (50° sensitivity warning, F4 [32]).
- **Positive direction:** elevation +, IR (medial) +; abduction + away from midline.
- **Zero/reference:** arm at side, anatomical neutral (clinical; converts F7's neutral wording).
- **DOFs:** 3 (ball-and-socket). MVP scope: may restrict to elevation + axial rotation if validated against task data (ASSUMPTION — record restriction).
- **Constraints:** anatomical ROM (P001–P005, ACTIVE_ROM general-human). Feasible arm-wrestling envelope UNKNOWN; start posture ≈45° flexion + progressive IR is scenario context (P088), not a constraint law.
- **Status:** DOFs + anatomical ROM SUPPORTED; adopted origin CONVENTION (assumption); task envelope UNKNOWN.

## 5. Ulna

- **Origin:** midway between distal ulna and coronoid process (SUPPORTED — ISB as cited F4).
- **Axes:** +Y proximal along shaft; +X anterior toward ulnar tuberosity; Z = X×Y right-handed (SUPPORTED — ISB exposition F4).
- **Anatomical meaning:** Y = flexion axis reference; X = anterior stability reference (MCL/varus–valgus context).
- **Parent:** humerus (ulnohumeral hinge). **Child:** radius (PRUJ/DRUJ coupling), carpus functionally.
- **Rotation convention:** flexion/extension about the trochlear axis; mean flexion axis varus 3.1±1.9° (P009) with coupled translation/rotation — hinge is approximate.
- **Positive direction:** flexion +. **Zero:** 0° = full extension (clinical; C-01 resolution).
- **DOFs:** ~1 (flexion/extension) + coupled axial micro-motion (F4). MVP: pure 1-DOF hinge (IMPLEMENTATION ASSUMPTION; varus/translation deferred).
- **Constraints:** anatomical 0–145° (P006); feasible placeholder 30–130° (P017, ASSUMPTION); elastic restraint 100 Nm/deg + 0.001745 damping (P021, MODEL DERIVED); carrying-angle/valgus context (P008, REFERENCE).
- **Status:** frame + hinge SUPPORTED; pure-hinge reduction ASSUMPTION; feasible limits ASSUMPTION.

## 6. Radius

- **Origin:** midway between distal radius and proximal radial head (SUPPORTED — ISB as cited F4).
- **Axes:** +Y proximal; +X anterior (SUPPORTED — ISB exposition F4); Z right-handed.
- **Anatomical meaning:** Y = longitudinal rotation axis for pronation/supination (radius rotates about/around ulna; annular ligament + TFCC + interosseous membrane context, F4/F7).
- **Parent:** humerus (radiocapitellar) + ulna (PRUJ/DRUJ). **Child:** carpus/hand (radiocarpal surface).
- **Rotation convention:** ISB intermediate forearm system at neutral (elbow 90°, thumb-to-shoulder); rotation axis aligned with ulnar Y at neutral (SUPPORTED — ISB per F7).
- **Positive direction:** pronation +. **Zero:** neutral (thumb to shoulder).
- **DOFs:** 1 (pronation/supination). Coupled ulnar abd/add during rotation ±5° (F4) — deferred micro-motion.
- **Constraints:** anatomical 76–80° pron / 80–87° sup (P010/P011, ACTIVE_ROM); passive +3–5° (P012); feasible placeholder ±50° (P018, ASSUMPTION).
- **Status:** frame + 1-DOF SUPPORTED; feasible limits ASSUMPTION; coupled ±5° REFERENCE (not implemented in MVP).

## 7. Hand (carpus + metacarpals + lumped digits)

- **Origin (wrist JCS):** center of carpal articular surface of distal radius (SUPPORTED — ISB per F7); wrist center corroborated as FE-axis ∩ mid-styloid sagittal plane (F4 cadaveric, SUPPORTED).
- **Axes:** Y along 3rd metacarpal; Z perpendicular to palmar carpal surface; X = Y×Z (SUPPORTED — ISB exposition F7).
- **Zero:** forearm vertical (palm down) for FE; 3rd metacarpal aligned for deviation (SUPPORTED — ISB per F7); converted to neutral-zero for simulator I/O (ASSUMPTION).
- **DOFs:** 2 (flexion/extension, radial/ulnar deviation); mechanical axes oblique 26.6° (P016) → coupled motion (implement as axis obliquity or note as limitation — ASSUMPTION if simplified to orthogonal).
- **Constraints:** anatomical 80° flex / 70° ext / 20–25° rad / 30–35° uln (P013–P015). Feasible subset is principle-based and partly anomalous in wording (C-20) → UNKNOWN; use flexion-biased functional subset as ASSUMPTION with flag.
- **Lumped contact sub-frames (all ASSUMPTION, posture-dependent, P068–P070):** palm patch (0,0,0.05), finger patch (0,0.08,0.03), thumb patch (0.04,0.06,0.02) m in hand-root frame. Re-register per hand size; recompute r-vectors each step (moment arms change with posture — SUPPORTED principle, F3).
- **Finger/thumb joints:** MCP flexion + IP hinges per ISB (SUPPORTED as definitions); carpus as single rigid body is MODEL DERIVED simplification (F4). MVP: rigid hand + 3 patches (ASSUMPTION, F3 "safe simplification"); articulated digits deferred.
- **Status:** wrist frame + ROM SUPPORTED; obliquity SUPPORTED (implement or document); patches + rigid hand ASSUMPTION.

## Transform checklist (implementation, all ASSUMPTION unless noted)

1. Native-source → simulator-neutral angle maps (F6 grids, Chen mid-prone, F7 elbow-zero text). SUPPORTED source values; maps are implementation.
2. Fixed Euler sequence per joint + logged (sequence sensitivity SUPPORTED, F4 [32]).
3. Quaternion↔JCS conversion tested against restraint boundaries (P021) and ROM bounds (P001–P018).
4. Patch r-vectors recomputed from wrist/forearm posture each step (posture-dependence SUPPORTED, F3).
5. Clavicle/scapula either locked or rhythm-prescribed with the choice logged (ASSUMPTION).

## Forearm-rotation scaffold mapping (added for the rotation subsystem; IMPLEMENTATION CONVENTION, no evidence altered)

- Scalar joint coordinate phi maps to the Radius frame (�6) rotation about +Y_ulna at neutral: phi = 0 neutral, +phi = pronation, SI radians internally (FOREARM_ROTATION_SPEC.md �7). Parent: ulna (elbow subsystem); child: radius/hand. Validity: anatomical +80/-87 deg (P010/P011); feasible +/-50 deg placeholder (P018).

