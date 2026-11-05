# Project decisions

This file separates current direction from decisions still requiring team agreement.

## Current direction

- Team: Tony, Mostafa, and Jacob.
- Tony intends to coordinate GitHub for the capstone.
- Software and AI proof of concept building on the AAI-540 project.
- RF intrusion classification, radar micro-Doppler classification, thermal/vision feasibility, binary acoustic drone detection with noise-robustness checks, a human-in-the-loop coordination agent, evidence-based comparison, and human-reviewed alerts.
- The agent has no response or actuator tools and is evaluated only on simulated replay against a fixed rule-based baseline. See [agent-coordination.md](agent-coordination.md).
- Anduril Lattice integration is an optional extension that depends on verified sandbox access. It is not part of the submitted core deliverables, and the core demonstration must remain locally executable.

## Open decisions

| Decision | Evidence needed | Owner/status |
| --- | --- | --- |
| Initial classes: drone/bird/person and unknown handling | Research objective and compatible labels | Team / open |
| Radar dataset and relation to AAI-540 inputs | Actual data audit, schema, provenance, permissions | Team / open |
| Thermal/vision feasibility dataset | Access, labels, license, compute assessment | Jacob / scheduled Nov 9–15 |
| Real paired radar-camera data | Synchronized observations and ground truth, or explicitly limited simulation | Team / open |
| Baseline and neural-network method | Literature, data fit, training feasibility | Team / open |
| Python/framework versions | Tested shared environment | Team / open |
| Evaluation and acceptance criteria | Baseline, split plan, metric definitions, uncertainty tests | Tony proposes; team agrees / open |
| Repository license and publication | Team agreement and third-party rights review | Team / open |
| Acoustic model evidence | Reproducible code, source/license record, split evidence, metrics, noise-robustness results, and limitation review | Mostafa / scheduled Nov 9–15 |
| Agent label mapping, status rules, and uncertainty bands | Validation-split outputs from each modality and team review | Mostafa / scheduled Nov 9–12 |
| Score calibration claim | Per-model temperature scaling on the validation split and reported calibration error, or scores labeled uncalibrated | Each model owner / before row 14 |
| Lattice integration | Verified sandbox access and tested interface | Optional extension; not a core deliverable |

## Phase 2 proposal

- Proposed first task: map D1–D6 to `drone`, all bird labels to `bird`, and human_run/human_walk to `human`.
- Corner reflector (`CR`) remains explicit and excluded from the three-class metrics; it is not silently treated as unknown.
- Use the committed measurement-disjoint manifest in `data/radar-split-manifest.csv` (seed 590; target 70%/15%/15% by segment count).
- The split prevents measurement-ID leakage, but session, subject, or target overlap across measurement IDs remains unverified and must be reported as a limitation.
- Baseline: training-only magnitude statistics with a nearest-centroid classifier. Report accuracy, macro F1, per-class precision/recall/F1, and a confusion matrix.
- The neural network must be trained from scratch after baseline review; its framework and architecture remain open.

## Data and claim boundaries

The proposed KTH data consists of target-centered radar scan segments. It is not automatically a source of complete 3D trajectories, calibrated uncertainty, or continuous negative surveillance periods. Any simulated tracks must be labeled. Real model metrics and simulated integration behavior should be reported separately.

Two model outputs agreeing does not establish ground truth. Define verification states, thresholds, and human-review behavior explicitly. Validate using held-out observations and account for shared recording groups to reduce leakage.

The RF, radar, thermal/vision, and acoustic datasets capture different events and are not synchronized. Evaluate each model independently. Use simulated scenarios only for evidence-based comparison and operator-review behavior. Do not claim measured real-time fusion or improved real-world detection without suitable paired observations.

## Submitted management-plan scope

The current plan includes RF classification, radar classification, thermal/vision feasibility, binary acoustic drone detection, the human-in-the-loop coordination agent, and local replay. The acoustic addition is a documented scope revision dated 2026-11-01. The agent addition was agreed by the full team and included in the submitted introduction and Assignment 2.1.2 plan. The dated ownership and review windows are in [project-management-plan.md](project-management-plan.md).

## Decision log

When the team resolves an item, record the date, decision, rationale, evidence link, and participants here. No architecture or dataset is approved merely because it appears in this scaffold.

| Date | Decision | Rationale | Evidence | Participants |
| --- | --- | --- | --- | --- |
| 2026-11-01 | Add binary acoustic drone detection to scope | Completed acoustic-model work identified | [acoustic-model-evidence.md](acoustic-model-evidence.md) | Tony, Mostafa, Jacob |
| 2026-11 (before plan submission) | Add human-in-the-loop coordination agent; LLM reporting, AWS model-health, and IoT device-health integration are future work | Coordinates separately evaluated models without claiming fusion; addresses RF Benign/Machine ambiguity | Submitted introduction and Assignment 2.1.2 plan; [agent-coordination.md](agent-coordination.md) | Tony, Mostafa, Jacob |
