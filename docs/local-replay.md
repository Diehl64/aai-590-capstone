# Local replay and operator review

Phase 4 begins with a local, recorded or simulated event contract. It does not claim synchronized radar-camera data, geographic tracking, calibrated probabilities, or field deployment.

The current radar and candidate verification datasets capture different events. Replay therefore tests software handling of evidence states, not whether combining sensors improves detection. Any future paired-data fusion experiment must be evaluated separately with its own ground truth.

`src/replay_workflow.py` carries a radar result, an optional verification result, and an operator-review state under one event ID. Verification can be confirmed, conflicting, unavailable, or timed out. Missing verification remains explicit and requires review. A confirmed matching class produces an `accepted` review state; conflicts, timeouts, and unavailable evidence remain `required`. This is orchestration behavior, not ground truth.

Each replay scenario should retain the event ID, source observation ID, timestamp provenance, radar model version, class scores, evidence reference, verification state/reason, and human disposition. Scores are model outputs and must not be described as calibrated probabilities without calibration evidence.

The first scenarios should cover matching evidence, conflicting evidence, missing/timeout evidence, and an event-ID mismatch. Report simulated workflow outcomes separately from the real radar metrics in `docs/radar-model-results.md`. RGB/thermal datasets and Lattice integration remain outside this phase.
