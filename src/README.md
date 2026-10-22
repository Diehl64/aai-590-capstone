# Reusable Python source

## Radar image exporter

`radar/export_radar_images.py` converts the official SAAB/SIRS 77 GHz FMCW NumPy source into the three-class image-classification layout used by this project.

Run it from the repository root:

```powershell
python .\src\radar\export_radar_images.py
```

Its default input is `data/raw/data_SAAB_SIRS_77GHz_FMCW.npy`; its default output is `data/processed/radar/`. Both paths can be overridden with `--source` and `--output`.

The exporter requires NumPy and Pillow. It reads the trusted official pickled NumPy object array, leaves that source file unchanged, applies a seeded global dB calibration, preserves the source split assignments, writes 256 × 5 grayscale PNGs, and verifies every generated or reused image. It also writes `metadata.csv`, `validation_report.json`, and `export_config.json` beside the export.

Do not use the supplied split as evidence of session-independent generalization: its parent measurements contribute samples to multiple splits. Any group/session-level split must be a separate, documented dataset version.

Future reusable preprocessing, training, evaluation, and integration modules belong under `src/` in focused subdirectories. Keep notebooks for exploration and use `src/` for code that must be rerun or tested.
