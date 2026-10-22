# AAI-590 Capstone: Multi-Stage Monitoring

University of San Diego — M.S. in Applied Artificial Intelligence

**Team:** Ramon (Tony) Diehl-Verdugo, Mostafa Zamaniturk, and Jacob Tassos.

**Status:** Radar audit, measurement-disjoint baseline, and from-scratch CNN evaluation are complete. Visual verification, coordination, and operator-review workflow remain future work.

## Completed Radar Audit

The checksum-verified dataset contains **130 measurements and 75,868 segments**.

- No nonfinite signal, range, or time values, or negative within-measurement time steps, were found in the checks performed.
- There are 67 edge-marked segments.
- 128 measurements span published splits 1, 2, and 3. Measurement IDs 81 and 92 span only splits 1 and 3.
- The proposed three-class mapping is drone, bird, and human; reflectors are explicitly excluded, leaving 72,588 segments.

All measurements span multiple published splits. The published partition therefore does not evaluate unseen measurements. We need measurement-disjoint evaluation and further checks for session or target overlap. This does not establish that the original study's results are invalid; its evaluation question may differ.

The audit was followed by a measurement-disjoint nearest-centroid baseline and a from-scratch CNN. The CNN was trained on an RTX 5080 with PyTorch CUDA and evaluated once on the untouched test partition. See the [model results](docs/radar-model-results.md). These are target-centered dataset results, not continuous field-detection performance.

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

The new AAI-590 contributions now include radar preprocessing, measurement-disjoint evaluation, a radar baseline, and a neural network trained from scratch. Separately evaluated visual verification, coordination of observation and verification events, and operator review remain future work.

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
- Extend the measured radar comparison with error analysis and robustness checks.
- Build the local replay and operator-review workflow without implying paired real-world radar-camera data.

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

This repository contains the executed audit, split manifest, baseline and CNN code, measured results, provenance records, and planning documents. Download the raw dataset separately using SETUP.md; it is not bundled here.

## Next Milestones

1. Review the measured radar results, error patterns, and the remaining session/subject/target-overlap limitation.
2. Add report-ready methodology, results, figures, and a reviewed dependency specification.
3. Add meaningful split, schema, and metric tests.
4. Build a local replay and operator-review demonstration; keep simulated coordination separate from measured radar metrics.
5. Evaluate visual verification separately only after its data, labels, and permissions are established.

Record actual team contributions in [the contribution log](docs/contributions.csv).

## Licensing and AI Assistance

The radar dataset is attributed to Alexander Karlsson (KTH), [DOI 10.5281/zenodo.5896641](https://doi.org/10.5281/zenodo.5896641), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit the source, link the license, and identify modifications when sharing derived material. Verification evidence is in the source metadata linked above.

The team has not selected a software license. The dataset license does not automatically license this repository's code. Review permissions for additional datasets and models before use and redistribution.

Repository preparation, Python audit execution, and documentation used ChatGPT assistance. See [the AI assistance record](docs/ai-assistance.md). The team is responsible for verifying content and following instructor disclosure requirements.
