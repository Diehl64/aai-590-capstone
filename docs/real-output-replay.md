# Partial real-output simulated replay

This replay uses saved held-out outputs from the independently evaluated RF, radar, thermal, and acoustic models. The source datasets are not synchronized, so the selected rows are paired only as explicitly simulated scenarios. This is not a measured sensor-fusion evaluation and does not report combined accuracy.

The evaluation record for the RF model is [RF CNN v4 versus v5 evidence](rf-v4-v5-evidence.md).

## Available inputs

- Radar: `data/model-outputs/radar-cnn-test-outputs.csv` — 11,050 held-out RadarCNN outputs.
- Thermal: `data/model-outputs/thermal-dataset2-batch32-test-outputs.csv` — 2,631 held-out Dataset 2 thermal outputs.
- Acoustic: `data/model-outputs/acoustic-cnn-tuned-test-outputs.csv` — 57,015 held-out CNN-Tuned outputs. The drone decision uses threshold 0.344, the 1% false-alarm point chosen on clean validation. The score is the raw probability of the predicted class.
- RF: `data/model-outputs/rf-cnn-test-outputs.csv` — 2,400 held-out outputs from CNN v5, weight 1.50, seed 42 (`rf-intrusion-cnn-v5-w1.50-seed42-selected`). The Machine threshold 0.45 was chosen on validation. Temperature is 1.293297. `score` is the raw softmax probability of the thresholded predicted class, and `calibrated_score` is the temperature-scaled probability of that same class. The replay records `score`. It does not apply a score floor.

`first_clean_rf` in `src/run_real_output_replay.py` keeps an RF row only when `--rf-manifest` (`data/rf-split-manifest.csv`) gives the same class as the predicted label, and the image is not one of the 41 test files with a byte-identical copy outside the test split. Those filenames and the chosen output ids are recorded in the runner, checked on 2026-11-18. The false-alarm exception is `rf-test-dronerf_046542.png`: predicted Machine, true class Benign. The manifest is not on this branch, so the runner uses the recorded output ids. Scenarios 001–016 use a Machine row when the other sensors predict a drone and a Benign row when they do not. Scenarios 017–025 use the RF-specific rows below.

DADS has no source or site label, so these acoustic scores do not measure generalization to a new site.

## Run

From the repository root:

```powershell
python src/run_real_output_replay.py
python src/plot_replay_scenarios.py
```

The script validates the RF, radar, thermal, and acoustic CSVs before use and writes:

`results/real-output-replay/real-output-replay.json`

The plot writes `results/real-output-replay/scenario-evidence-status-matrix.png`.

## Current scenarios

The JSON lists four sensors, `rf`, `radar`, `thermal`, and `acoustic`, and 25 scenarios. `missing_sensor_types` is empty. Every scenario is marked `simulated: true` and `review_required: true`.

- `sim-real-001` `all_three_predict_drone`: RF Machine, radar drone, thermal drone, acoustic drone.
- `sim-real-002` `radar_drone_thermal_no_drone`: RF Benign, radar drone, thermal no drone, acoustic no drone.
- `sim-real-003` `radar_bird_thermal_no_drone`: RF Benign, radar bird, thermal no drone, acoustic no drone.
- `sim-real-004` `radar_human_thermal_drone`: RF Machine, radar human, thermal drone, acoustic drone.
- `sim-real-005` `thermal_missing`: thermal is missing. RF is Machine, and radar and acoustic predict drone.
- `sim-real-006` `thermal_delayed`: thermal is delayed. RF is Machine, and radar and acoustic predict drone.
- `sim-real-007` `radar_missing`: radar is missing. RF is Machine, and thermal and acoustic predict drone.
- `sim-real-008` `radar_delayed`: radar is delayed. RF is Machine, and thermal and acoustic predict drone.
- `sim-real-009` `thermal_low_quality`: thermal is low quality. RF is Machine, and radar and acoustic predict drone.
- `sim-real-010` `all_non_drone_predictions`: RF Benign, radar human, thermal no drone, acoustic no drone.
- `sim-real-011` `radar_and_thermal_missing`: radar and thermal are missing. RF is Machine, and acoustic predicts drone.
- `sim-real-012` `radar_thermal_drone_acoustic_disagrees`: RF Benign, radar drone, thermal drone, acoustic no drone.
- `sim-real-013` `only_acoustic_hears_drone`: RF Benign and acoustic drone, while radar predicts human and thermal predicts no drone.
- `sim-real-014` `acoustic_missing`: acoustic is missing. RF is Machine, and radar and thermal predict drone.
- `sim-real-015` `acoustic_delayed`: acoustic is delayed. RF is Machine, and radar and thermal predict drone.
- `sim-real-016` `acoustic_low_quality`: acoustic is low quality. RF is Machine, and radar and thermal predict drone.
- `sim-real-017` `all_four_predict_drone`: RF Machine, radar drone, thermal drone, acoustic drone.
- `sim-real-018` `rf_machine_false_alarm_others_no_drone`: RF calls a Benign image Machine (`rf-test-dronerf_046542.png`). Radar predicts human, and thermal and acoustic predict no drone.
- `sim-real-019` `rf_benign_others_drone`: RF Benign, while radar, thermal, and acoustic predict drone.
- `sim-real-020` `rf_only_sensor_available`: RF Machine is the only sensor present.
- `sim-real-021` `rf_jamming_others_drone`: RF Broadband_Jam, while radar, thermal, and acoustic predict drone.
- `sim-real-022` `rf_delayed`: RF Machine is delayed. Radar, thermal, and acoustic predict drone.
- `sim-real-023` `rf_low_quality`: RF Machine is low quality. Radar, thermal, and acoustic predict drone.
- `sim-real-024` `rf_missing`: RF is missing. Radar, thermal, and acoustic predict drone.
- `sim-real-025` `radar_low_quality`: radar is low quality. RF is Machine, and thermal and acoustic predict drone.

The replay is a test of software behavior and operator review handling. It does not establish real-world sensor association, synchronized timing, calibrated combined confidence, or operational detection performance.

## Limitations

The RF images are not from the same events as the radar, thermal, or acoustic rows. A Machine label is a cue for a mechanical or UAV-like target, not a confirmed drone. On the selected test screen, the RF model calls 249 of 400 Benign images Machine, about 62%. The agent score floor is still the placeholder 0.60, above the 0.45 validation threshold, and this replay does not apply it.

## Scenario-status figure

`results/real-output-replay/scenario-evidence-status-matrix.png` visualizes the evidence state for all twenty-five simulated scenarios and all four sensors. It is a presentation aid for explaining available, missing, delayed, and low-quality evidence. It does not show real-world sensor fusion performance.
