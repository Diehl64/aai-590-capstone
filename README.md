# AAI-590 Capstone: Multi-Stage Monitoring

University of San Diego — M.S. in Applied Artificial Intelligence

**Team:** Ramon (Tony) Diehl-Verdugo, Mostafa Zamaniturk, and Jacob Tassos.

**Status (2026-11-26):** Radar, thermal, acoustic, and RF evaluation evidence and held-out output handoffs are committed on `main`. Radar figures and error analysis, four thermal experiments, acoustic robustness checks, and RF validation selection, calibration, and duplicate sensitivity records are available for team review. The committed saved-output replay contains 25 explicitly simulated four-sensor records; it is not a measurement of synchronized sensor fusion or combined accuracy. The coordination-agent interface and tests are also committed. The remaining integration is the agent run and fixed-rule-versus-cascade comparison in PR #57, followed by final scientific review and report/presentation assembly.

## Completed Radar Audit

The checksum-verified dataset contains **130 measurements and 75,868 segments**.

- No nonfinite signal, range, or time values, or negative within-measurement time steps, were found in the checks performed.
- There are 67 edge-marked segments.
- 128 measurements span published splits 1, 2, and 3. Measurement IDs 81 and 92 span only splits 1 and 3.
- The proposed three-class mapping is drone, bird, and human; reflectors are explicitly excluded, leaving 72,588 segments.

All measurements span multiple published splits. The published partition therefore does not evaluate unseen measurements. The capstone uses a measurement-disjoint split; session or target overlap remains a limitation. This does not establish that the original study's results are invalid; its evaluation question may differ.

The audit was followed by a measurement-disjoint nearest-centroid baseline and a from-scratch CNN. The CNN was trained on an RTX 5080 with PyTorch CUDA and evaluated once on the untouched test partition. See the [model results](docs/radar-model-results.md). These are target-centered dataset results, not continuous field-detection performance.

Evidence:

- [Audit notebook](notebooks/01_radar_data_audit.ipynb)
- [Results and limitations](results/radar-audit-results.md)
- [Measurement audit](results/radar-measurement-audit.csv) and [class counts](results/radar-class-summary.csv)
- [Source metadata](results/radar-source-metadata.json) and [execution environment](results/radar-audit-environment.json)

## Project Overview

This capstone explores a software pipeline that classifies sensor observations, requests visual verification, and presents evidence and uncertainty to a human operator.

## Continuity from AAI-540 to AAI-590

This capstone builds on the team's [AAI-540 RF Intrusion Detection MLOps project](https://github.com/Mosizamani/aai-540-final-project-group6), retained as a read-only predecessor/reference project. Its reusable foundation includes CNN training and evaluation, dataset and model provenance, SageMaker batch inference, model/data monitoring, and performance-gated CI/CD promotion. AAI-590 documents the RF v4/v5 evaluation evidence and dataset provenance; the predecessor's SageMaker deployment, monitoring, and CI/CD system have not been integrated into this repository.

**RF communications data and radar data are separate modalities.** AAI-540 classifies RF activity from spectrogram images into Benign, Broadband_Jam, Human, Machine, Narrowband_Jam, and Wildlife. AAI-590 evaluates complex-valued measurements from a 77 GHz FMCW radar using the documented drone/bird/human mapping and explicit reflector exclusion. Shared label wording does not establish equivalent targets, paired observations, compatible inputs, or transferable performance. AAI-540 weights, preprocessing, thresholds, and metrics do not establish radar classifier performance.

The new AAI-590 contributions include radar preprocessing and measurement-disjoint evaluation, separately evaluated thermal-IR and acoustic models, the RF v5 Machine-screen evidence package, simulated replay using saved outputs, and a committed coordination-agent interface. The agent's comparison with fixed rules remains pending in PR #57.

The remaining scope and dated ownership are recorded in the [project management plan](docs/project-management-plan.md). The local comparison uses explicitly simulated replay scenarios and does not claim measured sensor fusion.

The [synthetic local-replay foundation](docs/synthetic-replay.md) provides an RF/radar/thermal/acoustic event contract and five placeholder-only development scenarios. These are separate from the committed [saved-output replay](docs/real-output-replay.md), which provides 25 four-sensor records (not 25 distinct evidence combinations). The RF CSV is already committed; no model training or invented RF predictions were used for this integration. Every scenario remains simulated and requires human review.

The committed handoffs contain 11,050 radar outputs, 2,631 thermal decisions, 57,015 acoustic outputs, and 2,400 RF outputs. See the [radar](docs/radar-model-results.md), [thermal](docs/thermal_ir_pipeline.md), [acoustic](docs/acoustic-model-evidence.md), and [RF](docs/rf-v4-v5-evidence.md) evidence. RF `Machine` is a mechanical/UAV-like cue requiring corroborating evidence and operator review, not a confirmed drone. Keep each model's metrics and limitations separate from replay results.

The radar and any future verification datasets capture different events and are not synchronized. They therefore cannot establish that sensor fusion improves real-world detection. We evaluate each model independently and use clearly labeled simulated scenarios to test agreement, conflict, missing evidence, and delayed verification. Claims about combined performance require suitable paired observations and will not be made from the current datasets.

[Phase 1 integration plan](docs/aai-540-integration.md) records source evidence, reuse boundaries, proposed interfaces, and completion criteria. Phase 1 documents continuity and scope; it does not deploy or execute the predecessor's AWS workflows.

## Scope

The proposed proof of concept uses recorded or simulated observations to demonstrate:

1. RF intrusion-classification evaluation.
2. Radar observation classification.
3. Thermal/vision feasibility for drone detection.
4. Acoustic drone-sound detection.
5. Structured results containing a predicted class, model score with its calibration status, supporting evidence, and verification status.
6. An operator alert for human review.

Physical drone flight control and interception are outside the capstone implementation scope.

Coordinates, velocity, timestamps, and camera pose must come from an external source or a clearly labeled simulation. The classifier does not produce measured coordinates from classification labels.

## Data and Modeling

Evaluated radar dataset:
https://zenodo.org/records/5896641

The [thermal-IR pipeline and evaluation record](docs/thermal_ir_pipeline.md) documents data provenance, license status, notebook order, held-out results, and error-analysis artifacts. The [Thermal Dataset Exploration notebook](notebooks/03_thermal_dataset_exploration.ipynb) documents Dataset 2 recording counts, durations, annotation issues, bounding-box geometry, target location, and temporal dependence, plus Dataset 1 source characteristics and a descriptive cross-source comparison.

Radar integrity checks, class mapping, preprocessing, and evaluation are documented, and the source metadata identifies CC BY 4.0. Team review must retain the remaining session/subject/target-overlap limitation. See the [dataset manifest](data/dataset-manifest.csv) and [audit notes](docs/radar-data-audit.md).

Remaining data and evidence review:

- Confirm unresolved provenance, limitations, and permitted uses, especially thermal Dataset 1.
- Review split integrity, including RF exact duplicates and unavailable recording/session identifiers, without claiming the checks prove independent recordings.
- Carry radar, thermal, acoustic, and RF error analysis and limitations into the report.
- Complete thermal provenance/access review and report integration, and extend the local replay without implying paired real-world sensor data.

Synchronized radar-camera data has not yet been secured. Models using separate real-world datasets will be evaluated separately. Simulated verification scenarios will be identified explicitly.

## Integration

The demonstration uses a local simulated replay workflow and structured saved model outputs. The four-sensor replay and coordination-agent interface are committed; review the agent's fixed-rule comparison before presenting it as a completed result. The RF Machine threshold and calibrated scores must retain their documented meaning; the radar 0.60 agent score floor remains a development placeholder until supported by validation evidence.

Live sensor control, Lattice integration, interception, cloud deployment, and real-time field testing are outside this capstone's implementation scope.

## Repository Structure

| Location | Purpose |
|---|---|
| `data/` | Dataset documentation and provenance manifest |
| `docs/` | Course requirements, decisions, contributions, and AI assistance |
| `notebooks/` | Data exploration, training, and evaluation notebooks |
| `src/` | Reusable Python implementation |
| `results/` | Experiment results, metrics, and figures |
| `reports/` | Report, presentation, and submission materials |
| `CONTRIBUTING.md` | Team development and review workflow |
| `SETUP.md` | Setup and onboarding guidance |
| `.gitignore` | Git exclusions for local and generated files |

## Evaluation

Planned evaluation includes:

- Per-class precision, recall, and F1.
- Confusion matrices and baseline comparisons.
- Processing latency on documented hardware.
- Handling of uncertain, conflicting, or missing evidence.
- Reproducible experiments with documented data splits and configurations.

Final metrics and acceptance criteria require team agreement informed by the audit. Report macro F1 and per-class recall alongside accuracy to account for class imbalance.

Target-centered classification samples alone cannot establish continuous perimeter detection performance or false alerts per operating hour. Those metrics require suitable continuous observations and ground truth.

## Team Workflow

Tony coordinates repository organization. Technical responsibilities are recorded in the project management plan and tracked through issues and contributions.

Each member contributes to implementation, documentation, and the final presentation. Changes should use focused branches and teammate review.

## Getting Started

Read [SETUP.md](SETUP.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

This repository contains the executed audit, split manifest, baseline and CNN code, measured results, provenance records, and planning documents. Download the raw dataset separately using SETUP.md; it is not bundled here.

## Next Milestones

1. Rebase, review, and run the coordination agent on the committed four-sensor replay; record the fixed-rule comparison while preserving RF class/score semantics.
2. Complete cross-model integrity and reproducibility review, retaining RF duplicate/test-exposure limitations and each modality's generalization limits.
3. Confirm thermal Dataset 1 access/reuse terms and approve final thermal report claims.
4. Complete results/figures and reproducibility work by November 26, with review November 27. Integrate the existing [report outline](reports/final-report-outline.md), [radar methods/results](reports/radar-methodology-results.md), and [claims matrix](reports/claims-evidence-matrix.md) into the full draft by November 28, with review November 29.
5. Finish report/source review and presentation deliverables during Week 7, November 30–December 6, following the project management plan. Record outstanding team signoffs rather than treating a merged artifact as final scientific approval.

Record actual team contributions in [the contribution log](docs/contributions.csv).

## Licensing and AI Assistance

The radar dataset is attributed to Alexander Karlsson (KTH), [DOI 10.5281/zenodo.5896641](https://doi.org/10.5281/zenodo.5896641), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit the source, link the license, and identify modifications when sharing derived material. Verification evidence is in the source metadata linked above.

The Thermal-IR work records two separate sources. Dataset 1 is the [Official Dataset Release for the 4th Anti-UAV Challenge](https://doi.org/10.5281/zenodo.15103888), version 1.0.0, published by China Telecom. Its files are restricted and its Zenodo Rights → License field was blank when checked on 2026-11-15; confirm access, reuse, and redistribution permission before sharing source or derived image data. Dataset 2 is [DroneDetectionThesis/Drone-detection-dataset](https://github.com/DroneDetectionThesis/Drone-detection-dataset), whose repository [LICENSE](https://github.com/DroneDetectionThesis/Drone-detection-dataset/blob/master/LICENSE) is CC0 1.0 Universal. Cite the source as requested by its repository. Detailed access, version, split, and permission notes are in [the dataset manifest](data/dataset-manifest.csv).

The team has not selected a software license. The dataset license does not automatically license this repository's code. Review permissions for additional datasets and models before use and redistribution.

Repository preparation, Python audit execution, and documentation used ChatGPT assistance. See [the AI assistance record](docs/ai-assistance.md). The team is responsible for verifying content and following instructor disclosure requirements.
