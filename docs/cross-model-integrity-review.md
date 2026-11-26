# Cross-model integrity review

## Purpose and review boundary

This review records the claim controls for the final report and presentation. It is a documentation review of committed component evidence and replay artifacts. It does not rerun, retrain, recalibrate, or combine the component models.

| Review item | Status | Evidence and required final-report treatment |
| --- | --- | --- |
| Radar split and metrics | Reviewed | Report the measurement-disjoint split, 11,050 held-out segments, and component-only metrics. Retain the unresolved session/subject/target-overlap limitation. |
| Thermal Dataset 2 baseline | Reviewed | Report the Dataset 2-only operating point and its separate held-out metrics. Only Dataset 2 supports the stated bird-rejection result. |
| Thermal Dataset 1 follow-on work | Pending team confirmation | Keep Dataset 1 access/reuse, source-specific controls, and final claim eligibility under review. Do not extend the Dataset 2 bird-rejection claim to Dataset 1. |
| Acoustic evaluation | Reviewed with limitation | Separate the clean operating point from controlled-noise evidence. DADS has no source/site identifier, so do not claim unseen-site performance. |
| RF evaluation | Reviewed with limitation | Preserve the selected validation threshold/calibration, the 249 Benign-to-Machine test calls, earlier exploratory test exposure, exact-duplicate sensitivity, and unknown recording/session overlap. `Machine` is a drone-like cue, not a confirmed drone. |
| Saved-output replay | Reviewed | The 25 records pair independent held-out outputs only as scenarios. State that some combinations repeat and that scenario count is not a performance measure. |
| Coordination-agent interface | Reviewed | Preserve the simulated-only schema, mandatory human review, no fused probability, and the radar 0.60 development placeholder. The fixed-rule comparison remains pending in PR #57. |

## Required claim controls

- Keep individual-model metrics in their own modality sections; do not average, pool, or otherwise convert them into a combined metric.
- Call replay outcomes **simulated software behavior**, not sensor-fusion performance, real events, synchronized observations, latency measurements, or field tests.
- State that every replay alert requires operator review and that the project has no autonomous control or response function.
- Describe thresholds according to their source. The RF, acoustic, and thermal operating points have documented validation provenance. The radar 0.60 agent floor is a development placeholder, not a calibrated confidence threshold.
- Treat RF `Machine` as a cue needing corroboration. Do not equate it with a confirmed drone.

## Pre-submission checks

1. Rebase and review PR #57, run it against the committed 25-scenario replay, and retain any early-stop conflict findings in the final narrative.
2. Complete team review of the thermal Dataset 1 access/reuse record and select only approved thermal claims.
3. Verify that the final report, slides, captions, and spoken script use the same component metrics, threshold meanings, and limitations as the cited repository artifacts.
4. Run the full repository test suite at the final `main` commit and record the command, commit, Python environment, pass count, and date.

## Prohibited conclusions

This repository does not support claims of measured synchronized sensor fusion, combined accuracy, combined false-alarm rate, fused probability, continuous operational monitoring, live sensor control, autonomous response, geographic tracking, or field-deployment readiness.
