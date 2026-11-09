# Thermal-IR Drone Detection Pipeline

**Last updated:** 2026-11-02  
**Scope:** Source-data validation, one-class YOLO export, training, and evaluation for the question: **Is there a drone in this image?**

## 1. Objective and model contract

The deployed model is a one-class object detector with `0: drone` as its only YOLO class. An image is reported as **drone present** when at least one predicted drone box meets a threshold selected on validation data; otherwise it is reported as **no drone present**.

Birds are not a second model class. Dataset 2 bird frames are retained as hard-negative no-drone examples with empty YOLO label files. Their source boxes remain available for provenance and QA only. This design directly measures the important operational failure: falsely identifying a bird as a drone.

## 2. Source datasets and roles

| Dataset | Local source | Pipeline role |
|---|---|---|
| Official Anti-UAV Challenge (Dataset 1) | `data/thermal-ir/raw/anti_uav_dataset1/` | Additional drone-positive material for the later combined experiment |
| Drone Detection Dataset (Dataset 2) | `data/thermal-ir/raw/drone_detection_dataset2/Data/Video_IR/` | Initial drone-positive and bird hard-negative baseline |

Dataset 1 is the [Official Dataset Release for the 4th Anti-UAV Challenge](https://doi.org/10.5281/zenodo.15103888), version 1.0.0, published by China Telecom. The Zenodo record is public but its files are restricted, and it does not state a license. Access must therefore be requested through the official release links, and reuse or redistribution permission must be confirmed before sharing derived data. Dataset 1 is documented for the later combined experiment but is not used in the Dataset 2-only baseline reported here.

Dataset 2 is the [DroneDetectionThesis/Drone-detection-dataset](https://github.com/DroneDetectionThesis/Drone-detection-dataset) repository, recorded here at commit `442d0c6750708cc221636f7a1fd31cbd8cb0aeb8`. Its bundled `LICENSE` is **CC0 1.0 Universal** (verified 2026-11-08). The source asks users to cite Svanstrom et al. (2021), *A Dataset for Multi-Sensor Drone Detection*; its linked Zenodo DOI is [10.5281/zenodo.5500576](https://doi.org/10.5281/zenodo.5500576). The raw videos and MATLAB annotations are accessed by cloning the source repository (or obtaining its Zenodo release) and remain outside Git. The corresponding provenance/access/license record is in [`data/dataset-manifest.csv`](../data/dataset-manifest.csv).

Dataset 1 provides 223 labelled `train` sequences. Its supplied `track1_test` and `track2_test` folders are inference-only: they do not have compatible frame-level annotations and are excluded from training, validation, model selection, and reported test metrics.

Dataset 2 provides 365 paired thermal videos and MATLAB `groundTruth` label files. The initial pipeline uses its 157 drone videos and 79 bird videos. Airplane and helicopter recordings are excluded rather than being silently treated as background.

## 3. Data validation and cleaning policy

Raw files are never changed. The pipeline records issues in manifests and applies the policy only while creating a derived YOLO dataset.

| Issue | Count | Export policy |
|---|---:|---|
| Dataset 1 box exceeds image boundary | 130 | Exclude the affected positive frame; do not automatically clip the box. |
| Dataset 1 non-positive box dimensions | 121 | Exclude the affected positive frame; do not relabel it as no-drone. |
| Dataset 1 zero-byte source image | 117 | Log as `unreadable_source_frame` and skip if eligible for export. |
| Dataset 2 video/annotation length mismatch | 85 videos | Process only `min(video_frame_count, annotation_entries)`; do not pad or invent tail labels. |

This distinction matters: a malformed Dataset 1 box occurs in a frame where a target was marked present. Converting it to an empty label would incorrectly train the detector that the frame contains no drone.

## 4. Dataset 1 exploratory analysis

Dataset 1 EDA covers its 223 labelled `train` sequences only; its restricted supplied test folders remain inference-only and are not treated as evaluated data. The source contains 247,579 frame/annotation entries: 229,977 target-present entries and 17,602 target-absent entries. Two frame resolutions occur: 200 sequences at 640x512 and 23 at 512x512. Sequence length ranges from 28 to 1,630 frames (median 1,000; mean 1,110).

After excluding invalid boxes, 229,726 valid drone boxes remain for descriptive geometry analysis. Their median area is 0.132% of the image, their median width-to-height ratio is 1.36, and their median normalized center is (0.496, 0.529). The audit findings remain 130 boxes extending beyond image boundaries, 121 non-positive-size boxes, and 117 zero-byte source frames. These values describe source properties and potential collection-specific shortcuts; they do not establish general detection performance.

Reproduce the analysis by running [`notebooks/03_thermal_eda.ipynb`](../notebooks/03_thermal_eda.ipynb) in order. It writes [`sequence_inventory_and_quality.png`](../results/thermal-ir/eda/dataset1/sequence_inventory_and_quality.png), [`box_geometry_and_target_location.png`](../results/thermal-ir/eda/dataset1/box_geometry_and_target_location.png), and [`eda_summary.json`](../results/thermal-ir/eda/dataset1/eda_summary.json). Dataset 1 contributes drone positives only, so it cannot by itself evaluate drone-versus-bird rejection and is kept separate from the Dataset 2-only baseline.

## 5. Combined-source descriptive EDA

The combined-source section of [`notebooks/03_thermal_eda.ipynb`](../notebooks/03_thermal_eda.ipynb) compares normalized box area, aspect ratio, and target-center location across Dataset 1 drones, Dataset 2 drones, and Dataset 2 birds. It preserves source identity and uses equal-size samples for the target-location scatterplot so Dataset 1's larger annotation count does not visually dominate. This is a descriptive source-comparison artifact only: it does not merge training data, change split assignments, or alter the Dataset 2-only baseline metrics.

## 6. Derived YOLO dataset

The derived export lives at `data/thermal-ir/processed/yolo_v1/`. It contains separate images and labels, source-frame metadata, an issue log, and a split-integrity report.

```text
data/thermal-ir/processed/yolo_v1/
  images/{train,val,test}/
  labels/{train,val,test}/
  metadata/frames.csv
  metadata/split_integrity_report.json
  metadata/skipped_unreadable_source_frames.csv
  experiment_a_dataset2_only.yaml
  experiment_b_combined.yaml
```

Each source sequence or video is assigned to exactly one partition. This recording-disjoint rule prevents adjacent, visually similar video frames from leaking into validation or test data. The initial export uses every fifth eligible frame to reduce temporal redundancy.

## 7. Experiment A: Dataset 2-only baseline

Experiment A establishes the initial drone-versus-bird-negative baseline before Dataset 1 material is introduced.

| Split | Drone-positive frames | Bird hard-negative frames | Total |
|---|---:|---:|---:|
| Train | 6,138 | 3,369 | 9,507 |
| Validation | 1,430 | 741 | 2,171 |
| Held-out test | 1,878 | 753 | 2,631 |

All 14,309 Dataset 2-only image paths were validated, and no recording crosses the train, validation, or test boundary.

## 8. Mosaic augmentation

During training, YOLO may combine four different source images into one composite training image. This is called **mosaic augmentation**. It is applied only while training; original files and normal inference images are not changed.

```text
+----------------+----------------+
| source image A | source image B |
+----------------+----------------+
| source image C | source image D |
+----------------+----------------+
```

Every original drone box is resized and moved with its source image. If two of the four images contain drones, the composite correctly contains two class-0 drone boxes. The seams, gray padding, and multiple scenes visible in Ultralytics `train_batch#.jpg` previews are expected consequences of this augmentation—not duplicated labels or corrupted data.

The baseline uses `mosaic: 0.5`, so about half of training samples are mosaics. `close_mosaic: 10` disables mosaic for the final ten epochs, allowing the model to finish on normal unmosaicked images. The default preview mosaics have long filename captions and are not used as report-quality QA artifacts.

## 9. Training configuration and completed baseline

The Batch-32 baseline uses pretrained `yolo26n.pt`, 640-pixel input images, AdamW optimization, a fixed seed, deterministic mode, and one output class. The run early-stopped after 23 epochs. Its best checkpoint is:

`results/thermal-ir/runs/experiment_a_dataset2_only_batch32/weights/best.pt`

The held-out test evaluation used a decision threshold of `0.25`, chosen on validation data to minimize bird false positives while retaining at least 90% validation recall.

| Held-out measure | Result |
|---|---:|
| Image-level precision | 99.73% |
| Drone-present recall | 97.44% |
| Image-level F1 | 98.57% |
| Bird false-positive rate | 0.66% (5 of 753 bird frames) |
| Drone false-negative rate | 2.56% (48 of 1,878 drone frames) |
| Detection mAP@0.5 | 87.95% |
| Detection mAP@0.5:0.95 | 39.55% |

`mAP@0.5` measures detection quality when a prediction overlaps a true drone box by at least 50%. `mAP@0.5:0.95` averages performance over increasingly strict overlap requirements and is therefore lower when boxes are not consistently tight.

## 10. Reproducible environment

The saved Batch-32 baseline was run on Windows 11 using an NVIDIA GeForce RTX 5080 (`CUDA:0`, CUDA runtime 13.0), Python 3.11.7, PyTorch 2.14.1+cu130, torchvision 0.29.1+cu130, and Ultralytics 8.4.198. The full direct-package record and the training settings are versioned in [`results/thermal-ir/environment.json`](../results/thermal-ir/environment.json); [`thermal-training-requirements.txt`](../thermal-training-requirements.txt) provides the corresponding install specification. Install it with the CUDA 13.0 PyTorch wheels available:

```powershell
python -m pip install -r thermal-training-requirements.txt --extra-index-url https://download.pytorch.org/whl/cu130
```

Run [`notebooks/02_thermal_ir_pipeline.ipynb`](../notebooks/02_thermal_ir_pipeline.ipynb) in order after placing the raw Dataset 2 checkout at the documented ignored local path. It records the validated manifests, recording-disjoint split, model arguments, selected validation threshold, and final held-out evaluation. Reproduction on different drivers, GPUs, or operating systems can cause small numerical differences.

## 11. Evaluation artifacts and error-analysis panels

The Batch-32 evaluation artifacts are stored in:

`results/thermal-ir/evaluation/experiment_a_dataset2_only_batch32/`

They include detection metrics, validation-threshold results, per-image drone/no-drone decisions, and row-level prediction outcomes.

The curated panels in `results/thermal-ir/evaluation/experiment_a_dataset2_only_batch32/error_analysis/` show true-positive drones, missed drones, correct bird rejections, and bird false positives. They are generated by [`src/generate_thermal_error_panels.py`](../src/generate_thermal_error_panels.py) from `test_image_decisions.csv` and `test_predictions.csv`, using the selected `0.25` operating threshold. Green boxes are ground truth; red boxes are retained predictions. `selection_manifest.csv` records every displayed source recording and frame. The selection prefers distinct source recordings and ranks candidates by maximum confidence, so the panels are traceable examples rather than a replacement for the full held-out metrics.

The reproducible implementation is [`notebooks/02_thermal_ir_pipeline.ipynb`](../notebooks/02_thermal_ir_pipeline.ipynb).
