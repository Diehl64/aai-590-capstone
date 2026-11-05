# Human-in-the-loop coordination agent

This document specifies the capstone's coordination agent (plan rows 10, 11, and 14). It turns the scope statement in the submitted introduction and management plan into implementable rules. Any change to this scope must be recorded in [project-decisions.md](project-decisions.md).

## Purpose

The agent coordinates the separately evaluated RF, radar, thermal/vision, and acoustic models. It does not run every model in a fixed sequence. Instead, it chooses which evidence to request next based on the observations already received. Every event ends as a structured alert for operator review.

## Authority boundary

- The agent may only request model evidence, wait for it, and submit an alert for review.
- It has no sensor-control, drone-control, countermeasure, or response tools. This boundary is enforced by the absence of such tools in code, not only by policy text.
- Every alert has `review_required: true`. No status, including `confirmed`, clears or escalates an event without a human disposition.

## Inputs

- Saved held-out model outputs that follow the [model-output handoff](model-output-handoff.md) schema, or labeled development placeholders.
- A simulated event that assigns those outputs to one event ID. Because the datasets are not synchronized, this association is defined by the scenario author, not inferred by the agent, and every event is marked `simulated: true`.
- Per-record arrival time, so evidence can arrive late or not at all within the event deadline.

## Shared label mapping

Each modality keeps its own labels. The agent maps them to a common hypothesis for status rules only:

| Modality | Source labels | Agent hypothesis |
| --- | --- | --- |
| RF | Benign, Broadband_Jam, Narrowband_Jam, Human, Machine, Wildlife | Machine → `drone_like`; Human, Wildlife → `not_drone`; Benign → `not_drone`; jamming classes → `other` |
| Radar | drone, bird, human | drone → `drone_like`; bird, human → `not_drone` |
| Thermal/vision | drone, no drone | drone → `drone_like`; no drone → `not_drone` |
| Acoustic | drone, no-drone | drone → `drone_like`; no-drone → `not_drone` |

A record whose score falls inside its modality's documented uncertainty band maps to `uncertain`. Bands are set from validation data, never from the test split. The final mapping is fixed in plan row 10.

## Alert status

| Status | Rule (initial proposal, finalized in row 10) |
| --- | --- |
| `confirmed` | At least two independent modalities report `drone_like` and no available modality reports `not_drone`. |
| `conflicting` | Available modalities disagree between `drone_like` and `not_drone`. |
| `unverified` | Expected evidence is missing, delayed past the deadline, or low quality, and the remaining evidence cannot reach `confirmed`. |
| `unknown` | All available evidence is `uncertain` or `other`. |

The existing `replay_workflow.VerificationStatus` and `synthetic_replay.EvidenceStatus` values map to these statuses. They are not replaced.

## Policies compared

- **Fixed rule-based baseline:** request every modality, wait until the deadline, then apply the status rules.
- **Agent policy:** request evidence sequentially. For example, request radar or acoustic evidence when RF is uncertain in the Benign/Machine region, and stop early once the status can no longer change.

## Alert content

Each alert contains the event ID, simulated flag, status, per-sensor prediction, score, calibration flag, model version, evidence reference, missing or delayed sensors, the agent's request sequence, and the operator disposition field.

## Scores

Scores are raw model outputs unless the model owner commits calibration evidence, such as temperature scaling fitted on the validation split with reported expected calibration error. Each alert records `score_calibrated: true/false` per sensor. The agent never computes a fused detection probability.

## Audit log

Every request, arrival, timeout, status decision, and operator disposition is logged with its timestamp and reason.

## Evaluation (row 14)

All metrics are measured on simulated replay scenarios only:

- status accuracy against each scenario's expected status;
- evidence requests per event;
- time to alert;
- review-gate and authority violations (target: zero).

Results are reported separately from per-model metrics and do not establish real-world fusion performance.

## Future work (outside the capstone)

- Training the evidence-combination component on synchronized multi-sensor recordings.
- Refinement from real-world operator feedback.
- LLM-generated operator reports that add AWS model-health and IoT device-health information.
