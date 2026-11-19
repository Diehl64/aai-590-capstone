# Partial real-output simulated replay

This replay uses saved held-out outputs from the independently evaluated radar, thermal, and acoustic models. The source datasets are not synchronized, so the selected rows are paired only as explicitly simulated scenarios. This is not a measured sensor-fusion evaluation and does not report combined accuracy.

## Available inputs

- Radar: `data/model-outputs/radar-cnn-test-outputs.csv` — 11,050 held-out RadarCNN outputs.
- Thermal: `data/model-outputs/thermal-dataset2-batch32-test-outputs.csv` — 2,631 held-out Dataset 2 thermal outputs.
- Acoustic: `data/model-outputs/acoustic-cnn-tuned-test-outputs.csv` — 57,015 held-out CNN-Tuned outputs. The drone decision uses threshold 0.344, the 1% false-alarm point chosen on clean validation. The score is the raw probability of the predicted class.
- RF is the only missing sensor.

`first_clean_rf` in `src/run_real_output_replay.py` picks an RF row only when `--rf-manifest` (`data/rf-split-manifest.csv`) gives the same class as the predicted label, and the image is not one of the 41 test files with a byte-identical copy outside the test split. Those filenames and the chosen output ids are recorded in the runner, checked on 2026-11-18. The false-alarm exception is `rf-test-dronerf_046542.png`: predicted Machine, true class Benign. The manifest is not on this branch. Scenarios 001–016 pass no RF row. Scenarios 017–023 add one: agreement, a Benign image called Machine, an RF Benign miss, RF alone, a jam, delayed RF, and low-quality RF.

DADS has no source or site label, so these acoustic scores do not measure generalization to a new site.

## Run

From the repository root:

```powershell
python src/run_real_output_replay.py
```

The script validates the radar, thermal, and acoustic CSVs before use and writes:

`results/real-output-replay/real-output-replay.json`

## Current scenarios

The first ten scenarios show simulated agreement, disagreement, non-drone predictions, missing radar or thermal evidence, delayed radar or thermal evidence, and a simulated low-quality thermal state. `sim-real-001` is `all_three_predict_drone` and `sim-real-010` is `all_non_drone_predictions`. Each of those ten also carries an acoustic row. Six scenarios add the acoustic cases:

- `sim-real-011` `acoustic_only_sensor_available`: radar and thermal are missing, and acoustic predicts drone.
- `sim-real-012` `radar_thermal_drone_acoustic_disagrees`: radar and thermal predict drone, and acoustic predicts no drone.
- `sim-real-013` `only_acoustic_hears_drone`: acoustic predicts drone while radar predicts human and thermal predicts no drone.
- `sim-real-014` `acoustic_missing`: the acoustic row is missing.
- `sim-real-015` `acoustic_delayed`: the acoustic evidence is delayed.
- `sim-real-016` `acoustic_low_quality`: the acoustic evidence is low quality.

RF is the only sensor represented as missing in every scenario. Every scenario is marked `simulated: true` and `review_required: true`.

The replay is a test of software behavior and operator review handling. It does not establish real-world sensor association, synchronized timing, calibrated combined confidence, or operational detection performance.

## Scenario-status figure

`results/real-output-replay/scenario-evidence-status-matrix.png` visualizes the evidence state for all sixteen simulated scenarios. It is a presentation aid for explaining available, missing, delayed, and low-quality evidence; it does not show real-world sensor fusion performance.
