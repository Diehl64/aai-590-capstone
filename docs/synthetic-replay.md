# Synthetic local-replay foundation

This is development scaffolding for the capstone's evidence-based local replay. It supports RF, radar, thermal/vision, and acoustic records in one explicitly simulated event. It does not generate sensor data, train a fusion model, calculate a fused probability, or establish real-world sensor-fusion performance.

## What is in the foundation

`src/synthetic_replay.py` defines one record per sensor with an event ID, timestamp, sensor type, availability state, model prediction, raw model score, model version, and evidence reference. `create_scenario` requires all records in a scenario to share one event ID and timestamp, and it always requires human review.

`src/run_synthetic_scenarios.py` writes four placeholder-only development scenarios:

1. RF, radar, thermal, and acoustic evidence support a drone hypothesis.
2. RF is uncertain while radar, thermal, and acoustic evidence support a drone hypothesis.
3. Thermal evidence is missing while acoustic evidence remains available.
4. RF, radar, thermal, and acoustic evidence conflict.

Every placeholder record has `placeholder_value: true`, `model_version: "placeholder-not-a-model"`, and a `placeholder://` source reference. These values must be replaced only with saved outputs from separately evaluated RF, radar, thermal/vision, and acoustic models. They are not model metrics, probabilities, or evidence about a real event.

## Run

```bash
python src/run_synthetic_scenarios.py --output results/synthetic-replay
```

The resulting JSON remains separate from measured-model results. The later multisensor-comparison task must retain the simulated label, document the source output for every record, and preserve the human-review requirement.

The [synthetic scenario plan](synthetic-scenario-plan.md) defines the five cases and the model-output handoff required before placeholders can be replaced.
