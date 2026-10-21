# Capstone setup and radar audit

Updated: 2026-10-21. Team: Tony, Mostafa, and Jacob.

## Current status

The repository exists at https://github.com/Diehl64/aai-590-capstone.
The first notebook is a documentation-driven radar audit, a completed data inspection rather than a model-training experiment. Its Python cells were executed sequentially against the checksum-verified real dataset on 2026-10-21; captured outputs and versions are in `results/`. Jupyter kernel startup was blocked here, so the JupyterLab steps below and cross-platform compatibility still require team validation.

Read [the project overview](README.md), [radar audit notes](docs/radar-data-audit.md), and [dataset manifest](data/dataset-manifest.csv) before running it. The official Zenodo API identifies the dataset as CC BY 4.0, verified 2026-10-21. Follow the attribution and change-disclosure guidance in the audit notes.

## 1. Get a local copy

Install Git and Python 3 if needed. The team must agree on and record a supported Python version after testing.

For a first clone, run:

```bash
git clone https://github.com/Diehl64/aai-590-capstone.git
cd aai-590-capstone
```

If you already have a clone, open its folder instead. Review `git status` and preserve any local work before updating from GitHub; do not overwrite an existing working copy.

## 2. Create an isolated Python environment

Run the commands for your operating system from the repository root. These use the environment's Python directly, so activation is unnecessary.

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install numpy pandas matplotlib jupyterlab ipykernel
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install numpy pandas matplotlib jupyterlab ipykernel
```

These dependencies cover the audit only. They are not a validated or pinned training environment. Do not add a deep-learning framework until the team selects the modeling approach.

## 3. Obtain and review the candidate dataset

1. Review the CC BY 4.0 license and the attribution guidance recorded in `data/dataset-manifest.csv` and the audit notes.
2. Visit the [official dataset record](https://zenodo.org/records/5896641) and read its `ReadMe.txt`.
3. Download `data_SAAB_SIRS_77GHz_FMCW.npy` from that record. Store it outside the repository. The download is approximately 1.6 GB; loading and inspecting it requires additional memory.
4. The notebook compares the download against the publisher's MD5 value recorded in the manifest before loading. A checksum checks file consistency; it is not a substitute for trusting the source.
5. This NumPy object array requires pickle deserialization. Only enable the trust setting below after reviewing and trusting the official file. Do not load an unknown replacement file.

Do not commit the dataset, credentials, virtual environment, or local absolute paths.

## 4. Set the dataset path and start JupyterLab

Replace the example path with the actual absolute path to your downloaded file. Run these commands in the same terminal session. Set the trust flag only after completing the review above.

### macOS / Linux

```bash
export RADAR_DATA_PATH="/absolute/path/to/data_SAAB_SIRS_77GHz_FMCW.npy"
export TRUST_OFFICIAL_RADAR_PICKLE=yes
.venv/bin/python -m jupyterlab
```

### Windows PowerShell

```powershell
$env:RADAR_DATA_PATH = "C:\absolute\path\to\data_SAAB_SIRS_77GHz_FMCW.npy"
$env:TRUST_OFFICIAL_RADAR_PICKLE = "yes"
.\.venv\Scripts\python.exe -m jupyterlab
```

In JupyterLab, open `notebooks/01_radar_data_audit.ipynb` and select the Python 3 kernel from this environment. Run cells in order. If you change environment variables after Jupyter starts, stop and relaunch Jupyter from the configured terminal.

## 5. Review the audit

The notebook checks file consistency and expected array structure, summarizes labels and measurement groups, counts nonfinite values and edge segments, checks whether measurements occur in multiple published splits, and plots one signal-magnitude example.

Review discrepancies before changing assertions. A successful run does not by itself prove the data is suitable or the evaluation is leakage-free. Inspect more examples per class and determine whether held-out measurement groups cover the intended classes.

The magnitude plot is not a calibrated micro-Doppler representation. This audit does not establish full 3D tracking, paired camera verification, continuous false-alert rates, or model performance.

After a successful real-data run:

- Record the Python/package versions printed in the first cell, operating system, hardware, dataset checksum, and repository commit used.
- Save reviewed notebook outputs. Remove personal paths and other unintended information before committing.
- Record decisions about classes, splits, and limitations in `docs/project-decisions.md`.
- Export the working environment to `requirements-audit.txt` using the appropriate command below. Review it for local paths or unrelated dependencies, then verify installation in a fresh environment before calling it reproducible.

macOS / Linux:

```bash
.venv/bin/python -m pip freeze > requirements-audit.txt
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip freeze | Out-File -Encoding utf8 requirements-audit.txt
```

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Missing `RADAR_DATA_PATH` | Set the variable before starting Jupyter, then relaunch it. |
| File not found | Check the actual downloaded filename and absolute path. |
| Checksum mismatch | Stop; verify the source, version, and whether the download completed. Do not bypass the check. |
| Trust-setting error | Complete source/rights review before explicitly enabling pickle loading. |
| Missing Python package | Confirm Jupyter is using the environment created above. |
| Schema assertion fails | Inspect the actual array and official README; document differences before revising code. |
| Kernel stops or runs out of memory | Review available memory and dataset-loading approach; do not report an incomplete run as successful. |

## Team workflow and next milestone

Confirm Mostafa's and Jacob's GitHub usernames before inviting them as collaborators. Follow [CONTRIBUTING.md](CONTRIBUTING.md), work on focused branches, and request teammate review. Record actual contributions and AI assistance; do not assign work to teammates without agreement.

After the audit, select preprocessing, a baseline, and a neural network training experiment. Plan for the Module 5 train-from-scratch learning outcome and clarify any alternative with the instructor. Lattice is optional; the local capstone demonstration must stand on its own. Physical flight control and interception remain outside this implementation.

## Setup references

- Python virtual environments: https://docs.python.org/3/library/venv.html
- Jupyter installation: https://jupyter.org/install

ChatGPT assisted with this setup draft. The real-data Python audit is complete. Team review, native Jupyter execution, and cross-platform validation remain pending; update `docs/ai-assistance.md` when adopting it.
