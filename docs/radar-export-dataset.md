# 77 GHz FMCW Radar Classification Dataset

This workspace contains an image dataset derived from the SAAB SIRS 1600 77 GHz FMCW radar measurements of drones, humans, and birds. The original source is retained locally as `data/raw/data_SAAB_SIRS_77GHz_FMCW.npy` and must not be modified.

## Radar export

The prepared three-class dataset is in `data/processed/radar`:

```text
data/processed/radar/
├── train/
│   ├── Bird/
│   ├── Drone/
│   └── Human/
├── val/
│   ├── Bird/
│   ├── Drone/
│   └── Human/
├── test/
│   ├── Bird/
│   ├── Drone/
│   └── Human/
├── metadata.csv
├── validation_report.json
├── export_config.json
└── contact_sheet.png
```

The export contains 72,588 PNGs. The 3,280 `CR` (corner-reflector) segments are excluded.

| Split | Drone | Human | Bird | Total |
|---|---:|---:|---:|---:|
| Train | 46,768 | 4,028 | 5,792 | 56,588 |
| Validation | 6,000 | 1,000 | 1,000 | 8,000 |
| Test | 6,000 | 1,000 | 1,000 | 8,000 |

Each PNG is a native-resolution 256 × 5 grayscale visualization of one radar segment: 256 consecutive FMCW/azimuth sweeps by five nearby range cells. Pixel values are signal magnitude in dB, mapped using one fixed global dB scale. The images are intended for classification, not object detection; this source does not provide bounding boxes.

## Labels

Detailed source labels are preserved in `metadata.csv` alongside the grouped label:

- `D1` through `D6` → `Drone`
- `human_walk`, `human_run` → `Human`
- Seagull, pigeon, raven, black-headed gull, mixed gull, and heron labels → `Bird`

This permits later training on drone subtypes without regenerating the source data.

## File names and traceability

Files use names such as `Drone_segment_000123.png`. The six-digit number is the segment's **global index in the original dataset's session order**, not its index within the Drone class or its split. It increments across all 75,868 original segments, including excluded corner-reflector samples, so numbering may contain gaps in the exported folders.

Use `metadata.csv` to trace every image to its `session_index`, `session_segment_index`, detailed `source_label`, grouped `class_label`, and supplied split assignment.

## Reproducing the export

Run the exporter from the workspace root:

```powershell
python .\src\radar\export_radar_images.py
```

The bundled desktop Python runtime may be needed if system Python is unavailable. The exporter refuses to modify the source `.npy` file, processes the embedded arrays in batches, validates every PNG, and resumes a partial export safely. It uses the original split assignments.

## Evaluation caveat

The source's train/validation/test assignments are preserved exactly. However, each parent measurement session contributes segments to multiple splits. Nearby segments from the same session can therefore be correlated across splits. For an independent generalization experiment, create a separate group/session-level split and report it alongside results using the provided split.
