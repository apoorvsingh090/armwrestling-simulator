# NEXT RESEARCH BATCH — exact Deep Research questions, dependency order

Answer each with: values + units + population (sex/age/n) + method + source/DOI +
uncertainty; or an explicit "not found in literature" (a documented negative IS
an acceptable answer — it confirms UNKNOWN). No adjacent-domain borrowing without
a transfer-validity argument. No technique narratives as numbers.

## Batch 1 (P0/P1 — unblocks numerical rotation + passive + elbow constants)

1. **Rotation MA surfaces.** Report measured forearm rotation (pronation/supination)
   moment arms for pronator teres, pronator quadratus, supinator, and biceps
   (supination MA) as functions of elbow flexion AND forearm rotation (Murray
   tendon-excursion protocol or Holzbaur-model exports with grid ranges). Required:
   per-posture means + SDs + specimen n + angle conventions + validity ranges.
   Unblocks: A-MA, coupling coefficients, E-12 length laws. Accept fitted
   polynomial/Hermite coefficients with AICc + RMS if raw exports unavailable.
2. **PT/PQ/supinator architecture + dynamics.** Report PCSA, optimal fiber length,
   pennation, tendon slack, and (if available) vmax/FL/FV parameters for pronator
   teres, pronator quadratus, and supinator from cadaveric or imaging studies
   (dissection + laser-diffraction standard as in [92]). Unblocks: A-muscles.
3. **Passive rotation + elbow curves.** Report passive pronation/supination and
   elbow flexion/extension torque–angle curves (stiffness + damping) with posture
   conditions and specimen details. Unblocks: G (replaces PROV-09-class surrogates).
4. **Specific tension + Hill constants for arm muscles.** Report specific tension
   (N/cm²), FL width, and vmax values measured or calibrated for biceps, triceps,
   brachialis, pronator teres (human arm; state transfer limits if from lower
   limb). Unblocks: F (replaces PROV-01/02/03). A documented "no human-arm value
   exists" answer is acceptable and preserves PROVISIONAL status honestly.
5. **Elbow↔pronation 2-D coupling numbers.** From the same sources as Q1, report
   how biceps flexion MA varies with supination angle and how supination MA varies
   with elbow angle (tabulated, ≥3×3 postures). Unblocks: coupling channel values.

## Batch 2 (P1 — wrist + shoulder minimum)

6. **Wrist MA + architecture minimum.** Report wrist-muscle (FCR/FCU/ECU/ECRL/ECRB)
   moment arms over (FE × RUD × pronation) and PCSA/Lopt for ≥1 wrist muscle,
   extending the Chen wrist-simulator protocol. Include ECU-vs-pronation surface
   status and the C-20 wrist-subset wording provenance if traceable.
7. **GH minimum.** Report shoulder internal-rotation moment arms + rotator-cuff
   architecture in arm-wrestling-relevant postures, plus any measured scapular-
   rhythm relationship for humeral elevation with load. State stability-boundary
   results if any exist (else document negative).

## Batch 3 (P2 — contact; parallelizable after Batch 1)

8. **Skin friction laws.** Report Stribeck parameters (μs/μk/vs) for skin-on-skin
   (palmar) and skin-on-table/play-surface under 50–500 N normal loads with
   moisture conditions, from tribometer studies (NOT catalog single-μ values).
9. **Grip distribution + S(θ).** Report patch-resolved (palm/fingers/thumb) grip
   force splits and wrist-posture scaling curves with functional forms fitted to
   data (form + coefficients, not assumed bells).
10. **Table + implement metrology.** Report competition table surface friction,
    elbow-pad force data, and pad/edge geometry effects if measured anywhere.

## Batch 4 (P3 — sport dataset design; methods research, not numbers)

11. **D-01 protocol precedents.** Report published synchronized mocap + force +
    EMG match-measurement protocols for grappling/combat sports (sensor lists,
    sync methods, reported uncertainties) suitable as a template for an
    arm-wrestling D-01 study. Deliverable is a shopping-list protocol, not data.
12. **Validation-threshold transfer.** Report whether gait-derived residual gates
    (P083-class) have sport-specific counterparts in upper-limb inverse dynamics,
    or document the negative (justifying the Partially-Validated cap).

## Stop rule
Do not proceed to Batch N+1 implementation until Batch N answers are registered
in `parameters.json` (or confirmed UNKNOWN in this register). Interleave batches
only for interface/scaffold work, which needs no numbers.
