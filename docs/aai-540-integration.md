# AAI-540 foundation and AAI-590 integration plan

## Phase 1 scope and evidence

Phase 1 documents project continuity, reusable components, and the capstone's new contributions. It adds no model implementation, artifact migration, AWS deployment, or claimed radar/visual performance. The initial radar audit is complete; team scientific review, radar modeling, visual verification, and the coordinated demonstration remain outstanding.

The [AAI-540 RF Intrusion Detection MLOps repository](https://github.com/Mosizamani/aai-540-final-project-group6) is a read-only predecessor/reference project. This inventory was checked against commit [`4187e05489ba1bbaeb3a73ef95633d248b31fcb8`](https://github.com/Mosizamani/aai-540-final-project-group6/tree/4187e05489ba1bbaeb3a73ef95633d248b31fcb8). Reviewing its code and saved outputs does not independently reproduce its experiments. No predecessor notebooks or AWS-mutating cells were executed for Phase 1.

Source links below are relative to that pinned [reference tree](https://github.com/Mosizamani/aai-540-final-project-group6/tree/4187e05489ba1bbaeb3a73ef95633d248b31fcb8):

| Component | Predecessor evidence | Candidate adaptation for AAI-590 |
| --- | --- | --- |
| CNN training and evaluation | `RF_Intrusion_02_Local_Training_CNN_v1_and_v2.ipynb`, `RF_Intrusion_05_CNN_v3_v4_Training_and_Evaluation.ipynb`; baseline/improved CNN metadata JSON | Reuse experiment organization, architecture comparisons, per-class metrics, confusion matrices, early stopping, and artifact metadata. Design radar features and input shapes separately; train and evaluate new models. |
| Data and inference MLOps | `RF_Intrusion_03_Data_Lake_v2_Training_and_Baseline_Batch_Transform.ipynb`, assignment/Athena metadata CSVs | Adapt provenance records, split manifests, versioned artifacts, and batch input/output contracts. S3, Athena, and SageMaker Batch Transform are optional deployment patterns; the capstone starts with local replay. |
| Model and data monitoring | `RF_Intrusion_04_Model_and_Data_Monitoring.ipynb`, `monitoring_baseline.json` | Adapt schema/missing-value checks, confidence and class-distribution monitoring, baseline comparisons, and PASS/ALERT reports. CloudWatch alarms/dashboard and S3 report uploads are optional cloud extensions. Establish new baselines for each capstone modality. |
| CI/CD promotion | `RF_Intrusion_06_v3_v4_CI_CD_Promotion_and_Batch_Transform.ipynb` | Adapt candidate validation, evaluation/package steps, accuracy and macro-F1 gates, failure reporting, registry provenance, and promotion only after passing checks. This is a notebook-driven SageMaker promotion workflow for uploaded artifacts, not automatic retraining or an installed capstone GitHub Actions workflow. |
| Configuration and runtime separation | `README.md`, `.config/project.example.json` | Reuse separation of personal settings from code and explicit runtime prerequisites. Do not copy account-specific S3 locations, role ARNs, credentials, or deployment identities. |

The predecessor documents local Docker/NVIDIA TensorFlow training for notebooks 02/05 and SageMaker Studio/AWS workflows for 01/03/04/06. These requirements do not become capstone prerequisites merely through this reference. Notebook 06 promotes an already-trained candidate; its intentionally weak v3 demonstrates rejection and v4 demonstrates the passing path. Its saved outcomes and thresholds apply to that RF experiment, not to radar readiness.

## Keep the data modalities separate

| Property | AAI-540 predecessor | AAI-590 radar candidate |
| --- | --- | --- |
| Data and task | RF communications/activity classification from spectrogram images; notebook 01 references Kaggle `hector484/unified-multi-class-rf-intrusion-dataset` | Reflected measurements from a 77 GHz FMCW radar; [Zenodo record 5896641](https://zenodo.org/records/5896641) |
| Representation | Image inputs; retained baseline metadata specifies 128 × 128 RGB inputs | Complex-valued segments of 1,280 values, arranged as five range cells × 256 azimuth samples, plus range/time/split/edge metadata |
| Labels | Benign, Broadband_Jam, Human, Machine, Narrowband_Jam, Wildlife | Fine labels include drone types, birds, human motion, and a corner reflector; proposed drone/bird/person grouping excludes reflectors and awaits team approval |
| Partition evidence | Predecessor documents a 40/10/10/40 train/validation/test/production layout | Audit found all 130 measurements span multiple published splits; measurement-disjoint evaluation and further session/target overlap checks are required |
| Measured capability | Predecessor RF experiments and saved evaluation artifacts | Initial integrity/schema audit: 130 measurements and 75,868 segments; no classifier performance measured |

Both modalities involve radio-frequency signals, but communications activity classification and radar reflection classification have different acquisition processes, inputs, labels, and evaluation questions. A Human or Wildlife RF label is not interchangeable with a radar person or bird label. No shared event identity, synchronization, or geographic tracking follows from label similarity.

Do not copy RF image normalization, augmentation, split ratios, class mapping, model weights, confidence cutoffs, or monitoring/promotion thresholds into radar experiments without a documented rationale and independent validation. A magnitude image of a radar segment is not automatically a calibrated micro-Doppler representation. RF accuracy and macro F1 must never be presented as radar or combined-system results.

The [radar audit notes](radar-data-audit.md), [dataset manifest](../data/dataset-manifest.csv), and [audit results](../results/radar-audit-results.md) are the current radar evidence. Attribute Alexander Karlsson (KTH), DOI 10.5281/zenodo.5896641, CC BY 4.0, and disclose transformations. Check code and other dataset reuse permissions separately; the radar dataset license does not grant permission to redistribute predecessor code or model artifacts.

## New AAI-590 contributions and evidence to produce

| Contribution | Planned implementation | Completion evidence |
| --- | --- | --- |
| Radar classification | Approve label mapping and reflector treatment; select preprocessing; train a baseline and a neural network from scratch; split by measurement and investigate remaining session/target overlap | Versioned data/split manifests, class coverage, preprocessing fitted only on training data, reproducible runs, held-out macro F1/per-class recall and confusion matrices |
| Visual verification | Select licensed RGB data and evaluate an independent verifier; thermal imagery is optional | Separate visual dataset provenance, split policy, metrics, and documented missing/uncertain/conflicting outcomes |
| Coordination | Connect recorded radar observations to verification requests and results through a local replay workflow | Versioned event contract, event IDs, time/source provenance, timeouts, duplicate handling, and tests for matched, missing, late, and conflicting evidence |
| Operator review | Present model evidence, uncertainty, verification status, and an explicit human decision | Replay scenarios showing reviewable alerts, human disposition, and an audit trail; no autonomous physical response |
| Capstone monitoring and promotion | Apply the predecessor's monitoring/gating patterns to the new components with new baselines and validation-selected thresholds | Reports for each model and the coordinated workflow, rejected-candidate evidence, versioned approved artifacts, and preserved final test independence |

The radar modeling contributions and metrics are now recorded in [radar-model-results](radar-model-results.md). Visual verification, coordinated replay, and operator review remain separate capabilities with their own evidence requirements. Final acceptance criteria still require team agreement.

## Proposed coordination boundary

Use a local, recorded/simulated workflow first:

1. A radar observation produces a versioned classification result tied to its measurement/segment and model/preprocessing versions.
2. A coordinator assigns an event ID and requests visual verification using explicit association evidence.
3. The visual stage returns evidence references and its own model result, or an explicit unavailable/timeout outcome.
4. The coordinator retains both results and surfaces agreement, conflict, or insufficient evidence for operator review.
5. The operator records a disposition linked to the original event and evidence.

A proposed event record should carry an event ID, observation/source IDs, timestamps and their provenance, modality, model version, class scores, evidence references, verification status/reason, and human-review status. Final field names and state transitions belong to a later implementation phase. Scores are model outputs; they must not be described as calibrated probabilities without calibration evidence. Unknown or absent fields must remain explicit rather than fabricated.

Synchronized radar-camera data has not been secured. Separate datasets support separate model evaluations; any cross-modal pairing or coordination scenario must be labeled as simulated. Coordinates, velocity, shared timestamps, and camera pose require external measurements or an explicitly documented simulation. Classification labels do not produce measured locations or trajectories.

Anduril Lattice remains an optional, access-dependent extension. Local replay and operator review must remain demonstrable without it. Physical drone flight control and interception are outside scope. Target-centered samples cannot establish continuous detection performance or false alerts per operating hour.

## Implementation sequence and Phase 1 review

Phase 1 delivers this reference inventory and the [README continuity summary](../README.md#continuity-from-aai-540-to-aai-590). Review should confirm that inherited work, new work, completed evidence, and planned capabilities are distinguishable. The predecessor remains unchanged.

Subsequent work should first approve radar labels and leakage-aware splits, validate the audit environment, and establish radar baselines. Then evaluate visual verification independently, implement the event contract and local replay scenarios, and add operator review and monitoring. Cloud deployment and optional integrations follow only when justified by the working local demonstration.

For each adapted component, record the exact predecessor commit/path, permission or license, changes made, and new validation evidence. Track actual implementation ownership and contributions through issues and the [contribution log](contributions.csv). Follow the [AI-assistance disclosure guidance](ai-assistance.md) when adopting generated documentation or code. Do not duplicate predecessor results as new capstone contributions.
