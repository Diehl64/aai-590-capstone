# AAI-590 Capstone: Multi-Stage Monitoring

University of San Diego — M.S. in Applied Artificial Intelligence

**Team:** Ramon (Tony) Diehl-Verdugo, Mostafa Zamaniturk, and Jacob Tassos.

**Status:** Initial real-data radar audit complete (2026-10-21). Model training and the verification pipeline remain to be implemented. Team scientific review and native Jupyter validation are pending.

## Completed Radar Audit

The checksum-verified dataset contains **130 measurements and 75,868 segments**.

- No nonfinite signal, range, or time values, or negative within-measurement time steps, were found in the checks performed.
- There are 67 edge-marked segments.
- 128 measurements span published splits 1, 2, and 3. Measurement IDs 81 and 92 span only splits 1 and 3.
- Proposed drone/bird/person grouping, excluding reflectors, leaves 72,588 segments, approximately 81% drones. Team approval of these labels remains pending.

All measurements span multiple published splits. The published partition therefore does not evaluate unseen measurements. We need measurement-disjoint evaluation and further checks for session or target overlap. This does not establish that the original study's results are invalid; its evaluation question may differ.

The four notebook Python cells ran sequentially with a Python runner and captured outputs. Native Jupyter kernel startup was blocked in that environment. JupyterLab execution and cross-platform compatibility still need validation. **No classifier performance has been measured.**

Evidence:

- [Audit notebook](notebooks/01_radar_data_audit.ipynb)
- [Results and limitations](results/radar-audit-results.md)
- [Measurement audit](results/radar-measurement-audit.csv) and [class counts](results/radar-class-summary.csv)
- [Source metadata](results/radar-source-metadata.json) and [execution environment](results/radar-audit-environment.json)

## Project Overview

This capstone explores a software pipeline that classifies sensor observations, requests visual verification, and presents evidence and uncertainty to a human operator.

## Continuity from AAI-540 to AAI-590

This capstone builds on the team's [AAI-540 RF Intrusion Detection MLOps project](https://github.com/Mosizamani/aai-540-final-project-group6), retained as a read-only predecessor/reference project. Its reusable foundation includes CNN training and evaluation, dataset and model provenance, SageMaker batch inference, model/data monitoring, and performance-gated CI/CD promotion. These components are candidates for adaptation; they have not been integrated into this repository.

**RF communications data and radar data are separate modalities.** AAI-540 classifies RF activity from spectrogram images into Benign, Broadband_Jam, Human, Machine, Narrowband_Jam, and Wildlife. AAI-590 is auditing complex-valued measurements from a 77 GHz FMCW radar, with a proposed drone/bird/person grouping pending review. Shared label wording does not establish equivalent targets, paired observations, compatible inputs, or transferable performance. AAI-540 weights, preprocessing, thresholds, and metrics do not establish radar classifier performance.

The new AAI-590 contributions are planned radar preprocessing and measurement-disjoint evaluation, a radar baseline and neural network trained from scratch, separately evaluated visual verification, coordination of observation and verification events, and operator review of evidence and uncertainty. Only the initial radar data audit is complete; the models and coordinated demonstration remain to be implemented.

[Phase 1 integration plan](docs/aai-540-integration.md) records source evidence, reuse boundaries, proposed interfaces, and completion criteria. Phase 1 documents continuity and scope; it does not deploy or execute the predecessor's AWS workflows.

## Scope

The proposed proof of concept uses recorded or simulated observations to demonstrate:

1. Radar observation classification.
2. Visual verification using RGB imagery, with thermal imagery as a possible extension.
3. Structured results containing a predicted class, confidence, supporting evidence, and verification status.
4. An operator alert for human review.

Physical drone flight control and interception are outside the capstone implementation scope.

Coordinates, velocity, timestamps, and camera pose must come from an external source or a clearly labeled simulation. The classifier does not produce measured coordinates from classification labels.

## Data and Modeling

Candidate radar data:
https://zenodo.org/records/5896641

Initial integrity and schema checks are complete, and the source metadata identifies CC BY 4.0. Final adoption, class mapping, preprocessing, and evaluation suitability require team review. See the [dataset manifest](data/dataset-manifest.csv) and [audit notes](docs/radar-data-audit.md).

The team will:

- Select suitable radar and visual datasets.
- Document provenance, limitations, and permitted uses.
- Prevent leakage between related recordings in training and test splits.
- Plan a neural network trained from scratch to address the Module 5 learning outcome; clarify any alternative with the instructor.
- Compare model performance against a documented baseline.

Synchronized radar-camera data has not yet been secured. Models using separate real-world datasets will be evaluated separately. Simulated verification scenarios will be identified explicitly.

## Integration

The initial demonstration will use a local replay workflow and structured model outputs.

Integration with Anduril's Lattice sandbox is an optional extension, dependent on access and available interfaces. The core capstone must remain demonstrable without that integration.

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

Tony coordinates repository organization. Technical responsibilities will be agreed upon by the team and tracked through issues and contributions.

Each member contributes to implementation, documentation, and the final presentation. Changes should use focused branches and teammate review.

## Getting Started

Read [SETUP.md](SETUP.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

This repository contains an executed data-audit notebook, derived tables and a figure, provenance records, and planning documents. Download the raw dataset separately using SETUP.md; it is not bundled here. There is no runnable model pipeline or finalized dependency specification yet.

## Next Milestones

1. Review the audit and approve class mapping and reflector treatment in [project decisions](docs/project-decisions.md).
2. Define measurement-disjoint training, validation, and test groups; check class coverage and remaining session overlap.
3. Validate native Jupyter execution and record a tested dependency specification.
4. Inspect more class and edge examples, select preprocessing, and train a baseline and neural network.
5. Evaluate radar classification before adding separately evaluated visual verification and explicitly simulated integration.

Record actual team contributions in [the contribution log](docs/contributions.csv).

## Licensing and AI Assistance

The radar dataset is attributed to Alexander Karlsson (KTH), [DOI 10.5281/zenodo.5896641](https://doi.org/10.5281/zenodo.5896641), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit the source, link the license, and identify modifications when sharing derived material. Verification evidence is in the source metadata linked above.

The team has not selected a software license. The dataset license does not automatically license this repository's code. Review permissions for additional datasets and models before use and redistribution.

Repository preparation, Python audit execution, and documentation used ChatGPT assistance. See [the AI assistance record](docs/ai-assistance.md). The team is responsible for verifying content and following instructor disclosure requirements.
