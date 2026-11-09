# Project management plan

This repository follows the Group 1 plan submitted for Assignment 2.1.2. The plan's scope was revised on 2026-11-01 to add acoustic modeling after the team identified completed acoustic-model work. This document is the source of truth for current scope, dates, ownership, and review.

## Scope

The capstone evaluates RF intrusion classification, 77 GHz radar micro-Doppler classification, thermal/vision feasibility for drone detection, and acoustic drone-sound detection. The source datasets are not synchronized. Multisensor work is therefore limited to an evidence-based comparison and local replay; it does not claim measured real-time sensor fusion.

## Workflow

GitHub Projects is the team Kanban board. Work moves from **To do** to **In progress**, **Review**, and **Done**. A task is done only after the assigned reviewer records feedback and the owner resolves it.

## Schedule and ownership

| No. | Project section | Owner window | Review window | Owner | Reviewer |
| ---: | --- | --- | --- | --- | --- |
| 1 | Introduction and scope | Oct 19–23 | Oct 24–25 | All | Jacob |
| 2 | Management plan and GitHub Project | Oct 26–30 | Oct 31–Nov 1 | Tony | Jacob |
| 3 | Radar data audit, cleaning, EDA, and data summary | Nov 2–6 | Nov 7–8 | Mostafa | Jacob |
| 4 | Literature review and methods decisions | Nov 2–12 | Nov 13–15 | Jacob | Tony |
| 5 | RF v4 versus v5 evaluation and error analysis | Nov 9–13 | Nov 14–15 | Mostafa | Tony and Jacob |
| 6 | Radar model evaluation and limitations | Nov 9–13 | Nov 14–15 | Tony | Mostafa and Jacob |
| 7 | Thermal vision data and model feasibility | Nov 9–13 | Nov 14–15 | Jacob | Tony |
| 8 | Acoustic model evidence and robustness review | Nov 9–13 | Nov 14–15 | Mostafa | Tony and Jacob |
| 9 | Data leakage, split integrity, and metric checks | Nov 16–18 | Nov 19 | Mostafa | Tony and Jacob |
| 10 | Ethics, limitations, and project risks | Nov 16–18 | Nov 19 | Tony | Jacob |
| 11 | Multisensor comparison and local replay | Nov 16–21 | Nov 22 | Mostafa | Tony and Jacob |
| 12 | Methodology and limitations report sections | Nov 16–21 | Nov 22 | Jacob | Tony |
| 13 | Results, error analysis, and figures | Nov 23–26 | Nov 27 | Tony | Mostafa and Jacob |
| 14 | Repository setup and reproducibility check | Nov 23–26 | Nov 27 | Mostafa | Jacob |
| 15 | Full report draft and integration | Nov 23–28 | Nov 29 | Jacob | Tony and Mostafa |
| 16 | Final report and source/claim review | Nov 30–Dec 1 | Dec 2 | All | Tony, Mostafa, and Jacob |
| 17 | Slides, rehearsal, and presentation recording | Dec 2–4 | Dec 5 | All | Tony, Mostafa, and Jacob |
| 18 | Playback check, final repository review, and submission | Dec 6 | Dec 6 | Tony submits | Mostafa and Jacob |

## Current execution status (2026-11-08)

This status records repository evidence without changing the approved schedule or ownership above. A task remains in progress until its listed review is complete.

| Project area | Repository status | Remaining action |
| --- | --- | --- |
| Management plan and GitHub Project | Plan, issues, and review workflow are committed. | Jacob records review feedback. |
| Radar audit and data summary | Audit, measurement-disjoint split, baseline, CNN, metrics, tests, report figures, error analysis, and held-out output handoff are committed. | Obtain reviewer feedback and document the remaining session/subject/target-overlap limitation. |
| RF v4 versus v5 | Comparison evidence and RF dataset provenance are committed. The team branch contains calibration and held-out-output export code. | Commit the existing saved RF held-out outputs, configuration, metrics, and provenance; do not retrain solely for handoff. |
| Radar evaluation and limitations | Validated 11,050-row held-out output handoff, report figures, and error analysis are committed. | Obtain reviewer feedback. |
| Thermal/vision feasibility | A validated 2,631-row held-out thermal handoff is committed; the source pipeline remains on the team branch. | Review the full pipeline, environment, data-access/license evidence, curated error-analysis figures, and final thermal manifest entry. |
| Acoustic evidence and robustness | Acoustic Transformer, CNN, and Random Forest baseline notebook is committed on the team branch. | Commit optimized-model comparison, controlled-noise evidence, metrics, and held-out outputs. |
| Local replay | A ten-scenario partial replay using real radar and thermal held-out outputs is committed; every case is simulated and requires human review. | Add RF and acoustic held-out outputs, then run the planned four-sensor simulated scenarios. |
| Coordination-agent comparison | Coordination rules are documented, and an interface with tests exists on the team agent branch. | Create a focused agent-only PR, approve validation-based per-sensor thresholds, and run the scheduled comparison with fixed rules. |

## Weekly status snapshot

Status meaning: 🟢 is committed and documented repository evidence; 🟡 is active work or review still needed; 🔴 has no committed implementation evidence.

| Project area | Status | Committed evidence | Next action |
| --- | --- | --- | --- |
| Scope and project plan | 🟢 Complete | Scope, schedule, risks, ethics, and limitations are documented. | Record team review feedback. |
| Radar audit and model | 🟢 Complete | Audit, grouped split, baseline, RadarCNN, metrics, figures, error analysis, and 11,050 held-out outputs are committed. | Obtain reviewer feedback and integrate into the report. |
| Thermal-IR | 🟡 In progress | A validated 2,631-row held-out handoff and baseline evidence are committed. | Complete provenance/access entry, environment details, curated error figures, and review. |
| RF v4 versus v5 | 🟡 In progress | Comparison evidence is committed; calibration and held-out-output export code exists on the team branch. | Commit the saved held-out RF CSV, configuration, metrics, and provenance without retraining solely for handoff. |
| Acoustic | 🟡 In progress | Transformer, CNN, and Random Forest baselines plus a padding-shortcut check exist on team branches. | Commit optimized comparison, controlled-noise evidence, metrics, and held-out outputs. |
| Simulated replay | 🟡 In progress | Ten simulated scenarios, real radar/thermal outputs, and a scenario-status figure are committed. | Add real RF/acoustic outputs and run the four-sensor replay. |
| Coordination agent | 🟡 In progress | Coordination-agent interface and tests exist on the team branch. | Open a focused agent-only PR, approve validation-based thresholds, and compare with fixed rules. |
| Literature and methods | 🔴 Not started in repository | No committed report source exists. | Complete Jacob’s draft and review. |
| Leakage and integrity review | 🔴 Not started | No final cross-model integrity review artifact exists. | Review split integrity, preprocessing, and metrics after remaining artifacts arrive. |
| Final report and slides | 🔴 Not started | No report or presentation source exists. | Start after methods and remaining outputs are ready. |

This snapshot does not change the approved schedule or ownership. The replay remains explicitly simulated, and it does not establish measured real-world sensor fusion or combined accuracy.

## Risks and controls

| Risk | Control |
| --- | --- |
| Unsynchronized datasets | Do not claim measured sensor fusion; compare model outputs and use local replay only. |
| Data leakage or invalid splits | Validate source splits, target overlap, preprocessing, and test isolation before reporting metrics. |
| Thermal labels or coverage are insufficient | Limit the work to feasibility analysis or a clearly labeled binary baseline; state the limitation. |
| Acoustic evaluation does not prove new-site performance | Preserve recording-level splits, document source/site limitations, and avoid claims beyond the evaluated dataset. |
| Late integration or report overload | Draft methods and limitations in Week 5 and results/report sections in Week 6; reserve Week 7 for review and presentation. |
| Ethical or operational overclaim | Frame outputs as decision support, document false-positive/false-negative tradeoffs, and retain a limitations section. |

## Presentation and submission

The team will complete slides by December 4, record by December 5, verify playback, and submit by December 6. The presentation needs at least eight visualizations and at least two speaking minutes from each teammate. Tony is the designated final-submission lead.
