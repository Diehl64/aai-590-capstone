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

RF Machine is a cue for machine-generated RF activity, not a confirmed drone. A jam is an RF alert of its own (`other`), not evidence for or against a drone.

## Score floors

A `drone_like` or `not_drone` hypothesis becomes `uncertain` when its score is below the sensor's floor. A score exactly at the floor counts. Floors must come from validation outputs, never from test. Thermal is the exception: its score is the maximum detection confidence, so a `not_drone` call stays `not_drone` even when the score is below the floor. The floor still applies to a thermal `drone` call.

| Sensor | Floor | Source | What `score` means | Effect on the held-out CSV |
| --- | --- | --- | --- | --- |
| RF | 0.45 | Machine threshold chosen on validation (`results/rf-intrusion/run_config.json`) | calibrated probability of the predicted class | 4 of 2,400 rows `uncertain` (1 Benign, 1 Human, 2 Wildlife); all 648 Machine calls stay `drone_like` |
| Acoustic | 0.344 | CNN-Tuned 1% false-alarm threshold on clean validation (`docs/acoustic-model-evidence.md`) | probability of the predicted class | no held-out row `uncertain` |
| Radar | 0.60 | placeholder. RadarCNN decides by argmax and has no validation score threshold (`docs/radar-model-results.md`) | top raw softmax score | 419 of 11,050 rows `uncertain` (200 drone, 121 bird, 98 human) |
| Thermal | 0.25 | validation-selected decision threshold (`docs/thermal-baseline-evidence.md`) | YOLO's highest detection confidence, not the probability of the predicted class | 796 no_drone calls stay `not_drone`; 1,835 drone calls stay `drone_like` |

The effects were checked on 2026-11-19 with `observation_from_handoff()` on the committed held-out CSVs. They show what the current floors do; they were not used to choose any floor. The radar placeholder can be replaced when a floor is chosen from radar validation outputs.

## Status rules

`decide_status()` applies these rules in order to the usable observations of the expected sensors. The first rule that matches decides.

1. **Conflicting:** at least one sensor says `drone_like` and at least one says `not_drone`. This holds even when one side has a majority.
2. **Confirmed:** at least two sensors share the same definitive hypothesis (`drone_like` or `not_drone`).
3. **Unverified:** an expected sensor is missing, delayed, or low quality.
4. **Unknown:** everything else, for example a single supporting sensor with no gaps, or only `other` and `uncertain` votes.

`other` and `uncertain` never count as votes for or against a drone. The alert's `leading_hypothesis` is the definitive hypothesis that has support, and is empty for conflicting events. `reasons` lists the votes by hypothesis (for example `drone_like:radar,rf`) and each gap (for example `thermal_missing`).

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
- The RF, acoustic, and thermal floors come from validation. The radar floor is the placeholder 0.60, because the model has no validation score threshold.
- Radar and thermal scores are not calibrated, so a radar 0.9 and a thermal 0.9 do not mean the same thing.
- The status rules are fixed rules proposed for team review. They do not weigh one sensor above another.
- The agent run over the replay scenarios and the comparison of the fixed rules with the agent's cascade will be added after the RF and acoustic replay PRs merge.
