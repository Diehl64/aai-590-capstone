# Notebook plan

The following thermal notebooks are implemented. Run the source-manifest validation stage in the pipeline notebook before running the Dataset 2 EDA notebook.

| Suggested name | Purpose |
| --- | --- |
| `02_thermal_ir_pipeline.ipynb` | Thermal dataset provenance, source validation, visual QA, derived-data export, recording-disjoint splitting, and YOLO workflow |
| `03_thermal_dataset2_eda.ipynb` | Dataset 2-only EDA: class counts, recording durations, annotation mismatches, bounding-box geometry, target locations, and temporal-dependence checks. Reads validated manifests and raw annotations; writes derived summaries and figures only. |
| `01_data_audit_and_cleaning.ipynb` | Provenance, data issues, preprocessing, and split construction |
| `03_baseline_and_model_training.ipynb` | Baseline and neural-network training or fine-tuning |
| `04_optimization_and_evaluation.ipynb` | Validation-driven optimization, final test evaluation, and error analysis |
| `05_verification_and_demo.ipynb` | Recorded/simulated workflow, uncertainty states, timing, and limitations |

Rename or split these as the actual architecture requires. Keep the README current and record each notebook's environment, inputs, outputs, and execution order. Retain useful plots and export completed notebooks to PDF for the final code submission.

The EDA notebook reads `data/thermal-ir/manifests/dataset2_videos.csv` and `annotation_issues.csv`, plus the local Dataset 2 annotation files. It writes a derived box-summary CSV to `data/thermal-ir/interim/eda/` and report-ready figures to `results/thermal-ir/eda/dataset2/`; it does not alter raw source files.
