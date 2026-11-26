# Coordination agent interface

`src/agent_interface.py` defines what the coordination agent reads, how it turns each sensor's output into a common hypothesis, how it labels an event, and what alert it produces. Tests are in `tests/test_agent_interface.py`. It is the "Coordination agent" item in `docs/project-management-plan.md`.

## What the agent does and does not do

The agent combines evidence from RF, radar, thermal, and acoustic for one event and produces an alert for operator review. It may **recommend** which sensor to ask next.

It does not:
- control sensors or drones, schedule anything, or start a response;
- calculate a fused detection probability;
- produce an alert without review. The schema rejects any alert with `review_required` false, and any alert not marked `simulated`, because the current datasets are not synchronized.

The status rule is passed in as a function (`status_rule`), so it can be replaced later, for example by a model trained on synchronized recordings, without changing the alert schema.

## Input: one observation per sensor

An `AgentObservation` is one `SensorEvidence` record from `src/synthetic_replay.py`, plus:
- `arrival_s`: seconds after the event opened, or `None` if never received;
- `score_calibrated`: whether the score is calibrated.

`observation_from_handoff()` builds an observation from one row of a held-out handoff CSV (`docs/model-output-handoff.md`):
- It accepts only `split = test`. Training and validation rows would leak, and production rows are not part of replay.
- It uses `calibrated_score` when the column is present and not empty, and sets `score_calibrated` to true. Otherwise it uses `score`.

Scores must be finite and between 0 and 1. An alert accepts one observation per sensor and rejects observations from sensors it was not told to expect.

## Observation state

Each observation has one state at the event's deadline (`deadline_s`):

| State | When |
| --- | --- |
| `usable` | evidence is available and arrived by the deadline |
| `missing` | no evidence |
| `delayed` | marked delayed, or available but arrived after the deadline |
| `low_quality` | marked low quality |

Only `usable` observations vote.

## Label map

Each sensor's label is normalized (lowercase; `-` and spaces become `_`) and mapped to one hypothesis. A label with no mapping raises an error instead of being guessed.

| Sensor | `drone_like` | `not_drone` | `other` | `uncertain` |
| --- | --- | --- | --- | --- |
| RF | Machine | Benign, Human, Wildlife | Broadband_Jam, Narrowband_Jam | uncertain |
| Radar | drone | bird, human | | |
| Thermal | drone | no_drone, bird | | |
| Acoustic | drone | no_drone | | |

RF Machine is a cue for machine-generated RF activity, not a confirmed drone. On its own it can never confirm an event: confirmation needs a second sensor with the same hypothesis, and every alert, confirmed or not, still requires operator review. A jam is an RF alert of its own (`other`), not evidence for or against a drone.

## Score floors

A `drone_like` or `not_drone` hypothesis becomes `uncertain` when its score is below the sensor's floor. A score exactly at the floor counts. Floors must come from validation outputs, never from test. Thermal is the exception: its score is the maximum detection confidence, so a `not_drone` call stays `not_drone` even when the score is below the floor. The floor still applies to a thermal `drone` call.

| Sensor | Rows | Floor | `uncertain` | What `score` means | Threshold source |
| --- | ---: | ---: | --- | --- | --- |
| RF | 2,400 | 0.45 | 4 (1 Benign, 1 Human, 2 Wildlife). All 648 Machine calls stay `drone_like`. | calibrated probability of the predicted class | Machine threshold chosen on validation (`results/rf-intrusion/run_config.json`) |
| Acoustic | 57,015 | 0.344 | 0 | probability of the predicted class | CNN-Tuned 1% false-alarm threshold on clean validation (`docs/acoustic-model-evidence.md`) |
| Radar | 11,050 | 0.60 | 419 (200 drone, 121 bird, 98 human) | top raw softmax score | development placeholder. RadarCNN decides by argmax and has no validation score threshold (`docs/radar-model-results.md`) |
| Thermal | 2,631 | 0.25 | 0. The 796 no_drone calls stay `not_drone` and the 1,835 drone calls stay `drone_like`. | YOLO's highest detection confidence, not the probability of the predicted class | threshold selected on Dataset 2 validation (`docs/thermal_ir_pipeline.md`) |

These counts were recomputed on 2026-11-19 with `observation_from_handoff()` and `hypothesis()` on the four held-out CSVs, using the floors in this table. The counts were not used to choose a floor. The radar placeholder can be replaced when a floor is chosen from radar validation outputs.

## Status rules

`decide_status()` applies these rules in order. The first rule that matches decides. Only expected sensors are considered. An expected sensor with no observation counts as missing. Only a usable observation that has a prediction votes, and `other` and `uncertain` never count for or against a drone.

1. **Conflicting:** at least one vote is `drone_like` and at least one is `not_drone`. This holds even when one side has a majority, and even when another expected sensor is missing, delayed, or low quality. `leading_hypothesis` is empty.
2. **Confirmed:** at least two sensors share the same definitive hypothesis (`drone_like` or `not_drone`). That shared hypothesis is `leading_hypothesis`. This also holds when another expected sensor is missing, delayed, or low quality.
3. **Unverified:** an expected sensor is missing, delayed, or low quality. `leading_hypothesis` is the definitive hypothesis that has any support, or empty when none does.
4. **Unknown:** no gaps remain, and the votes neither conflict nor confirm. That is one supporting sensor, or only `other` and `uncertain` votes, or usable records with no prediction. `leading_hypothesis` is that one definitive hypothesis, or empty when there is none. `reasons` then ends with `single_modality_support` or `no_definitive_evidence`.

`reasons` lists each hypothesis that received votes, with its sensors (for example `drone_like:radar,rf`), then each gap as `{sensor}_{state}` (for example `thermal_missing`, `acoustic_delayed`).

The radar-only replay statuses map onto these: confirmed → confirmed, conflicting → conflicting, and pending, timeout, or unavailable → unverified (`VERIFICATION_TO_ALERT`).

## Request recommendations

`recommend_requests()` lists which expected sensors to ask for next. It is advice only, and nothing is triggered.
- No request is made once an event is confirmed or conflicting. A conflict goes to the operator.
- Otherwise it lists every expected sensor without usable evidence, in the order acoustic, radar, thermal (`DEFAULT_REQUEST_ORDER`), then any others.

RF is not in the default order, because RF is the first-stage cue that opens an event. A different strategy can pass its own order.

## Output: the alert

`build_alert()` returns an `Alert` with the event ID, status, leading hypothesis, reasons, a summary for each expected sensor (state, prediction, hypothesis, score, whether the score is calibrated, model version, source reference, arrival time), the missing and delayed sensors, and the deadline. `to_dict()` turns it into JSON.

Every alert carries `simulated: true`, `review_required: true`, an empty `operator_disposition`, and two notes: no fused detection probability is calculated, and scores are raw model outputs unless `score_calibrated` is true.

## Limitations

- The RF, radar, thermal, and acoustic datasets are not synchronized. Alerts built from them are simulated and do not measure detection performance.
- The RF, acoustic, and thermal floors come from validation-selected thresholds. The radar floor of 0.60 is a development placeholder, because RadarCNN has no validation score threshold; it must not be reported as validated.
- Radar and thermal scores are not calibrated, so a radar 0.9 and a thermal 0.9 do not mean the same thing.
- The status rules are fixed rules proposed for team review. They do not weigh one sensor above another.
- The 25-record saved-output replay is now in `main`. The agent run over it and the comparison of the fixed rules with the agent's cascade come in PR #57. The 25 records repeat some evidence, so they are not 25 independent trials.
