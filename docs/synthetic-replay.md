# Synthetic local-replay foundation

This is development scaffolding for the capstone's evidence-based local replay. It supports RF, radar, thermal/vision, and acoustic records in one explicitly simulated event. It does not generate sensor data, train a fusion model, calculate a fused probability, or establish real-world sensor-fusion performance.

## What is in the foundation

`src/synthetic_replay.py` defines one record per sensor with an event ID, timestamp, sensor type, availability state, model prediction, raw model score, model version, and evidence reference. `create_scenario` requires all records in a scenario to share one event ID and timestamp, and it always requires human review.

`src/run_synthetic_scenarios.py` writes five placeholder-only development scenarios:

1. An RF Machine cue appears alongside radar, thermal, and acoustic drone predictions; the RF cue is not a confirmed drone.
2. RF is uncertain while radar, thermal, and acoustic evidence support a drone hypothesis.
3. Thermal evidence is missing while acoustic evidence remains available.
4. RF, radar, thermal, and acoustic evidence conflict.
5. RF and radar predict human activity while thermal and acoustic predict no drone.

Every placeholder record has `placeholder_value: true`, `model_version: "placeholder-not-a-model"`, and a `placeholder://` source reference. They are not model metrics, probabilities, or evidence about a real event. Keep these development fixtures labeled as placeholders; use the separate saved-output replay for evaluated model evidence.

## Relationship to saved-output replay

The five placeholder cases are separate from the [saved-output replay](real-output-replay.md). As of the November 25 review, main at `5fc4dca` contains 16 radar/thermal/acoustic scenarios and all four modality handoffs, including RF. The integration from PR #55 is prepared and tested on `tony/replay-integration-review` with 25 four-sensor records, including a repeated evidence combination. Teammate review and merge remain pending. Do not count placeholder cases as evaluated saved-output scenarios or generate replacement RF predictions.

Saved-output scenarios must retain the originating dataset, split, model version, and source output identifier. Their pairing and evidence availability are simulated; all scenarios require human/operator review and provide no measured real-world fusion accuracy.

## Run

```bash
python src/run_synthetic_scenarios.py --output results/synthetic-replay
```

The resulting JSON remains separate from measured-model results and from the saved-output replay JSON. The multisensor-comparison task must retain the simulated label, document the source output for every non-placeholder record, and preserve the human-review requirement.

The [synthetic scenario plan](synthetic-scenario-plan.md) defines the five development cases and the model-output handoff requirements for using evaluated evidence.
