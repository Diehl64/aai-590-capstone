# Notebook timeline

The radar, thermal, RF, and acoustic work are separate tracks. **Notebook 01 is the standalone radar audit. Notebooks 02–07 are the thermal-IR workflow.** Within the thermal track, run 02 before 03; notebooks 04–06 are focused experiments, and 07 is the final comparison after the baseline and balanced-joint experiment are complete. The RF and acoustic notebooks are self-contained and do not depend on the radar or thermal notebooks.

| Order | Track | Notebook | Role in the workflow |
| --- | --- | --- | --- |
| 01 | Radar | `01_radar_data_audit.ipynb` | Standalone radar data audit; not a prerequisite for the thermal notebooks. |
| 02 | Thermal-IR | `02_thermal_data_preparation_and_baseline.ipynb` | Validate sources, create derived data and recording-disjoint splits, and reproduce the Dataset 2 baseline. **Start here.** |
| 03 | Thermal-IR | `03_thermal_dataset_exploration.ipynb` | Read-only source inventory, annotation-quality checks, geometry, target locations, and cross-source EDA. Run after source-manifest validation in 02. |
| 04 | Thermal-IR | `04_thermal_dataset1_training_and_evaluation.ipynb` | Dataset 1-only training and held-out evaluation; measures Dataset 1 internal generalization. |
| 05 | Thermal-IR | `05_thermal_transfer_learning.ipynb` | Fine-tune the Dataset 2 baseline on Dataset 1, then evaluate the two sources separately. |
| 06 | Thermal-IR | `06_thermal_balanced_joint_training.ipynb` | Train the source-balanced Dataset 1 + Dataset 2 model and evaluate each source separately. |
| 07 | Thermal-IR | `07_thermal_model_comparison.ipynb` | Read-only final comparison of the Dataset 2 baseline and balanced-joint model. Run after 02 and 06. |
| — | RF | `rf_machine_detection.ipynb` | Train and evaluate the RF CNN v5 Machine screen; choose it on validation and export the held-out CSV. |
| — | Acoustic | `acoustic_drone_detection.ipynb` | Train and evaluate the acoustic baselines and CNN-Tuned; export the held-out CSV. |

Notebooks 04–06 share validated thermal inputs but answer different modeling questions; they are not a single sequential dependency chain.
The EDA notebook reads `data/thermal-ir/manifests/dataset2_videos.csv` and `annotation_issues.csv`, plus the local Dataset 2 annotation files. It writes a derived box-summary CSV to `data/thermal-ir/interim/eda/` and report-ready figures to `results/thermal-ir/eda/dataset2/`; it does not alter raw source files.

## `rf_machine_detection.ipynb`

Environment: Google Colab with an A100, TensorFlow 2.21.0, seed 42, images 128 × 128, batch size 32. The RF packages in `requirements-training.txt` are `tensorflow==2.21.0`, `kagglehub`, pandas, scikit-learn, and matplotlib. The Windows 11 RTX 5080 block in that file is a separate install.

Inputs: the Kaggle dataset `hector484/unified-multi-class-rf-intrusion-dataset`, and `data/rf-split-manifest.csv`.

Outputs: `results/rf-intrusion/` (including `run_config.json`, the validation files, the test metrics, and the figures) and the held-out copy `data/model-outputs/rf-cnn-test-outputs.csv`. The `.keras` weights stay out of git. `results/rf-intrusion/rf-production-outputs.csv` is the production split and is not the handoff.

Run order on Colab: section 1 downloads the dataset, section 2 builds the assignment split, and section 7 chooses the screen on validation and scores the test set once. Section 6 still shows an earlier exploratory test sweep and does not choose the model. Section 10 writes the held-out CSV. Section 11 zips and downloads the results. Sections 1 and 11 are Colab-only. The record of the run is `docs/rf-v4-v5-evidence.md`.

## `acoustic_drone_detection.ipynb`

Environment: Google Colab with an A100. The acoustic packages in `requirements-training.txt` are `torch`, `datasets`, `optuna`, `scipy`, and `joblib`.

Inputs: Hugging Face `Z121mm/drone-audio-detection-samples`, with the file-level split in `data/acoustic-file-splits.csv`. ESC-50 (`ashraq/esc50`) folds 1–4 are mixed into training audio, and fold 5 is used only for the held-out noise test.

Outputs: `data/model-outputs/acoustic-cnn-tuned-test-outputs.csv` and `results/acoustic/`. The model checkpoints and features stay out of git. The write-up is `docs/acoustic-model-evidence.md`.
