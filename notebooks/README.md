# Notebook timeline

The radar and thermal work are separate tracks. **Notebook 01 is the standalone radar audit. Notebooks 02–07 are the thermal-IR workflow.** Within the thermal track, run 02 before 03; notebooks 04–06 are focused experiments, and 07 is the final comparison after the baseline and balanced-joint experiment are complete.

| Order | Track | Notebook | Role in the workflow |
| --- | --- | --- | --- |
| 01 | Radar | `01_radar_data_audit.ipynb` | Standalone radar data audit; not a prerequisite for the thermal notebooks. |
| 02 | Thermal-IR | `02_thermal_data_preparation_and_baseline.ipynb` | Validate sources, create derived data and recording-disjoint splits, and reproduce the Dataset 2 baseline. **Start here.** |
| 03 | Thermal-IR | `03_thermal_dataset_exploration.ipynb` | Read-only source inventory, annotation-quality checks, geometry, target locations, and cross-source EDA. Run after source-manifest validation in 02. |
| 04 | Thermal-IR | `04_thermal_dataset1_training_and_evaluation.ipynb` | Dataset 1-only training and held-out evaluation; measures Dataset 1 internal generalization. |
| 05 | Thermal-IR | `05_thermal_transfer_learning.ipynb` | Fine-tune the Dataset 2 baseline on Dataset 1, then evaluate the two sources separately. |
| 06 | Thermal-IR | `06_thermal_balanced_joint_training.ipynb` | Train the source-balanced Dataset 1 + Dataset 2 model and evaluate each source separately. |
| 07 | Thermal-IR | `07_thermal_model_comparison.ipynb` | Read-only final comparison of the Dataset 2 baseline and balanced-joint model. Run after 02 and 06. |

Notebooks 04–06 share validated thermal inputs but answer different modeling questions; they are not a single sequential dependency chain.
The EDA notebook reads `data/thermal-ir/manifests/dataset2_videos.csv` and `annotation_issues.csv`, plus the local Dataset 2 annotation files. It writes a derived box-summary CSV to `data/thermal-ir/interim/eda/` and report-ready figures to `results/thermal-ir/eda/dataset2/`; it does not alter raw source files.
