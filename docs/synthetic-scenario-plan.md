# Synthetic scenario plan

This catalog defines the five local-replay scenarios used to demonstrate how separate RF, radar, thermal/vision, and acoustic model outputs can be displayed together for an operator. It is a software demonstration plan, not a paired-sensor dataset and not a measured sensor-fusion experiment.

The scenario names, evidence states, and expected operator actions are in [`data/synthetic-scenario-catalog.csv`](../data/synthetic-scenario-catalog.csv). The current words such as `drone`, `uncertain`, and `missing` describe intended development cases. They are not final model scores or claims about one real-world event.

## Before a scenario becomes a report result

For each sensor record, the team must retain:

- the independently evaluated model version;
- the source prediction or saved output identifier;
- the dataset and held-out split used for that output;
- whether the evidence was available, missing, delayed, or low quality; and
- the simulated-event label and the reason the records were paired.

The development placeholders in `src/run_synthetic_scenarios.py` stay marked as placeholders. Replace them only after the RF, radar, thermal/vision, and acoustic components have committed their reproducible artifacts and outputs. Do not calculate or present a combined probability as a validated real-world result.

## Team handoff

| Modality | Needed from model owner | Status needed before replay use |
| --- | --- | --- |
| RF | Saved held-out predictions, model version, metric summary, and source reference | Reproducible evaluation committed |
| Radar | Saved held-out predictions, model version, metric summary, and source reference | Reproducible evaluation committed |
| Thermal/vision | Saved held-out predictions, model version, metric summary, and source reference | Reproducible evaluation committed |
| Acoustic | Saved held-out predictions, model version, metric summary, and source reference | Reproducible evaluation committed |

Every completed scenario still requires a human reviewer. The local replay is intended to show evidence, uncertainty, conflict, and missing-data behavior; it does not make an autonomous decision.
