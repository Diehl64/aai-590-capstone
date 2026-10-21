# AAI-590 Capstone: Multi-Stage Monitoring

**Project status: Planned — repository scaffold; models and experiments are not yet implemented.**

This University of San Diego MS in Applied Artificial Intelligence capstone explores a software pipeline for classifying sensor observations, requesting visual verification, and presenting evidence and uncertainty to a human operator. The team is Ramon Antonio Diehl-Verdugo (Tony), Mostafa Zamaniturk, and Jacob Tassos.

## Objective and scope

The proposed system combines radar classification with visual verification using recorded or simulated observations. Initial outputs will include a predicted class, confidence, evidence, and a verification state. Exact classes, datasets, models, and acceptance criteria remain team decisions.

The capstone ends with an operator alert. Physical flight control and interception are future work. Position, velocity, camera pose, and timestamps must come from an external system or a clearly labeled simulation; the classifier does not create measured coordinates.

## Relationship to AAI-540

This project builds on the team's [AAI-540 RF Intrusion Detection MLOps project](https://github.com/Mosizamani/aai-540-final-project-group6). That repository documents six-class RF spectrogram classification, CNN training, batch inference, monitoring, and promotion workflows. It remains a separate record of the earlier course.

No previous notebooks, data, models, or results have been copied into this scaffold. Before reusing material, document the source commit, its license or permission, the changes, and the original contribution made in AAI-590. RF communications data and radar measurements must not be treated as interchangeable inputs.

## Candidate methods and data

- Radar: [KTH 77 GHz FMCW measurements](https://zenodo.org/records/5896641), subject to a data and licensing audit.
- Vision: select a suitable RGB dataset first; thermal data remains a proposed extension.
- Models: include at least one neural network/deep learning model and actual training or fine-tuning. Architecture selection follows the literature review and data audit.
- Integration: local replay and structured output first; Anduril Lattice sandbox integration is optional and access-dependent.

There is no secured synchronized radar-camera test set documented here. Evaluate each real-data model separately. Label simulated fusion results explicitly and do not present them as measured real-world fusion improvement.

## Repository guide

| Path | Purpose |
| --- | --- |
| `README.md` | Project overview and entry point |
| `SETUP.md` | Repository creation, local setup, and onboarding |
| `CONTRIBUTING.md` | Branches, reviews, notebook handling, and contribution evidence |
| `.gitignore` | Excludes local credentials, datasets, caches, and model binaries from normal Git staging |
| `.github/ISSUE_TEMPLATE/task.md` | Task template with owner, evidence, and completion criteria |
| `.github/pull_request_template.md` | Change summary, validation, and review checklist |
| `docs/course-requirements.md` | Confirmed requirements and weekly milestones |
| `docs/project-decisions.md` | Provisional scope and unresolved decisions |
| `docs/contributions.csv` | Individual contribution record |
| `docs/ai-assistance.md` | Record of AI assistance and human review |
| `data/README.md` | Dataset acquisition and split documentation rules |
| `data/dataset-manifest.csv` | Dataset provenance, rights, and access inventory |
| `notebooks/README.md` | Suggested notebook sequence covering the required workflow |
| `src/README.md` | Location for reusable Python implementation |
| `results/README.md` | Experiment evidence and result naming rules |
| `reports/README.md` | Report, presentation, and final export guidance |

Update this table whenever a file is added so the README continues to describe the code base.

## Getting started

Read [SETUP.md](SETUP.md), then [CONTRIBUTING.md](CONTRIBUTING.md). The scaffold has no executable model pipeline or dependency lock file. Add and document the actual environment when the first implementation is selected and tested; do not imply that training can run from this initial scaffold.

## Evaluation

Record per-class precision and recall, confusion counts, baseline comparisons, and processing latency on documented hardware. Validate uncertainty thresholds without using the final test set for tuning. Establish a split strategy that accounts for related samples from the same recording.

Target-centered radar samples alone do not establish continuous perimeter detection probability or false alerts per operating hour. Operational metrics require suitable continuous observations and ground truth. Each result must identify its data source, split, model version, configuration, and whether it is measured or simulated.

## Team workflow

Tony coordinates repository organization and reviews. Implementation ownership will be agreed by the team and recorded in issues. Each teammate contributes through their own account and reviews another member's changes. Everyone contributes to code, report, and presentation; repository coordination does not replace technical participation.

## License and acknowledgments

The team has not selected a license. Do not represent this repository as open source or redistribute third-party assets until the team has reviewed the applicable permissions. Public datasets and model weights may carry separate restrictions.

Repository scaffold drafting used ChatGPT assistance. See [the assistance record](docs/ai-assistance.md). The team remains responsible for verification, original work, and the instructor's disclosure requirements.
