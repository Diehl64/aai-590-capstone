# Partial real-output simulated replay

This replay uses saved held-out outputs from the independently evaluated radar and thermal models. The source datasets are not synchronized, so the selected rows are paired only as explicitly simulated scenarios. This is not a measured sensor-fusion evaluation and does not report combined accuracy.

## Available inputs

- Radar: `data/model-outputs/radar-cnn-test-outputs.csv` — 11,050 held-out RadarCNN outputs.
- Thermal: `data/model-outputs/thermal-dataset2-batch32-test-outputs.csv` — 2,631 held-out Dataset 2 thermal outputs.
- RF and acoustic: missing until their owners provide validated held-out output CSVs.

## Run

From the repository root:

```powershell
python src/run_real_output_replay.py
```

The script validates both input CSVs before use and writes:

`results/real-output-replay/real-output-replay.json`

## Current scenarios

The initial ten scenarios show simulated agreement, disagreement, non-drone predictions, missing radar or thermal evidence, delayed radar or thermal evidence, and a simulated low-quality thermal state. RF and acoustic are represented only as missing evidence. Every scenario is marked `simulated: true` and `review_required: true`.

The replay is a test of software behavior and operator review handling. It does not establish real-world sensor association, synchronized timing, calibrated combined confidence, or operational detection performance.

## Scenario-status figure

`results/real-output-replay/scenario-evidence-status-matrix.png` visualizes the evidence state for all ten simulated scenarios. It is a presentation aid for explaining available, missing, delayed, and low-quality evidence; it does not show real-world sensor fusion performance.
