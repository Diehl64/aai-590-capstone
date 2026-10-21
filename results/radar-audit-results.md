# Radar audit results — 2026-10-21

## Execution and provenance

The official 1,555,196,683-byte dataset was downloaded and matched publisher MD5 `01d66ba7b1ccc04477a9e69b2813f251`. The Zenodo API identifies CC BY 4.0; see `radar-source-metadata.json` for the source evidence. Attribution: Alexander Karlsson (KTH), Radar measurements on drones, birds and humans with a 77GHz FMCW sensor, version 2.0, https://doi.org/10.5281/zenodo.5896641. License: https://creativecommons.org/licenses/by/4.0/. Audit tables and plots are derived summaries; the source file was not modified.

The notebook's four Python cells ran sequentially in Python 3.12.14. A Python runner captured stdout, DataFrame displays, and the plot into the notebook. Native Jupyter kernel startup was blocked by this environment's socket restrictions; this is not a validated JupyterLab end-to-end run. See `radar-audit-environment.json` for versions. NumPy 2.3.5, pandas 2.2.3, and matplotlib 3.10.8 were used. These observations do not establish portability to other environments.

## Observations

- Array shape: 130 by 6, matching the expected schema.
- Total segments: 75,868, matching the publisher's count.
- Nonfinite signal, range, and time values: zero in the checks performed.
- Negative time steps within measurements: zero.
- Edge-marked segments: 67.
- All 130 measurements contain segments assigned to all three published splits.

| Proposed coarse class | Measurements | Segments |
| --- | ---: | ---: |
| Drone | 44 | 58,768 |
| Bird | 56 | 7,792 |
| Person | 11 | 6,028 |
| Reflector | 19 | 3,280 |

These are proposed groupings, not approved modeling labels. Excluding reflectors would leave 72,588 segments, approximately 81% drones. Pigeon and raven each occur in only one measurement (32 and 19 segments respectively), so a measurement-disjoint split cannot put those fine categories in every partition. A coarse bird class may be more feasible but still requires group-level analysis.

## Consequences for the capstone

The published segment-level partition does not hold out complete measurements. For an unseen-measurement evaluation, it could give optimistic results because related observations are shared across partitions. This finding is not proof that the original study's results are invalid; its evaluation question may differ.

Develop a measurement-group split and report per-class coverage before model selection. Investigate whether session, subject, or target identity overlaps remain across measurement IDs. Preserve an untouched final test set, fit preprocessing on training data, and compare against a baseline. Report macro F1 and per-class recall alongside accuracy because the coarse classes are imbalanced.

This audit does not prove independent sessions, remove duplicates, establish paired radar-camera data, derive geographic coordinates, or evaluate a classifier. Only one signal-magnitude example was plotted; more class/edge inspection is needed before preprocessing selection. No model-performance metrics have been generated.

## Files

- `radar-measurement-audit.csv`: one row per measurement.
- `radar-class-summary.csv`: fine-label counts.
- `radar-first-segment.png`: illustrative native signal magnitude, not a calibrated micro-Doppler spectrogram.
- `../notebooks/01_radar_data_audit.ipynb`: captured outputs from real-data Python execution.

ChatGPT prepared and executed this audit. Team review remains pending.
