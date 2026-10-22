# Radar methodology and results draft

## Data and task

The study uses the checksum-verified version 2.0 KTH 77 GHz FMCW radar dataset (130 measurements and 75,868 segments; CC BY 4.0). The proposed coarse mapping assigns D1–D6 to `drone`, bird labels to `bird`, and human_run/human_walk to `human`. The 19 corner-reflector measurements are retained for accounting and excluded from the three-class task. The raw 1.6 GB object-array file is not committed.

## Leakage-aware evaluation

Complete measurement IDs, rather than individual segments, define the split. Seed 590 assigns 50,491 segments to train, 11,047 to validation, and 11,050 to test. Preprocessing statistics are fitted on training segments only. The published split field is not used because every measurement spans multiple published splits. Session, subject, and target independence across measurement IDs is not established by the source metadata and remains a limitation.

## Models

The baseline uses five magnitude statistics per segment and nearest class centroids fitted on training measurements. The CNN is trained from scratch on normalized magnitude reshaped to five range cells by 256 azimuth samples. Its checkpoint is selected by validation macro F1. The recorded CNN run used PyTorch 2.11.0+cu128 on an NVIDIA RTX 5080.

## Results

| Model | Test accuracy | Test macro F1 |
| --- | ---: | ---: |
| Nearest centroid | 0.5807 | 0.4882 |
| RadarCNN, epoch 7 | **0.9439** | **0.8910** |

The CNN test confusion matrix, in class order drone/bird/human, is `[[8556, 173, 153], [98, 1075, 3], [193, 0, 799]]`. Per-class precision/recall/F1 are: drone 0.9671/0.9633/0.9652; bird 0.8614/0.9141/0.8870; human 0.8366/0.8054/0.8207.

## Interpretation and limitations

The CNN substantially outperforms this simple baseline on the held-out measurement groups. This is evidence for the selected representation and model on this dataset and split. It is not evidence of continuous perimeter detection, false alerts per operating hour, calibrated probabilities, geographic tracking, unseen-session generalization, or field deployment readiness. The replay/operator-review scenarios are simulated and must be reported separately from these measured classifier results. RGB/thermal verification and Lattice integration were not evaluated.

## Reproducibility checklist

- Record the dataset MD5, source DOI/license, repository commit, split seed, model seed, hardware, PyTorch/CUDA versions, and output JSON.
- Preserve the untouched test partition and do not tune thresholds against it.
- Review class mapping and reflector treatment with the team.
- Add figures for class counts, split coverage, both confusion matrices, and replay state transitions.
