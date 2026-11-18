# Notebooks

Record each notebook's environment, inputs, outputs, and run order. Retain useful plots and export completed notebooks to PDF for the final code submission.

## Run order

1. `01_radar_data_audit.ipynb` audits the radar file. It does not train a model and does not feed the RF notebook.
2. `rf_machine_detection.ipynb` trains and evaluates the RF screen on this branch.
3. `acoustic_drone_detection.ipynb` is the acoustic notebook on branch `acoustic-pipeline`. It is not in this checkout.

## `01_radar_data_audit.ipynb`

Environment: NumPy, pandas, matplotlib, and a Jupyter kernel.

Inputs: `RADAR_DATA_PATH`, the official local `.npy` download. The raw file stays outside git. Read `docs/radar-data-audit.md` first.

Outputs: audit prints and plots from that file. This notebook does not evaluate a classifier.

## `rf_machine_detection.ipynb`

Environment: Google Colab with an A100, TensorFlow 2.21.0, seed 42, images 128 × 128, batch size 32. The RF packages in `requirements-training.txt` are `tensorflow==2.21.0`, `kagglehub`, pandas, scikit-learn, and matplotlib. The Windows 11 RTX 5080 block in that file is a separate install.

Inputs: the Kaggle dataset `hector484/unified-multi-class-rf-intrusion-dataset`, and `data/rf-split-manifest.csv`.

Outputs: `results/rf-intrusion/` (including `run_config.json`, the validation files, the test metrics, and the figures) and the held-out copy `data/model-outputs/rf-cnn-test-outputs.csv`. The `.keras` weights stay out of git. `results/rf-intrusion/rf-production-outputs.csv` is the production split and is not the handoff.

Run order on Colab: section 1 downloads the dataset, section 2 builds the assignment split, and section 7 chooses the screen on validation and scores the test set once. Section 6 still shows an earlier exploratory test sweep and does not choose the model. Section 10 writes the held-out CSV. Section 11 zips and downloads the results. Sections 1 and 11 are Colab-only. The record of the run is `docs/rf-v4-v5-evidence.md`.

## `acoustic_drone_detection.ipynb`

This notebook is on branch `acoustic-pipeline`. It is not in this checkout.

Environment: Google Colab with an A100. That branch lists `torch`, `datasets`, `optuna`, `scipy`, and `joblib` in `requirements-training.txt`.

Inputs: Hugging Face `Z121mm/drone-audio-detection-samples`. ESC-50 is added as test-time noise. The file list on that branch is `data/acoustic-file-splits.csv`.

Outputs: `data/model-outputs/acoustic-cnn-tuned-test-outputs.csv` and `results/acoustic/`. The write-up on that branch is `docs/acoustic-model-evidence.md`.
