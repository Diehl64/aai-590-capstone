# Thermal-IR Dataset Audit — Stage 1

**Audit date:** 2026-11-01  
**Scope:** Read-only inspection of the original local copies, followed by repository-staging setup. No model training, annotation conversion, or source-data modification was performed.

## Executive finding

The datasets can support a two-class thermal detector, but only after controlled conversion and sequence-aware splitting. The usable labelled material is:

- Dataset 1: **229,977** visible-drone frame annotations in its local `train` partition, subject to validation/exclusion of **121** non-positive-size boxes and **130** boxes extending past the frame boundary.
- Dataset 2: **47,622** drone and **21,967** bird visible-object frame annotations decoded from thermal-video MATLAB labels. Its decoder-reported boxes are geometrically valid.

The primary scientific risks are correlated video frames, source bias (all birds originate in Dataset 2), Dataset 1's incomplete/misaligned supplied test annotations, and Dataset 2 video/label frame-count mismatches. Dataset 1 test folders must **not** automatically be used for YOLO test metrics.

## Repository-local layout

| Dataset | Repository-local root | Relevant structure |
|---|---|---|
| 1 — Official 4th Anti-UAV Challenge | `data/thermal-ir/raw/anti_uav_dataset1/` | `train`, `track1_test`, `track2_test`; frame-extracted JPEG/PNG sequences; `IR_label.json` per labelled sequence |
| 2 — Drone Detection Dataset | `data/thermal-ir/raw/drone_detection_dataset2/Data/Video_IR/` | 365 IR `.mp4` files with paired `*_LABELS.mat` MATLAB Computer Vision Toolbox `groundTruth` files |

Dataset 1 has 763,270 image files across 655 sequence directories: 247,579 in `train` (223 sequences), 232,742 in `track1_test` (216 sequences), and 282,949 in `track2_test` (216 sequences). Dataset 2 has 365 matched IR video/label pairs; no pair is missing its counterpart.

### Repository-local staging layout

Thermal source data are being staged beneath the repository rather than accessed through processing code at the original external locations. The sources remain immutable; the repository copies are local working copies and are ignored by Git.

```text
data/thermal-ir/
  raw/
    anti_uav_dataset1/           # immutable working copy of Dataset 1
    drone_detection_dataset2/    # immutable working copy of Dataset 2
  manifests/                     # tracked/derived inventory and issue tables
  interim/qa_overlays/           # ignored visual-validation artifacts
  processed/yolo_v1/             # ignored exported YOLO dataset
results/thermal-ir/
  figures/
  metrics/
  test_predictions.csv
```

**Staging status at 2026-11-01:** Dataset 2 was copied completely (736/736 files). The Dataset 1 copy was intentionally halted for manual completion after 749,756/763,717 files were copied; its labelled `train` partition was 239,187/247,803 files, including 209/223 `IR_label.json` files. The notebook's raw-data completeness gate will block processing until both copies match their audited file counts.

The reproducible entry point is [`notebooks/02_thermal_ir_pipeline.ipynb`](../notebooks/02_thermal_ir_pipeline.ipynb). It includes the dedicated environment setup, dependency check, raw-copy gate, source documentation, and the subsequent processing/evaluation contract.

## Compatibility summary

| Property | Dataset 1 | Dataset 2 |
|---|---|---|
| Source | Zenodo 15103888 / Anti-UAV (provided by project brief) | DroneDetectionThesis/Drone-detection-dataset (provided by project brief) |
| Eligible classes | Drone only | Drone and Bird; airplane/helicopter are present but excluded from initial two-class data |
| Usable labelled sequences | 223 local `train` sequences | 157 drone videos; 79 bird videos |
| Total usable labelled frames | 247,579 frame/annotation positions | 73,731 visible frames: 47,622 drone + 21,967 bird |
| Visible target annotations | 229,977 drones | 47,622 drones; 21,967 birds |
| Absent target positions | 17,602 | 1,565 drone + 2,577 bird |
| Image/video resolution | 200 sequences at 640×512; 23 at 512×512 | All 365 videos at 320×256, 30 fps |
| Annotation format | JSON arrays: `exist`, `gt_rect`; some train files add challenge attributes | MATLAB MCOS `groundTruth`; decoded with `mcos_decoder.load_groundtruth()` |
| Box convention | Verified/project rendering code interprets `gt_rect` as pixel `x, y, width, height`, top-left origin | Repository decoder returns pixel `(x, y, width, height)` or `None` when absent |
| Existing usable split | `train` only | No published train/validation/test split identified locally |

## Dataset 1 details

### Training partition

Each of the 223 `train` sequences has an `IR_label.json`. The 247,579 images are exactly aligned with the `exist` and `gt_rect` arrays: both arrays total 247,579 positions. The JSON schema is not completely uniform:

- 143 sequences: `exist`, `gt_rect`
- 30 sequences: `exist`, `gt_rect`, `LR`, `VE`, `OC`, `FM`, `SV`, `IC`, `DBC`, `TS`
- 50 sequences: `exist`, `gt_rect`, `OC`, `FM`, `TC`, `SV`, `DBC`

For initial YOLO conversion, use only `exist[i] == 1` and `gt_rect[i]`; retain the extra per-frame attributes in provenance metadata for later quality analysis. Dataset-supplied `labeled-gif.py` confirms the intended top-left `xywh` interpretation and that `exist` takes precedence over stale boxes.

Validation found no missing arrays or frame/annotation length mismatches. Among visible target entries, 121 boxes have non-positive width or height, and 130 extend beyond their native image boundary. These are data-quality events, not normal negative frames. The converter must log each event and apply an explicit policy (normally exclude the affected frame unless a reviewed, documented clipping policy is adopted).

### Supplied test folders

`track1_test` has 216 sequence folders and 232,742 images, each with an `IR_label.json` containing only one `gt_rect` (216 boxes total). It lacks per-frame `exist` and frame-aligned box arrays. `track2_test` has 216 sequence folders and 282,949 images, with no JSON files. These layouts are incompatible with frame-level YOLO training or direct detection evaluation as currently supplied. Preserve them untouched; request official test labels/evaluation instructions before using them.

## Dataset 2 details

The README documents that the MATLAB `groundTruth` MCOS objects are not reliably decoded by conventional SciPy loaders. The audit used the repository-recommended `mcos-decoder` Python package, whose `load_groundtruth()` returns one `xywh` box or `None` per label index.

| Original target label | Videos | Label entries | Visible boxes | Absent entries | Invalid decoded boxes |
|---|---:|---:|---:|---:|---:|
| AIRPLANE | 74 | 23,243 | 23,243 | 0 | 0 |
| BIRD | 79 | 24,544 | 21,967 | 2,577 | 0 |
| DRONE | 157 | 49,187 | 47,622 | 1,565 | 0 |
| HELICOPTER | 55 | 16,953 | 16,953 | 0 | 0 |

No decoded box has a negative origin, non-positive dimensions, or extends past its 320×256 video frame. However, 85 files have video-frame-count versus label-length discrepancies: all 79 bird videos, four drone videos, and two helicopter videos. The discrepancy magnitude is usually one frame (77 files), but several are substantially different. The conversion must iterate only over the validated overlap `min(video_frame_count, label_length)`, retain both counts in metadata, and flag the extra/missing tail frames. For the drone/bird pipeline this affects all bird videos and four drone videos.

## Correct conversion and integration plan

1. Create immutable manifests for each original sequence/video before extracting or copying frames.
2. Convert eligible visible annotations only from native top-left pixel `xywh` to YOLO `class x_center y_center width height`, with native width/height from each image/video. Map Dataset 1 Drone to class `0`; Dataset 2 DRONE to `0` and BIRD to `1`.
3. Do not label `exist == 0` or `None` frames as object-positive examples. Retain a decision in metadata on whether validated target-absent frames will become negative images.
4. Exclude Dataset 2 airplane/helicopter recordings wholesale for the initial two-class implementation. They must not become unlabeled background because that would penalize correct detections of excluded aircraft.
5. Produce structured issue logs for Dataset 1 invalid/out-of-bounds boxes and Dataset 2 frame-count mismatches. Never silently clamp, drop, or fabricate labels.
6. Store a combined metadata row for every exported image containing `image_id`, `source_dataset`, `source_sequence`, `original_frame`, `class_id`, original `bbox`, conversion status, and eventual `split`.
7. Hash exported source frames for exact duplicates and use perceptual hashes within and across sequences. Preserve original recording IDs for grouping.

## Recommended two-class YOLO structure

```text
data/thermal-ir/processed/yolo_v1/
  images/{train,val,test}/
  labels/{train,val,test}/
  metadata/frames.csv
  metadata/issues.csv
  metadata/duplicate_groups.csv
  data.yaml                 # names: [Drone, Bird]
```

All frames from an original Dataset 1 sequence or Dataset 2 video must remain in one partition. Parent-session relationships encoded in names (for example Dataset 1 split recordings) should be grouped further if validated as related. For the controlled comparison, reserve a fixed Dataset 2-only test set first; Experiment A trains on Dataset 2 training sequences, and Experiment B adds only Dataset 1 training sequences. Dataset 1 must not supply bird examples, so source-specific and source-bias evaluations are required.

## Obstacles and decisions needed before processing

1. **Dataset 1 test use — resolved:** `track1_test` and `track2_test` remain inference-only. They are excluded from training, validation, test metrics, and model selection unless usable official frame-level labels become available.
2. **Dataset 2 mismatched tails:** Default recommendation is overlap-only conversion with the excluded tail recorded. Approve this policy before extraction.
3. **Dataset 1 invalid boxes:** Default recommendation is exclude affected positive frames (not clamp) until reviewed visual samples support a correction rule.
4. **Scale and correlation:** Exporting every visible frame would create roughly 303,566 positive frames before duplicate filtering, heavily dominated by correlated video frames. A deterministic temporal-subsampling policy should be chosen and reported before the build.

## Next implementation sequence

1. Complete the manual Dataset 1 raw-data copy, then run the notebook's raw-copy gate.
2. Implement read-only manifest and validation modules with unit tests for `xywh` → YOLO conversion.
3. Render reviewed drone and bird overlay samples, including all issue categories.
4. Implement Dataset 2 video extraction/decoder alignment and Dataset 1 conversion with issue logs.
5. Hash and deduplicate; calculate source, target-size, resolution, and thermal-intensity distributions.
6. Build recording-disjoint splits and a split-integrity report. Request approval of this prepared dataset and training configuration before any model training.

No detection metrics or model results exist at this stage.
