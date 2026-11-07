# Data documentation

The repository documents the radar and thermal datasets but does not version their raw or generated data. Both are ignored by Git; download the official sources before running the relevant notebook.

## Radar dataset layout

| Local path | Contents | Git status |
| --- | --- | --- |
| `data/raw/data_SAAB_SIRS_77GHz_FMCW.npy` | Official 77 GHz FMCW source array | Ignored |
| `data/processed/radar/` | Generated train/validation/test PNGs, metadata, and validation report | Ignored |
| `dataset-manifest.csv` | Dataset provenance, access, and checksum reference | Tracked |

Download the source from the record listed in `dataset-manifest.csv`, verify its MD5 checksum, and keep the file unmodified. The expected publisher checksum is `01d66ba7b1ccc04477a9e69b2813f251`.

Generate or validate the image export from the repository root:

```powershell
python .\src\radar\export_radar_images.py
```

The exporter preserves the supplied per-segment split codes, excludes `CR` corner-reflector samples, and writes `metadata.csv` as the mapping from each output PNG to its original segment. Its 72,588 expected images use the original source's segment-level splits; they are not measurement/session-disjoint. See [the radar export documentation](../docs/radar-export-dataset.md) and [the audit notes](../docs/radar-data-audit.md) before training a model.

For new data sources or derivatives, update `dataset-manifest.csv` with provenance, permissions, checksums, split construction, transformations, and known relationships among samples. Do not add raw data, model binaries, credentials, or personal paths to Git.

## Thermal Dataset 2 EDA layout

| Local path | Contents | Git status |
| --- | --- | --- |
| `thermal-ir/raw/drone_detection_dataset2/Data/Video_IR/` | Source thermal videos and MATLAB ground-truth annotations | Ignored |
| `thermal-ir/manifests/dataset2_videos.csv` | Recording inventory, source classes, dimensions, frame counts, and annotation counts | Generated and ignored |
| `thermal-ir/manifests/annotation_issues.csv` | Audited source-data issues, including video/annotation length mismatches | Generated and ignored |
| `thermal-ir/interim/eda/dataset2_box_summary.csv` | Derived valid-box geometry summary created by the EDA notebook | Generated and ignored |

Run `notebooks/02_thermal_ir_pipeline.ipynb` through source-manifest validation, then run `notebooks/03_thermal_dataset2_eda.ipynb`. The EDA notebook analyzes class counts, recording duration, annotation geometry, target location, and temporal dependence. It reads raw data without modifying it and writes figures under `results/thermal-ir/eda/dataset2/`.
