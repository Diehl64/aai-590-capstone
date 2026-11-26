# Project management plan

This repository follows the Group 1 plan submitted for Assignment 2.1.2. The plan's scope was revised on 2026-11-01 to add acoustic modeling after the team identified completed acoustic-model work. This document is the source of truth for current scope, dates, ownership, and review.

## Scope

The capstone evaluates RF intrusion classification, 77 GHz FMCW radar classification, thermal/vision feasibility for drone detection, and acoustic drone-sound detection. The radar classifier uses signal-magnitude inputs; these are not calibrated micro-Doppler features. The source datasets are not synchronized. Multisensor work is therefore limited to an evidence-based comparison and explicitly simulated local replay with mandatory human review; it does not claim measured real-time sensor fusion or combined detection accuracy.

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

## Current execution status (2026-11-25)

This status records evidence committed on `main` at `5fc4dca`, plus clearly identified work under review, without changing the approved schedule or ownership above. Completed component work is distinguished from remaining integration and scientific review. Review-branch changes and open PRs are not treated as merged deliverables.

| Project area | Repository status | Remaining action |
| --- | --- | --- |
| Management plan and GitHub Project | Plan, issues, and review workflow are committed. | Jacob records review feedback. |
| Radar audit and data summary | Audit, measurement-disjoint split, baseline, CNN, metrics, tests, report figures, error analysis, and held-out output handoff are committed. | Record reviewer feedback and retain the documented session/subject/target-overlap limitation in the report. |
| RF v4 versus v5 | PR #54 is merged: comparison evidence, 2,400 held-out outputs, selected configuration, validation threshold/calibration, class semantics, and exact-duplicate sensitivity are committed. | Review the RF cue and score handling in replay/agent integration. Preserve the Benign-to-Machine trade-off, earlier exploratory test exposure, exact duplicates, and unknown recording/session overlap in report claims. No retraining is required for handoff. |
| Radar evaluation and limitations | Validated 11,050-row held-out output handoff, report figures, and error analysis are committed. | Obtain reviewer feedback. |
| Thermal/vision feasibility | The 2,631-row Dataset 2 baseline handoff, full pipeline, four held-out experiments, EDA, and source-specific error panels are committed through PR #58. | Confirm Dataset 1 access/reuse terms, review experiment controls and figures, then approve which results may enter the final report. |
| Acoustic evidence and robustness | Optimized CNN-Tuned comparison, controlled-noise/padding/fill-source checks, figures, and 57,015 held-out outputs are committed. The documented clean-validation operating threshold is 0.344. | Record reviewer feedback and retain the full-length-window headline, padding caveat, and unavailable source/site labels in the report. |
| Local replay | Main at `5fc4dca` has 16 simulated radar/thermal/acoustic saved-output scenarios. All four handoffs are committed. The integration from PR #55 is prepared and tested on `tony/replay-integration-review`: 25 four-sensor records (including a repeated evidence combination), 37 passing unit tests, and successful two-/three-/four-sensor checks. The separate placeholder runner has five development cases. | Obtain teammate review before merging and retain the RF cue semantics. Every case remains simulated and requires human review. |
| Coordination-agent comparison | Coordination rules, interface, and tests are available for review in PR #56; integration and the fixed-rule comparison remain pending. | Review compatibility with the replay, verify per-sensor score semantics, and run the comparison. Keep the radar 0.60 floor labeled as a development placeholder unless validation evidence supports it. |
| Report preparation | A final-report outline, claims/evidence matrix, and radar methodology/results source are committed. PR #59 proposes carrying the merged RF limitations into the report plan. | Complete literature/methods review, integrate the full draft, and review the report and slides; no complete final report or slide source is recorded yet. |

Week 6 is **November 23–29**. Results/figures and reproducibility work are due November 26, with review November 27; the integrated full draft is due November 28, with review November 29. Record any outstanding integrity/ethics reviews scheduled for November 19 and methodology/replay reviews scheduled for November 22. Week 7 remains November 30–December 6 for final review, presentation, and submission.

## Weekly status snapshot

Status meaning: ✅ Complete requires committed and documented evidence; 🟡 In progress or In review means implementation, integration, or signoff remains; ⬜ Not started means no implementation artifact is recorded. Component evidence can be committed while the broader task remains in review.

| Project area | Status | Committed evidence | Next action |
| --- | --- | --- | --- |
| Scope and project plan | ✅ Complete | Scope, schedule, risks, ethics, and limitations are documented. | Record team review feedback. |
| Radar audit and model | ✅ Complete | Audit, grouped split, baseline, RadarCNN, metrics, figures, error analysis, and 11,050 held-out outputs are committed. | Record reviewer feedback and integrate into the report. |
| Thermal-IR | 🟡 In review | Full pipeline, four experiments, error panels, and the 2,631-row Dataset 2 handoff are committed. | Confirm Dataset 1 access/reuse terms, complete team review, and approve final report claims. |
| RF v4 versus v5 | 🟡 In review | Comparison, validation-selection/calibration evidence, duplicate sensitivity, and 2,400 held-out outputs are committed. | Review integration semantics and final claims; Machine remains a cue requiring corroboration and operator review. |
| Acoustic | 🟡 In review | Baselines, optimized comparison, robustness checks, metrics, figures, and 57,015 held-out outputs are committed. | Record review and carry the padding/source-site limitations into the report. |
| Simulated replay | 🟡 In progress | Sixteen three-sensor saved-output cases and five separate placeholder cases are committed; all four output handoffs are available. | Review the tested 25-record integration on the review branch before merging; this is not the agent-versus-fixed-rule comparison. |
| Coordination agent | 🟡 In progress | Interface and tests exist on the agent branch; PR #56 is open. | Complete integration review and the fixed-rule comparison; resolve or disclose placeholder thresholds. |
| Literature and methods | 🟡 In progress | Report outline, claims matrix, radar methods/results, and modality documentation exist. | Complete the literature/methods sections and record review; issue closure alone does not demonstrate signoff. |
| Leakage and integrity review | 🟡 In progress | Modality split checks and RF duplicate sensitivity are committed. | Complete and record cross-model review of split integrity, preprocessing, metrics, and unresolved limits. |
| Full report | 🟡 In progress | Outline, claims matrix, and radar methods/results provide draft sources. | Integrate the full draft by November 28 and review November 29. |
| Slides and recording | ⬜ Not started in repository | No slide or recording source is recorded. | Prepare the reviewed presentation during Week 7. |

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
