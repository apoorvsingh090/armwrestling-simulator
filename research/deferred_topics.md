# Deferred Topics — Not Sufficiently Established for Implementation

Everything below is UNKNOWN or ASSUMPTION-grade in the corpus. Items are ordered by
implementation impact. Each entry states what is missing, why it blocks, and what evidence
would unblock it. Nothing here may be silently promoted into the build.

## D-01. In-competition arm-wrestling dataset (BLOCKING for validation; not for MVP build)
- **Missing:** synchronized 3D kinematics + kinetics (joint torques, hand forces) + EMG during actual matches across techniques and phases.
- **Why it blocks:** caps every sport-specific claim at Partially Validated/Unvalidated (F2/F5); no technique-specific torque, timing, or recruitment magnitude can be asserted.
- **Unblocks with:** marker-based motion capture + force/instrumented table + EMG + synchronized video events, with full metadata (population, n, config, uncertainty) per F5 test template.

## D-02. Target-interface friction laws (BLOCKING for contact credibility)
- **Missing:** μs/μk/vs for skin-on-skin and skin-on-table under match loads, velocities, moisture (D-01's tribology counterpart).
- **Why it blocks:** contact torque magnitude/failure (slip) predictions rest on proxies (C-07/C-08); no slip/grip outcome is defensible.
- **Unblocks with:** tribometer Stribeck curves (temp/humidity-controlled) + pendulum/CMA-ES system-ID + HM/ABC calibration (F3 §5).

## D-03. Patch-resolved grip-force distribution under arm-wrestling postures
- **Missing:** how total grip splits across palm/fingers/thumb during hook/top-roll/press postures; quantitative wrist-coupling law S(θ) (form + coefficients).
- **Why it blocks:** R_i and S(θ) are placeholders (P072/P073); cupping/rising/containment mechanics cannot be quantified.
- **Unblocks with:** instrumented dynamometer at imposed wrist/forearm postures + torque-direction studies extended to arm-wrestling grips (F3/F5).

## D-04. Elite arm-wrestler muscle architecture and morphology
- **Missing:** PCSA, fiber length, pennation, moment-arm-relevant geometry, humeral cross-sections in elite/professional arm wrestlers.
- **Why it blocks:** Tier3 numbers are double-extrapolated assumptions (P031); bone-remodeling is pure hypothesis (F4 §tiers).
- **Unblocks with:** MRI/DTI + ultrasound architecture study on ranked competitors; pQCT humeral geometry; cadaveric Tier3 specimens (F4 future work).

## D-05. Tendon properties (slack, compliance, damping) for arm muscles
- **Missing:** tendon-slack lengths beyond two Holzbaur fits; SEE/SDE curves; damping values; dynamic pennation during contraction.
- **Why it blocks:** forces the rigid-vs-compliant fork to stay a scoped trade-off (C-09) with ~20% MAE hanging over dynamics; stretch-shortening and force-lag phenomena unavailable.
- **Unblocks with:** ultrasound-based MTU tracking during arm-wrestling-relevant tasks + parameter-sensitivity-ranked calibration (F4/F6).

## D-06. Hand/wrist biomechanics detail
- **Missing:** intrinsic-hand muscle roles and MCP/IP containment mechanics; TFCC/annular-ligament load behavior; ECU-vs-pronation full surface; APL/thumb force paths; C-20 wrist-subset anomaly resolution.
- **Why it blocks:** rigid-hand + 3-patch model cannot predict finger-level failure, fine pressure effects, or thumb-cupping torques quantitatively.
- **Unblocks with:** finger-resolved dynamometry + wrist-simulator sweeps over pronation (extending Chen protocol) + thumb-kinematics study.

## D-07. Injury mechanics as implementable rules
- **Missing:** validated bone/ligament/cartilage constitutive laws under arm-wrestling-rate torsional + valgus loads; subject-specific failure thresholds; MCL/LUCL/TFCC force–length + zero-load lengths.
- **Why it blocks:** FE fracture band (50–71 Nm) and ligament strengths are context, not damage criteria; any "injury prediction" now would be unvalidated.
- **Unblocks with:** rate-dependent tissue testing + validated FE with uncertainty + prospective injury-data linkage. DO NOT IMPLEMENT YET (see IMPLEMENTATION_READINESS.md).

## D-08. Neural control beyond lumped loops
- **Missing:** recruitment order, feedforward/feedback gains, inter-muscular coordination patterns, and reflex parameters specific to arm-wrestling phases; k_noise values; 4CCr rate constants for arm muscles; central-vs-peripheral weighting under match duty cycles.
- **Why it blocks:** controller can execute prescribed strategies but cannot claim human-like coordination, learning, or fatigue dynamics.
- **Unblocks with:** high-density EMG + perturbation studies + fitted activation/fatigue models; offline Huxley/extended-Hill cross-checks (F1/F7).

## D-09. Fatigue dynamics for match durations
- **Missing:** arm-muscle fatigability, recovery time constants, and task-dependence (isometric hold vs concentric attack) in competitors.
- **Why it blocks:** 4CCr integration would be decorative without rate/recovery data; long-match outcomes indefensible.
- **Unblocks with:** sustained-MVC + intermittent-duty protocols on elbow/wrist/pronation muscles with central/peripheral separation.

## D-10. GH and wrist stability boundaries (feasible-ROM laws)
- **Missing:** load-dependent safe envelopes for shoulder IR under compression/torsion and wrist under cupping/rising loads; scapular-rhythm law for the task.
- **Why it blocks:** feasible ROM stays ADL-placeholder (C-18); aggressive techniques could demand non-physiological poses the simulator cannot flag.
- **Unblocks with:** passive torque–angle + stability testing in arm-wrestling-relevant configurations (F5-Tier4 extended).

## D-11. Kinetic-chain (legs/trunk) contribution in arm wrestling
- **Missing:** any arm-wrestling measurement of proximal-segment energy/force transfer (the 51–55% figure is tennis).
- **Why it blocks:** back/side pressure and shoulder-commitment power cannot be apportioned; MVP correctly excludes the lower body.
- **Unblocks with:** full-body kinetics during matches (force plates + trunk kinematics).

## D-12. Individualisation and variability distributions
- **Missing:** population joint distributions (not just means/SDs) for PCSA, MA, ROM, friction, and segment inertia in relevant cohorts.
- **Why it blocks:** Monte-Carlo/variability claims rest on assumed CVs (10–20% MA precedent is the only solid anchor, P049).
- **Unblocks with:** aggregated datasets with documented ethnicity/sex/age/training strata (F4/F5 metadata standard).

## D-13. Smartphone/markerless roles beyond event/sync
- **Missing:** any evidence phones can validate continuous arm-wrestling kinematics (current errors 12–30°, threshold <5° unmet, P086).
- **Decision:** DEFER as kinematics source indefinitely; retain only event detection + TTL/clap sync + secondary velocity (P086).

## D-14. Advanced controllers (MPC, optimal-control extensions, learned policies)
- **Missing:** validated baseline to extend; task-specific cost functions; sim-to-real transfer evidence for this domain.
- **Decision:** DEFER until MVP baseline is Validated/Partially-Validated; RL explicitly excluded for phase 1 per F1/F2; optimal control stays an offline trajectory/parameter tool.
