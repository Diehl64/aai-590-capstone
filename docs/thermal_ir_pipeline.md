# Thermal-IR Pipeline and Evaluation Record

This is the authoritative record for the thermal-IR data workflow, experiments, held-out evaluations, and evidence boundaries. It supersedes the former standalone baseline-evidence note.

## Scope and decision rule

The system answers one question for each image: **is a drone present?** It is a one-class YOLO detector (`0: drone`), not a drone-versus-bird classifier. A drone is reported when at least one predicted box meets the operating threshold selected before held-out testing.

Dataset 2 bird frames are intentionally exported as empty-label no-drone hard negatives. Their source bird boxes are retained only for audit and visual QA. Dataset 1 target-absent frames are background negatives, not birds; Dataset 1 results therefore cannot support bird-rejection claims.

Raw source files are immutable. Each source recording or sequence belongs to exactly one train, validation, or test partition.

## Data provenance and license status

| Source | Use in this work | Access and license record |
| --- | --- | --- |
| Dataset 1 — [Official Dataset Release for the 4th Anti-UAV Challenge](https://doi.org/10.5281/zenodo.15103888), version 1.0.0 | Drone-positive source for Dataset 1-only, transfer, and balanced-joint experiments | The Zenodo record is public but its files are restricted. Its Rights → License field was blank when checked on 2026-11-15. Do not redistribute source frames or derived image data; confirm access, reuse, and redistribution terms with the rights holder before publication beyond internal course review. |
| Dataset 2 — [Drone Detection Dataset](https://github.com/DroneDetectionThesis/Drone-detection-dataset) | Drone positives and bird hard negatives | The repository's [LICENSE](https://github.com/DroneDetectionThesis/Drone-detection-dataset/blob/master/LICENSE) is CC0 1.0 Universal. The repository requests citation of Svanström et al. (2021), *A Dataset for Multi-Sensor Drone Detection*. |

The detailed source record is maintained in [`data/dataset-manifest.csv`](../data/dataset-manifest.csv). Neither source is synchronized with the radar, RF, or acoustic datasets, so thermal outputs are used with other modalities only in explicitly simulated replay scenarios.

## Notebook timeline

| Order | Notebook | Purpose |
| ---: | --- | --- |
| 02 | [`02_thermal_data_preparation_and_baseline.ipynb`](../notebooks/02_thermal_data_preparation_and_baseline.ipynb) | Validate sources, create manifests and recording-disjoint exports, and reproduce the Dataset 2-only baseline. |
| 03 | [`03_thermal_dataset_exploration.ipynb`](../notebooks/03_thermal_dataset_exploration.ipynb) | Read-only inventory, annotation-quality, geometry, and cross-source analysis. |
| 04 | [`04_thermal_dataset1_training_and_evaluation.ipynb`](../notebooks/04_thermal_dataset1_training_and_evaluation.ipynb) | Dataset 1-only internal-generalization experiment. |
| 05 | [`05_thermal_transfer_learning.ipynb`](../notebooks/05_thermal_transfer_learning.ipynb) | Fine-tune the Dataset 2 baseline on Dataset 1 and test each source separately. |
| 06 | [`06_thermal_balanced_joint_training.ipynb`](../notebooks/06_thermal_balanced_joint_training.ipynb) | Train the source-balanced joint model and test each source separately. |
| 07 | [`07_thermal_model_comparison.ipynb`](../notebooks/07_thermal_model_comparison.ipynb) | Read-only comparison of the Dataset 2 baseline and balanced-joint model. |

Notebooks 04–06 are distinct experiments, not one sequential training chain. Notebook 07 compares the Dataset 2 baseline and balanced-joint model on the shared Dataset 2 held-out test set.

## Source validation and dataset controls

Dataset 1 supplies 223 labelled `train` sequences. Its provided `track1_test` and `track2_test` folders are inference-only because compatible frame labels are unavailable; they are excluded from training, model selection, and reported metrics. Dataset 2 has 365 paired thermal videos and MATLAB `groundTruth` files; the current workflow uses 157 drone and 79 bird videos, excluding airplane and helicopter recordings rather than silently treating them as background.

The derived export applies these policies:

- exclude unreadable or zero-byte source images;
- exclude Dataset 1 positive frames with invalid or out-of-bounds boxes rather than relabeling them as no-drone;
- use only the validated overlap when a Dataset 2 video and annotation file differ in length; and
- sample every fifth eligible frame to reduce temporal redundancy.

The source inventories, issue logs, annotation geometry, and descriptive cross-source comparison are produced by notebook 03. Dataset 1 contributes drone positives only and cannot by itself measure drone-versus-bird discrimination.

## Evaluated experiments

All metrics below are held-out results from the saved evaluation artifacts. The Dataset 2-only baseline is the reviewed handoff used by the simulated replay. The Dataset 1-only, transfer, and balanced-joint results are repository artifacts awaiting final team review and should not be described as final report claims until that review is complete.

| Experiment | Held-out source | Threshold origin | Image-level result | Detection mAP@0.5 / mAP@0.5:0.95 |
| --- | --- | --- | --- | --- |
| Dataset 2-only baseline | Dataset 2 | 0.25, selected on Dataset 2 validation | 97.44% drone recall; 0.66% bird false-positive rate (5/753) | 87.95% / 39.55% |
| Dataset 1-only | Dataset 1 | 0.75, selected on validation | 35.43% recall; 0.00% target-absent false-positive rate | 77.27% / 40.18% |
| Dataset 2 → Dataset 1 transfer | Dataset 1 | 0.25 fixed from the Dataset 2 baseline | 80.40% recall; 5.90% target-absent false-positive rate | 75.22% / 38.95% |
| Dataset 2 → Dataset 1 transfer | Dataset 2 | 0.25 fixed from the Dataset 2 baseline | 96.81% recall; 54.32% bird false-positive rate | 9.60% / 1.89% |
| Balanced joint training | Dataset 1 | 0.50, selected on Dataset 2 validation | 66.07% recall; 0.98% target-absent false-positive rate | 74.62% / 38.09% |
| Balanced joint training | Dataset 2 | 0.50, selected on Dataset 2 validation | 93.98% recall; 0.00% bird false-positive rate | 87.83% / 40.12% |

The transfer experiment demonstrates a material Dataset 2 bird-rejection degradation at its fixed baseline threshold. The balanced-joint experiment preserved Dataset 2 localization closely relative to the baseline while selecting a stricter operating threshold. These are experiment-specific findings, not evidence of deployment readiness or cross-dataset generalization beyond the evaluated sources.

## Evaluation artifacts and error analysis

Each evaluation directory contains saved decision metrics, image decisions, and a `selection_manifest.csv` for its panels. The baseline also retains its original per-box prediction table.

| Experiment/test source | Error-analysis directory |
| --- | --- |
| Dataset 2-only baseline | `results/thermal-ir/evaluation/experiment_a_dataset2_only_batch32/error_analysis/` |
| Dataset 1-only | `results/thermal-ir/evaluation/experiment_c_dataset1_only_batch32/error_analysis/` |
| Transfer: Dataset 1 / Dataset 2 | `results/thermal-ir/evaluation/experiment_d_dataset2_to_dataset1_transfer_v2_batch32/dataset1_test/error_analysis/` and `dataset2_test/error_analysis/` |
| Balanced joint: Dataset 1 / Dataset 2 | `results/thermal-ir/evaluation/experiment_e_combined_balanced_yolo26n_batch32/dataset1_test/error_analysis/` and `dataset2_test/error_analysis/` |

[`src/generate_thermal_error_panels.py`](../src/generate_thermal_error_panels.py) selects examples using each evaluation's saved `test_image_decisions.csv` and recorded threshold. Green boxes are ground truth and red boxes are predictions. Where a run did not persist per-box predictions, the script replays inference only for the selected visual examples; that replay does not change saved metrics, thresholds, or decision categories. A panel stating that no examples occurred is a valid result at the recorded threshold.

## Reproducibility and reporting limits

The Dataset 2 baseline ran with pretrained `yolo26n.pt`, 640-pixel inputs, AdamW, a fixed seed, deterministic mode, and one output class. Its environment is recorded in [`results/thermal-ir/environment.json`](../results/thermal-ir/environment.json), with dependencies in [`thermal-training-requirements.txt`](../thermal-training-requirements.txt).

Do not combine thermal results with radar, RF, or acoustic metrics. The source datasets are not synchronized, and simulated replay does not establish sensor fusion, continuous monitoring performance, calibrated probabilities, or operational readiness.
