# Multimodal capstone roadmap

## Locked scope claim

We evaluate whether calibrated RF, radar, and a future thermal or acoustic model can be combined in simulated, time-aligned scenarios to produce a more useful assessment of whether an observed track is an attack drone. This is a software proof of concept, not validation of synchronized real-world sensors. The current radar, RF, and candidate verification datasets capture different events and must be evaluated independently.

## Work phases

1. **Individual models.** Finalize one model per selected modality. Each model must preserve a held-out test split and produce a common result record with `event_id`, `timestamp`, `sensor_type`, `attack_drone_probability`, uncertainty fields, data-quality score, and model version.
2. **Calibration.** Fit Platt scaling or isotonic calibration on validation predictions only. Evaluate calibrated outputs on untouched test predictions with reliability plots and Brier score. A raw class score must not be described as a probability.
3. **Scenario generation.** Pair saved model outputs into explicitly simulated one-second timelines. Include agreement, disagreement, missing sensor, delayed sensor, and low-quality evidence cases. Mark every scenario and output as simulated.
4. **Transparent fusion.** Combine calibrated probabilities with documented conservative weights and sensor-quality handling. Do not multiply probabilities as if sensors were perfectly independent. Return a fused probability, uncertainty interval, contributing sensors, and an explanation.
5. **Evaluation.** Compare the best individual model, RF plus radar, and all selected modalities within the simulated scenarios. Report stability, sensitivity to weights, missing-sensor behavior, and uncertainty handling. Do not claim improved real-world detection without paired observations and ground truth.

## Current state

Radar audit, measurement-disjoint split, nearest-centroid baseline, from-scratch RadarCNN, CUDA run, and simulated replay states are complete. RF and thermal/acoustic model adoption, calibration, fusion, and any Lattice publisher remain future work. The DADS audio result and any thermal result require committed code, dataset provenance, split evidence, calibration metrics, and reproducible outputs before inclusion.

## Decision gates

- Select exactly one additional modality for the first integrated demonstration.
- Record dataset license, labels, recording-level split policy, and access before implementation.
- Keep synchronized multimodal datasets such as MMAUD as an optional alternative until access, scope, and compute are confirmed.
- Keep Lattice integration blocked until Phases 1–5 produce one reviewed simulated-events file.
