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
| RF evaluation | v5 is the first-stage Machine screen at weight 1.50, seed 42, threshold 0.45, and validation-fitted temperature 1.2933; v4 remains the stand-alone reference. On the 2,400-row test split, accuracy is 0.8513, macro F1 0.8442, Machine recall 0.9050, and Machine precision 0.5586; 249/400 Benign images are called Machine. Excluding 41 test images with exact copies outside the test split leaves Machine recall 0.9048 and Benign→Machine/Machine→Benign counts at 249/16. These are dataset-specific results: earlier exploratory test scores were seen before the screen rule was written, and there are no recording/session IDs to establish recording-level independence. Machine is a drone-like cue, not a confirmed drone. | Committed and documented, with limitations. | `docs/rf-v4-v5-evidence.md`, `results/rf-intrusion/rf_v5_test_metrics.json`, and `results/rf-intrusion/rf_v5_test_duplicate_sensitivity.json` |
| RF replay handoff | The repository includes 2,400 held-out RF test outputs with the selected threshold, temperature, calibration status, and class semantics recorded. | Handoff committed; four-sensor replay integration remains under review in PR #55. | `data/model-outputs/rf-cnn-test-outputs.csv` and `docs/rf-v4-v5-evidence.md` |
| Acoustic evaluation | CNN-Tuned at the validation-selected threshold 0.344 has held-out recall 0.996 and false-alarm rate 0.012 on all 57,015 rewindowed test windows, and full-length recall 0.977. Noise and padding results are reported separately. DADS has no source or site label, so the scores do not measure new-site performance. | Committed. | `docs/acoustic-model-evidence.md` and `results/acoustic/` |
| Acoustic replay handoff | The repository includes 57,015 CNN-Tuned held-out test outputs at threshold 0.344. `score` is the probability of the predicted class. A second export of this same run differs only from the fourth decimal place of those scores. | Committed. | `data/model-outputs/acoustic-cnn-tuned-test-outputs.csv` |
| Simulated replay | The committed replay currently covers radar, thermal, and acoustic evidence. PR #55 proposes adding RF and expanding to 25 explicitly simulated four-sensor scenarios; until that integration is rebased, reviewed, merged, and rerun, do not describe the 25-scenario RF replay as part of main. | Three-sensor foundation committed; RF integration pending review. | `docs/real-output-replay.md`, replay code, and PR #55 |
| Sensor fusion | Source datasets are not synchronized. Pairing saved outputs in replay does not measure real-world sensor fusion, combined detection accuracy, or a fused probability. | Required project boundary. | Scope, replay, and limitations documentation |
| Human review | Every simulated alert requires human/operator review. | Required project boundary. | Replay and ethics documentation |

## Claims that must not be made

- Real-world synchronized sensor fusion was measured.
- A combined accuracy, combined false-alarm rate, or fused probability was measured.
- Radar results prove field deployment readiness, geographic tracking, or continuous perimeter performance.
- Acoustic results prove new-site performance without source/site evidence.
- RF `Machine` labels confirm a drone without confirmed class semantics and corroborating evidence.
- The system makes autonomous decisions or controls live sensors.

## Evidence still needed before final submission

1. Rebase and review PR #55, then regenerate/validate the four-sensor replay on the updated main branch; verify the 25 scenarios remain simulated and require human review.
2. Review and integrate the coordination agent in PR #56; run the agent over the replay scenarios and complete the fixed-rule comparison. Keep the radar 0.60 score floor marked as a placeholder unless a validation-based threshold is established.
3. Thermal focused review of environment, Dataset 1 data-access/license record, experiment controls, source-specific error panels, and final claim selection.
4. Final cross-model integrity review and report/presentation source checks, preserving each model's separate metrics and limitations.
