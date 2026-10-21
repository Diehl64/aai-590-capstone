# Project decisions

This file separates current direction from decisions still requiring team agreement.

## Current direction

- Team: Tony, Mostafa, and Jacob.
- Tony intends to coordinate GitHub for the capstone.
- Software and AI proof of concept building on the AAI-540 project.
- Classification, verification, evidence, uncertainty, and human-reviewed alerts.
- Stages 3–4 remain future work.
- Lattice integration depends on access; a local workflow provides a fallback.

## Open decisions

| Decision | Evidence needed | Owner/status |
| --- | --- | --- |
| Initial classes: drone/bird/person and unknown handling | Research objective and compatible labels | Team / open |
| Radar dataset and relation to AAI-540 inputs | Actual data audit, schema, provenance, permissions | Team / open |
| First RGB dataset and any thermal extension | Access, labels, license, compute assessment | Team / open |
| Real paired radar-camera data | Synchronized observations and ground truth, or explicitly limited simulation | Team / open |
| Baseline and neural-network method | Literature, data fit, training feasibility | Team / open |
| Python/framework versions | Tested shared environment | Team / open |
| Evaluation and acceptance criteria | Baseline, split plan, metric definitions, uncertainty tests | Tony proposes; team agrees / open |
| Repository license and publication | Team agreement and third-party rights review | Team / open |
| Lattice integration | Verified sandbox access and tested interface | Tony / access not verified here |

## Data and claim boundaries

The proposed KTH data consists of target-centered radar scan segments. It is not automatically a source of complete 3D trajectories, calibrated uncertainty, or continuous negative surveillance periods. Any simulated tracks must be labeled. Real model metrics and simulated integration behavior should be reported separately.

Two model outputs agreeing does not establish ground truth. Define verification states, thresholds, and human-review behavior explicitly. Validate using held-out observations and account for shared recording groups to reduce leakage.

## Decision log

When the team resolves an item, record the date, decision, rationale, evidence link, and participants here. No architecture or dataset is approved merely because it appears in this scaffold.
