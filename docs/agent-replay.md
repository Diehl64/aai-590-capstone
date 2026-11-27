# Coordination agent on the simulated replay

This note records the coordination agent run over the committed 25-record saved-output replay, and the comparison of the fixed parallel rule with the agent's cascade. **Every alert is simulated and requires human review.** The agent calculates no fused probability. These results describe how the software behaves on simulated pairings of unsynchronized datasets; they are not detection performance, sensor-fusion accuracy, or false-alarm rates.

The 25 records are not 25 independent trials. Several records reuse the same saved evidence; for example, cases 001 and 017 carry the same rows ([`real-output-replay.md`](real-output-replay.md)). Counts below describe these 25 records only. Each model's own metrics are in its evidence document ([RF](rf-v4-v5-evidence.md), [radar](radar-model-results.md), [thermal](thermal_ir_pipeline.md), [acoustic](acoustic-model-evidence.md)) and are not repeated here.

## Run

From the repository root:

```powershell
python src/run_agent_replay.py
```

It reads [`results/real-output-replay/real-output-replay.json`](../results/real-output-replay/real-output-replay.json) and the four handoff CSVs listed in its `input_files`, and writes [`results/agent-replay/`](../results/agent-replay/):

| File | Contents |
| --- | --- |
| `agent-alerts.json` | One alert and its recommended requests per record, with the rule version, floors, score types, and deadline. |
| `agent-observations.csv` | Decision log: one row per sensor per record (state, prediction, hypothesis, score, whether the score is calibrated, model version, source, arrival). |
| `agent-alerts.csv` | Decision log: one row per record (status, leading hypothesis, reasons, missing and delayed sensors, requests, rule version, floors, deadline, an empty `operator_disposition`, and a timestamp). |
| `fixed-vs-cascade.csv` | Fixed rule versus cascade per record: status, leading hypothesis, sensors used, sensors revealed and left unrevealed, unrevealed sensors that disagree, and `early_stop_masks_conflict`. |

The two log CSVs join on `event_id`. A rerun reproduces every file except the `created_at` timestamps.

## Settings

- Rule version `decide_status-v1`; the status rules are in [`agent-coordination.md`](agent-coordination.md).
- Deadline 5.0 s. A record marked delayed arrives after the deadline and cannot vote; a low-quality record is kept as low quality; a missing record has no prediction.
- Score floors: RF 0.45, acoustic 0.344, and thermal 0.25 (drone calls only) come from each model's validation-selected threshold. **The radar floor of 0.60 is a development placeholder**, because RadarCNN has no validation score threshold; it must not be reported as validated.
- Request order for the cascade: acoustic, radar, thermal. RF opens each event.

## Score type

The replay JSON keeps each model's raw `score`. A floor has to be applied to the score its threshold was set on, so each observation is built from its handoff row (found by the `output_id` in the evidence `source_ref`) through `observation_from_handoff()`. The scenario's injected state and arrival time are kept.

| Sensor | Score used | Why |
| --- | --- | --- |
| RF | `calibrated_score` | The 0.45 Machine threshold was chosen on temperature-scaled validation probabilities. |
| Acoustic | `calibrated_score` | Equal to `score` (temperature 1.000). |
| Radar | `score` | No calibrated score. |
| Thermal | `score` | Detector confidence; no calibrated score. |

In `agent-observations.csv`, every present RF and acoustic row has `score_calibrated` set to true, and every radar and thermal row false. No observation in these 25 records falls below its floor, so no hypothesis is `uncertain`.

## Results

### Fixed parallel rule

All four sensors are read at once.

| Status | Records |
| --- | ---: |
| Confirmed, drone-like | 16 |
| Confirmed, not drone | 2 |
| Conflicting | 6 |
| Unverified | 1 |

Across the 100 sensor rows: 83 usable, 9 missing, 4 delayed, and 4 low quality. Only `rf_only_sensor_available` has recommended requests (acoustic, radar, thermal); a confirmed or conflicting event has none, and conflicts go to the operator.

### Cascade

RF opens the event; acoustic, radar, and thermal are revealed one at a time, stopping as soon as the event is confirmed or conflicting.

| Status | Records |
| --- | ---: |
| Confirmed | 21 |
| Conflicting | 3 |
| Unverified | 1 |

**Sensor use.** The fixed rule uses 4 sensors in every record. The cascade uses 2 in 17 records, 3 in 7, and 4 in 1, an average of 2.36. It stops with at least one sensor unrevealed in 24 of 25 records; only `rf_only_sensor_available` reveals all four.

### Status disagreements and conflicts hidden by early stopping

The two strategies end with different statuses in 3 of 25 records. In all three, the cascade confirms after RF and acoustic agree, while a sensor it never reads disagrees, so the fixed rule reports a conflict (`early_stop_masks_conflict` = true):

| Record | Fixed rule | Cascade | Sensors used (cascade) | Unrevealed sensor that disagrees |
| --- | --- | --- | ---: | --- |
| `radar_drone_thermal_no_drone` | conflicting | confirmed | 2 | radar |
| `radar_human_thermal_drone` | conflicting | confirmed | 2 | radar |
| `radar_thermal_drone_acoustic_disagrees` | conflicting | confirmed | 2 | radar, thermal |

In the other 22 records, the statuses match. In the 3 records where both strategies end conflicting (`only_acoustic_hears_drone`, `rf_machine_false_alarm_others_no_drone`, and `rf_benign_others_drone`), the conflict already appears between RF and acoustic, so the cascade stops after two sensors and still reports it.

## Interpretation

The cascade reads fewer sensors (2.36 on average against 4), but stopping at the first agreement can confirm an event that a later sensor contradicts. In these records, that happened 3 times, each time with radar (and once also thermal) unread. This is a cost of the cascade, not an error in the log: the comparison records the hidden sensors so an operator or a later strategy can account for them. These counts depend on how the 25 records were built and on the fixed request order, so they show the mechanism, not how often it would happen in operation.

## Limitations

- The four datasets are not synchronized; each record pairs saved outputs from different sources. Records are simulated, and every alert requires human review.
- The 25 records reuse some evidence and are not independent trials. Their counts are not performance metrics.
- The radar 0.60 floor is a development placeholder. Radar and thermal scores are not calibrated.
- Delayed, missing, and low-quality states are injected scenario controls, not measured latency or degradation.
- Only one request order and one deadline were run.
