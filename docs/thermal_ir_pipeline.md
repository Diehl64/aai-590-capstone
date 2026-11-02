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

## 4. Derived YOLO dataset

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

## 5. Experiment A: Dataset 2-only baseline

Experiment A establishes the initial drone-versus-bird-negative baseline before Dataset 1 material is introduced.

| Split | Drone-positive frames | Bird hard-negative frames | Total |
|---|---:|---:|---:|
| Train | 6,138 | 3,369 | 9,507 |
| Validation | 1,430 | 741 | 2,171 |
| Held-out test | 1,878 | 753 | 2,631 |

All 14,309 Dataset 2-only image paths were validated, and no recording crosses the train, validation, or test boundary.

## 6. Mosaic augmentation

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

## 7. Training configuration and completed baseline

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

## 8. Evaluation artifacts and next work

The Batch-32 evaluation artifacts are stored in:

`results/thermal-ir/evaluation/experiment_a_dataset2_only_batch32/`

They include detection metrics, validation-threshold results, per-image drone/no-drone decisions, and row-level prediction outcomes.

The next visualization change is to replace default Ultralytics `train_batch#` and `val_batch#` mosaics with curated panels showing true-positive drones, missed drones, correctly rejected bird frames, and bird false positives. Those panels must filter predictions using the selected operating threshold, rather than the low inference floor used to retain candidates for metric calculation.

The reproducible implementation is [`notebooks/02_thermal_ir_pipeline.ipynb`](../notebooks/02_thermal_ir_pipeline.ipynb).
