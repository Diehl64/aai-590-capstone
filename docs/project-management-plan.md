# Project management plan

This repository follows the Group 1 plan submitted for Assignment 2.1.2. The submitted plan is the source of truth for scope, dates, ownership, and review.

## Scope

The capstone evaluates RF intrusion classification, 77 GHz radar micro-Doppler classification, and thermal/vision feasibility for drone detection. The source datasets are not synchronized. Multisensor work is therefore limited to an evidence-based comparison and local replay; it does not claim measured real-time sensor fusion. Acoustic modeling is out of scope.

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
| 8 | Data leakage, split integrity, and metric checks | Nov 16–18 | Nov 19 | Mostafa | Tony and Jacob |
| 9 | Ethics, limitations, and project risks | Nov 16–18 | Nov 19 | Tony | Jacob |
| 10 | Multisensor comparison and local replay | Nov 16–21 | Nov 22 | Mostafa | Tony and Jacob |
| 11 | Methodology and limitations report sections | Nov 16–21 | Nov 22 | Jacob | Tony |
| 12 | Results, error analysis, and figures | Nov 23–26 | Nov 27 | Tony | Mostafa and Jacob |
| 13 | Repository setup and reproducibility check | Nov 23–26 | Nov 27 | Mostafa | Jacob |
| 14 | Full report draft and integration | Nov 23–28 | Nov 29 | Jacob | Tony and Mostafa |
| 15 | Final report and source/claim review | Nov 30–Dec 1 | Dec 2 | All | Tony, Mostafa, and Jacob |
| 16 | Slides, rehearsal, and presentation recording | Dec 2–4 | Dec 5 | All | Tony, Mostafa, and Jacob |
| 17 | Playback check, final repository review, and submission | Dec 6 | Dec 6 | Tony submits | Mostafa and Jacob |

## Risks and controls

| Risk | Control |
| --- | --- |
| Unsynchronized datasets | Do not claim measured sensor fusion; compare model outputs and use local replay only. |
| Data leakage or invalid splits | Validate source splits, target overlap, preprocessing, and test isolation before reporting metrics. |
| Thermal labels or coverage are insufficient | Limit the work to feasibility analysis or a clearly labeled binary baseline; state the limitation. |
| Late integration or report overload | Draft methods and limitations in Week 5 and results/report sections in Week 6; reserve Week 7 for review and presentation. |
| Ethical or operational overclaim | Frame outputs as decision support, document false-positive/false-negative tradeoffs, and retain a limitations section. |

## Presentation and submission

The team will complete slides by December 4, record by December 5, verify playback, and submit by December 6. The presentation needs at least eight visualizations and at least two speaking minutes from each teammate. Tony is the designated final-submission lead.
