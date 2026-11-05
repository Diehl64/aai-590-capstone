# Project management plan

This repository follows the Group 1 plan submitted for Assignment 2.1.2. The scope was revised twice: on 2026-11-01 to add binary acoustic drone detection, and again before the plan submission to add a human-in-the-loop coordination agent. Both revisions were agreed by Tony, Mostafa, and Jacob. This document is the source of truth for current scope, dates, ownership, and review.

## Scope

The capstone evaluates RF intrusion classification, 77 GHz radar micro-Doppler classification, thermal/vision feasibility for drone detection, and binary acoustic drone detection. Acoustic modeling may add controlled environmental noise to audio samples to test whether classification remains reliable under more realistic operating conditions. The source datasets are not synchronized, so multisensor work is limited to an evidence-based comparison and local replay. It does not claim measured real-time sensor fusion.

The capstone also develops a human-in-the-loop agent that coordinates these models. The agent:

- decides which sensor evidence to request based on the observations already received;
- assembles a structured alert with per-sensor predictions, confidence scores, cited evidence, and a confirmed, conflicting, unknown, or unverified status; and
- routes every alert to operator review.

The agent cannot control sensors or drones or initiate any response. It is evaluated on explicitly simulated replay scenarios against a fixed rule-based baseline and does not report a fused detection probability. See [agent-coordination.md](agent-coordination.md).

**Future work outside the capstone:**

- training the evidence-combination component on synchronized multi-sensor data;
- LLM-generated operator reports; and
- integration of AWS model-health and IoT device-health information.

## Workflow

GitHub Projects is the team Kanban board. Work moves from **To do** to **In progress**, **Review**, and **Done**. A task is done only after the assigned reviewer records feedback and the owner resolves it.

- Model and final-deliverable rows use two reviewers to check metrics, claims, figures, and reproducibility.
- No result enters the report until leakage, split integrity, metrics, and limitations are reviewed.

## Schedule and ownership

| No. | Project section | Owner window | Review window | Owner | Reviewer |
| ---: | --- | --- | --- | --- | --- |
| 1 | Introduction and scope | Oct 19–23 | Oct 24–25 | All | Jacob |
| 2 | Management plan and GitHub Project | Oct 26–30 | Oct 31–Nov 1 | Tony | Jacob |
| 3 | Radar data audit, cleaning, EDA, and data summary | Nov 2–6 | Nov 7–8 | Mostafa | Jacob |
| 4 | Literature review and methods decisions | Nov 2–12 | Nov 13–15 | Jacob | Tony |
| 5 | RF v4 versus v5 evaluation and error analysis | Nov 9–13 | Nov 14–15 | Mostafa | Tony and Jacob |
| 6 | Acoustic drone-detection model evaluation and noise robustness | Nov 9–13 | Nov 14–15 | Mostafa | Tony and Jacob |
| 7 | Radar model evaluation and limitations | Nov 9–13 | Nov 14–15 | Tony | Mostafa and Jacob |
| 8 | Thermal vision planning and data prep | Nov 2–6 | Nov 7–8 | Jacob | Tony and Mostafa |
| 9 | Thermal vision training and evaluation | Nov 9–13 | Nov 14–15 | Jacob | Tony and Mostafa |
| 10 | Agent interface: shared sensor record, alert schema, and status rules | Nov 9–11 | Nov 12 | Mostafa | Tony and Jacob |
| 11 | Agent implementation: evidence-request policy, rule-based baseline, review gate, and audit log | Nov 12–18 | Nov 19 | Mostafa | Tony and Jacob |
| 12 | Data leakage, split integrity, and metric checks | Nov 16–18 | Nov 19 | Mostafa | Tony and Jacob |
| 13 | Ethics, limitations, and project risks | Nov 16–18 | Nov 19 | Tony | Jacob |
| 14 | Multisensor comparison and local replay, including agent versus rule-based baseline evaluation | Nov 16–21 | Nov 22 | Mostafa | Tony and Jacob |
| 15 | Methodology and limitations report sections | Nov 16–21 | Nov 22 | Jacob | Tony |
| 16 | Results, error analysis, and figures | Nov 23–26 | Nov 27 | Tony | Mostafa and Jacob |
| 17 | Repository setup and reproducibility check | Nov 23–26 | Nov 27 | Mostafa | Jacob |
| 18 | Full report draft and integration | Nov 23–28 | Nov 29 | Jacob | Tony and Mostafa |
| 19 | Final report and source/claim review | Nov 30–Dec 1 | Dec 2 | All | Tony, Mostafa, and Jacob |
| 20 | Slides, rehearsal, and presentation recording | Dec 2–4 | Dec 5 | All | Tony, Mostafa, and Jacob |
| 21 | Playback check, final repository review, and submission | Dec 6 | Dec 6 | Tony submits | Mostafa and Jacob |

## Risks and controls

| Risk | Control |
| --- | --- |
| Unsynchronized datasets | Do not claim measured sensor fusion; compare model outputs and use local replay only. |
| Data leakage or invalid splits | Validate source splits, target overlap, preprocessing, and test isolation before reporting metrics. |
| Thermal labels or coverage are insufficient | Limit the work to feasibility analysis or a clearly labeled binary baseline; state the limitation. |
| Acoustic evaluation does not prove new-site performance | Preserve recording-level splits, document source/site limitations, and avoid claims beyond the evaluated dataset. |
| Late integration or report overload | Draft methods and limitations in Week 5 and results/report sections in Week 6; reserve Week 7 for review and presentation. |
| Ethical or operational overclaim | Frame outputs as decision support, document false-positive/false-negative tradeoffs, and retain a limitations section. |
| Agent scope creep (e.g., LLM orchestration) | Deliver the rule-based agent and baseline comparison first; treat LLM reporting as future work; give the agent no response or actuator tools. |
| Model outputs not ready for agent integration | Build against the replay contract with labeled placeholders; agree on the shared record schema by Nov 11; mark late model scores as uncalibrated. |

## Presentation and submission

The team will complete slides by December 4, rehearse before recording, record by December 5, verify playback, and submit by December 6. The presentation needs at least eight visualizations and at least two speaking minutes from each teammate. Tony is the designated final-submission lead.
