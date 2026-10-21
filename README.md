# AAI-590 Capstone: Multi-Stage Monitoring

University of San Diego — M.S. in Applied Artificial Intelligence

**Team:** Ramon Antonio Diehl-Verdugo (Tony), Mostafa Zamaniturk, and Jacob Tassos.

**Status:** Planning and repository setup. Models and experiments have not yet been implemented.

## Project Overview

This capstone explores a software pipeline that classifies sensor observations, requests visual verification, and presents evidence and uncertainty to a human operator.

The project builds on our AAI-540 RF Intrusion Detection MLOps project:
https://github.com/Mosizamani/aai-540-final-project-group6

The capstone will document its original contributions and distinguish RF communications data from radar measurements.

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

Dataset selection remains subject to inspection of labels, access rights, licensing, and suitability for evaluation.

The team will:

- Select suitable radar and visual datasets.
- Document provenance, limitations, and permitted uses.
- Prevent leakage between related recordings in training and test splits.
- Train or fine-tune at least one neural network.
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

Final metrics and acceptance criteria will be agreed upon after the data audit.

Target-centered classification samples alone cannot establish continuous perimeter detection performance or false alerts per operating hour. Those metrics require suitable continuous observations and ground truth.

## Team Workflow

Tony coordinates repository organization. Technical responsibilities will be agreed upon by the team and tracked through issues and contributions.

Each member contributes to implementation, documentation, and the final presentation. Changes should use focused branches and teammate review.

## Getting Started

Read [SETUP.md](SETUP.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

This repository currently contains planning materials and an initial folder structure. There is no runnable model pipeline or finalized dependency specification yet.

## Licensing and AI Assistance

The team has not selected a software license. Dataset and model permissions must be reviewed before third-party assets are redistributed.

Repository preparation used ChatGPT assistance. See [the AI assistance record](docs/ai-assistance.md). The team is responsible for verifying content and following instructor disclosure requirements.
