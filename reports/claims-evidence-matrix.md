# Claims and Evidence Matrix

This matrix controls the claims used in the capstone report and presentation. It separates committed evidence from active or missing work.

| Topic | Supported statement | Evidence status | Source |
| --- | --- | --- | --- |
| Radar evaluation | RadarCNN achieved 0.9439 held-out test accuracy and 0.8910 macro F1 on the documented measurement-disjoint radar split. | Committed and documented. | `docs/radar-model-results.md` and `results/radar-neural-network/` |
| Radar errors | The largest listed radar error is human segments predicted as drones; results are segment-level and do not establish false alerts per operating hour. | Committed and documented. | `docs/radar-model-results.md` |
| Radar replay handoff | The repository includes 11,050 saved RadarCNN held-out test outputs. | Committed and validated. | `data/model-outputs/radar-cnn-test-outputs.csv` |
| Thermal evaluation | The Dataset 2-only baseline reports 97.44% drone-present recall and 0.66% bird false-positive rate at its validation-selected threshold. | Committed baseline evidence and held-out handoff. | `docs/thermal_ir_pipeline.md` and thermal output CSV |
| Thermal replay handoff | The repository includes 2,631 held-out thermal test decisions. | Committed and validated. | `data/model-outputs/thermal-dataset2-batch32-test-outputs.csv` |
| Thermal follow-on experiments | Dataset 1-only, Dataset 2 → Dataset 1 transfer, and balanced-joint experiments have saved held-out artifacts. Dataset 1 target-absent results are not bird-rejection results; only Dataset 2 supports that claim. | Repository worktree evidence; pending Dataset 1 access/reuse confirmation and final team review. | `docs/thermal_ir_pipeline.md` and `results/thermal-ir/evaluation/` |
| RF evaluation | v5 is the first-stage screen at weight 1.50, Machine threshold 0.45, and seed 42. v4 remains the stand-alone reference. | Committed. | `docs/rf-v4-v5-evidence.md` and `data/model-outputs/rf-cnn-test-outputs.csv` |
| RF replay handoff | The repository includes 2,400 held-out RF test outputs. The validation-selected threshold, temperature, calibration status, and class semantics are recorded. The `.keras` checkpoint stays outside git. | Committed and validated. | `data/model-outputs/rf-cnn-test-outputs.csv` and `docs/rf-v4-v5-evidence.md` |
| Acoustic evaluation | CNN-Tuned at the validation-selected threshold 0.344 has held-out recall 0.996 and false-alarm rate 0.012 on all 57,015 rewindowed test windows, and full-length recall 0.977. Noise and padding results are reported separately. DADS has no source or site label, so the scores do not measure new-site performance. | Committed | [`docs/acoustic-model-evidence.md`](../docs/acoustic-model-evidence.md) and [`results/acoustic/`](../results/acoustic/) |
| Acoustic replay handoff | The repository includes 57,015 CNN-Tuned held-out test outputs at threshold 0.344. `score` is the probability of the predicted class. A second export of this same run differs only from the fourth decimal place of those scores. | Committed | [`data/model-outputs/acoustic-cnn-tuned-test-outputs.csv`](../data/model-outputs/acoustic-cnn-tuned-test-outputs.csv) |
| Simulated replay | Replay tests software behavior for agreement, conflict, missing, delayed, and low-quality evidence under human review. | Committed foundation; expanded integration remains active. | `docs/local-replay.md` and replay code |
| Sensor fusion | Source datasets are not synchronized. The replay does not measure real-world sensor fusion or combined detection accuracy. | Required project boundary. | Scope, replay, and limitations documentation |
| Human review | Every simulated alert requires human/operator review. | Required project boundary. | Replay and ethics documentation |

## Claims that must not be made

- Real-world synchronized sensor fusion was measured.
- A combined accuracy, combined false-alarm rate, or fused probability was measured.
- Radar results prove field deployment readiness, geographic tracking, or continuous perimeter performance.
- Acoustic results prove new-site performance without source/site evidence.
- RF `Machine` labels confirm a drone without confirmed class semantics and corroborating evidence.
- The system makes autonomous decisions or controls live sensors.

## Evidence still needed before final submission

1. Thermal focused review of environment, Dataset 1 data-access/license record, experiment controls, source-specific error panels, and final claim selection.
2. Clean coordination-agent PR, validation-based thresholds, and fixed-rule comparison.
3. Final cross-model integrity review and report/presentation sources.
