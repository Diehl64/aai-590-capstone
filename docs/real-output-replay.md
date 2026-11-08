# Partial real-output simulated replay

This replay uses saved held-out outputs from the independently evaluated radar and thermal models. The source datasets are not synchronized, so the selected rows are paired only as explicitly simulated scenarios. This is not a measured sensor-fusion evaluation and does not report combined accuracy.

## Available inputs

- Radar: `data/model-outputs/radar-cnn-test-outputs.csv` — 11,050 held-out RadarCNN outputs.
- Thermal: `data/model-outputs/thermal-dataset2-batch32-test-outputs.csv` — 2,631 held-out Dataset 2 thermal outputs.
- RF and acoustic: missing until their owners provide validated held-out output CSVs.

## Run

From the repository root:

```powershell
python src/run_real_output_replay.pysss