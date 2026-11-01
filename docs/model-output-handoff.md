# Model-output handoff for synthetic replay

Each modality owner must provide a CSV of saved **held-out test** outputs before the local replay replaces its placeholders. The schema is in [`data/model-output-handoff-template.csv`](../data/model-output-handoff-template.csv).

## Required fields

| Field | Purpose |
| --- | --- |
| `output_id` | Unique row identifier. |
| `sensor_type` | One of `rf`, `radar`, `thermal`, or `acoustic`. |
| `source_observation_id` | Identifier from the source dataset; not a fabricated shared-event ID. |
| `split` | Must be `test`; do not supply training or validation outputs. |
| `timestamp` | Source timestamp when available; otherwise a documented value such as `source-time-unavailable`. Radar exports use `relative_seconds:<value>` because the source provides within-measurement relative time rather than an absolute clock time. |
| `predicted_label` | The model's predicted class. |
| `score` | Raw model score from 0 through 1. It must not be called a calibrated probability without calibration evidence. |
| `model_version` | Exact model or experiment version. |
| `dataset_id` | Dataset identifier from the repository manifest. |
| `source_output_ref` | Path or stable reference to the saved model-output artifact. |

## Validate before handoff

```bash
python src/validate_model_outputs.py path/to/held_out_outputs.csv
```

The validator checks required fields, unique row IDs, supported sensors, a held-out test split, and score range. Passing it does not establish that outputs from different datasets describe the same real-world event. The replay pairs them only in explicitly simulated scenarios.

## Owner checklist

Each owner should commit or provide the model code, environment/dependency specification, dataset provenance, split policy, metrics, confusion matrix where applicable, and this validated output CSV. The acoustic output must also state the source/site-generalization limitation recorded in [acoustic-model-evidence.md](acoustic-model-evidence.md).

## Radar export

`src/radar_neural_network.py` writes `radar-test-outputs.csv` beside its metrics after a training run. Each row contains one held-out radar segment, its source relative time, prediction, top raw softmax score, and the model/dataset identifiers required by this handoff. The score is a model output, not a calibrated probability. Artifact references are filenames so local absolute paths are not recorded.
