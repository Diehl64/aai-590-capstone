# Ethics, limitations, and project risks

## Intended use and human responsibility

This capstone is a human-in-the-loop decision-support proof of concept for counter-UAS monitoring. It classifies individual sensor observations and presents evidence for operator review. It does not autonomously control sensors, direct aircraft, trigger enforcement actions, or authorize any response.

Every replay alert requires human review. An operator must consider the available evidence, missing or delayed inputs, confidence limitations, and local operating context before making a decision.

## Evidence and claim boundaries

RF, radar, thermal, and acoustic datasets capture different observations and are not synchronized. Their outputs may be placed together only in scenarios labeled `simulated`. The replay demonstrates software behavior under agreement, conflict, missing evidence, and delayed evidence. It does not measure real-world sensor fusion, prove sensor association, establish combined accuracy, or show operational detection performance.

Individual model metrics remain separate from replay results. A high single-model score does not establish that a prediction is correct in a new environment or that two sensors observing different datasets confirm the same real-world event.

## Error and operational risks

False positives could cause unnecessary operator workload or attention toward benign activity. False negatives could fail to surface a drone-like observation for review. The radar held-out test results show that human segments can be predicted as drones, so radar alerts require careful operator review.

Raw model scores are not automatically calibrated probabilities. Score thresholds and label mappings must be supported by validation evidence and reviewed separately for each modality. Missing, delayed, low-quality, or conflicting evidence must remain visible to the operator rather than being converted into a silent decision.

## Data, privacy, and provenance

The KTH 77 GHz radar dataset is documented as CC BY 4.0 and must retain its required attribution and modification disclosure. RF, thermal, and acoustic datasets require their own license, access, and provenance review before final reporting or redistribution.

Raw datasets, model weights, credentials, and local paths remain outside GitHub unless the team verifies that sharing is permitted. The repository should contain only small derived results and documentation needed for reproducibility.

## Risk controls

| Risk | Control |
| --- | --- |
| Unsynchronized sensor datasets | Use only explicitly simulated replay scenarios; do not claim measured fusion. |
| False positives or false negatives | Show individual evidence, error analysis, and require operator review. |
| Leakage or overstated generalization | Use documented held-out splits, preserve recording or measurement grouping, and state unresolved overlap limitations. |
| Uncalibrated scores or unsupported thresholds | Label raw scores clearly and select thresholds using validation evidence. |
| Missing, delayed, or conflicting evidence | Represent the condition explicitly and keep the alert open for human review. |
| Dataset-rights or privacy concerns | Document provenance and permissions; keep raw data and sensitive files outside the repository. |
| Scope expansion into field operations | Keep the project to offline evaluation and local simulated replay. |

## Residual limitations

The project does not establish continuous surveillance performance, false alerts per operating hour, geographic tracking, field readiness, or effectiveness in a live counter-UAS operation. Those claims would require appropriately collected, paired observations, operational ground truth, and a separate safety and governance review.
