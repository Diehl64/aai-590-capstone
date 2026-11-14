# Claims and Evidence Matrix

This matrix controls the claims used in the capstone report and presentation. It separates committed evidence from active or missing work.

| Topic | Supported statement | Evidence status | Source |
| --- | --- | --- | --- |
| Radar evaluation | RadarCNN achieved 0.9439 held-out test accuracy and 0.8910 macro F1 on the documented measurement-disjoint radar split. | Committed and documented. | `docs/radar-model-results.md` and `results/radar-neural-network/` |
| Radar errors | The largest listed radar error is human segments predicted as drones; results are segment-level and do not establish false alerts per operating hour. | Committed and documented. | `docs/radar-model-results.md` |
| Radar replay handoff | The repository includes 11,050 saved RadarCNN held-out test outputs. | Committed and validated. | `data/model-outputs/radar-cnn-test-outputs.csv` |
| Thermal evaluation | The Dataset 2-only baseline reports 97.44% drone-present recall and 0.66% bird false-positive rate at its validation-selected threshold. | Committed baseline evidence and held-out handoff. | `docs/thermal-baseline-evidence.md` and thermal output CSV |
| Thermal replay handoff | The repository includes 2,631 held-out thermal test decisions. | Committed and validated. | `data/model-outputs/thermal-dataset2-batch32-test-outputs.csv` |
| Thermal Dataset 1 | Dataset 1 EDA may inform future work but is not part of the reported baseline without confirmed access, reuse, and evaluation controls. | Active branch work; not final. | `thermal-ir-pipeline` branch and Group 1 review |
| RF evaluation | RF v4 versus v5 evaluation evidence is documented. | Documentation committed; final output handoff pending. | `docs/rf-v4-v5-evidence.md` |
| RF replay handoff | A held-out RF prediction CSV, exact checkpoint, validation-selected threshold, calibration status, and class semantics are required. | Not yet available. | Group 1 handoff requirement |
| Acoustic evaluation | Acoustic results must be reported from reproducible committed artifacts and must state source/site-generalization limitations. | Baseline and uploaded held-out CSVs available; final operating-point confirmation pending. | `docs/acoustic-model-evidence.md` |
| Acoustic replay handoff | Two validated 57,015-row acoustic test-output CSVs exist as separate operating points. The team must identify the validation-selected operating point. | Ready for integration after patch review and team confirmation. | `acoustic-test-outputs.csv` and `acoustic-test-outputs-0.6.csv` |
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

1. RF held-out output CSV, selected checkpoint, threshold, calibration status, and class semantics.
2. Acoustic selected operating point, optimized-model comparison, controlled-noise results, metrics, and provenance.
3. Thermal focused review of environment, data-access/license record, Dataset 2 error analysis, and Dataset 1 scope decision.
4. Clean coordination-agent PR, validation-based thresholds, and fixed-rule comparison.
5. Final cross-model integrity review and report/presentation sources.