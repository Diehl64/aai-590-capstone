# Data documentation

For new data sources or derivatives, update `dataset-manifest.csv` with provenance, permissions, checksums, split construction, transformations, and known relationships among samples. Do not add raw data, model binaries, credentials, or personal paths to Git.

## Thermal Dataset 2 EDA layout

| Local path | Contents | Git status |
| --- | --- | --- |
| `thermal-ir/raw/drone_detection_dataset2/Data/Video_IR/` | Source thermal videos and MATLAB ground-truth annotations | Ignored |
| `thermal-ir/manifests/dataset2_videos.csv` | Recording inventory, source classes, dimensions, frame counts, and annotation counts | Generated and ignored |
| `thermal-ir/manifests/annotation_issues.csv` | Audited source-data issues, including video/annotation length mismatches | Generated and ignored |
| `thermal-ir/interim/eda/dataset2_box_summary.csv` | Derived valid-box geometry summary created by the EDA notebook | Generated and ignored |

Run `notebooks/02_thermal_ir_pipeline.ipynb` through source-manifest validation, then run `notebooks/03_thermal_eda.ipynb`. Its Dataset 2 section analyzes class counts, recording duration, annotation geometry, target location, and temporal dependence. It reads raw data without modifying it and writes figures under `results/thermal-ir/eda/dataset2/`.

## Thermal Dataset 1 EDA layout

| Local path | Contents | Git status |
| --- | --- | --- |
| `thermal-ir/raw/anti_uav_dataset1/train/` | Source Dataset 1 train sequences and `IR_label.json` annotations | Ignored |
| `thermal-ir/manifests/dataset1_sequences.csv` | Sequence inventory, dimensions, annotation counts, and target-presence counts | Tracked |
| `thermal-ir/interim/eda/dataset1_box_summary.csv` | One row per valid drone box for descriptive geometry analysis | Generated and ignored |

Run `notebooks/03_thermal_eda.ipynb` after Dataset 1 source-manifest validation. Its Dataset 1 section reads raw annotations without modifying them and writes figures and an EDA summary under `results/thermal-ir/eda/dataset1/`.
