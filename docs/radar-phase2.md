# Phase 2: grouped radar split and baseline

## Proposed modeling decision

The first coarse task maps `D1`–`D6` to `drone`, all bird labels (`black-headed gull`, `heron`, `pigeon`, `raven`, `seagull`, and `seagull and black-headed gull`) to `bird`, and `human_run`/`human_walk` to `human`. The `CR` corner-reflector measurements remain explicitly excluded from these three-class metrics. They are retained in the manifest for accounting and are not silently treated as an unknown class. The mapping is a proposal for team approval, not evidence that the labels are interchangeable in every operating context.

The committed [split manifest](../data/radar-split-manifest.csv) assigns complete measurement IDs to train, validation, or test. It was produced with seed `590`, a deterministic class-wise greedy assignment targeting 70%/15%/15% of segments. No measurement is divided across partitions. The manifest includes all 19 reflector measurements as `excluded_reflector` and records source labels, proposed classes, and segment counts.

The manifest is based on the checksum-verified audit tables. When the official NPY is loaded, `src/radar_baseline.py` independently validates the `(130, 6)` schema and reconstructs the same assignments from the same seed. A mismatch should stop the run and trigger investigation rather than silently changing the split.

## Leakage and coverage limits

The split prevents leakage at the measurement-ID level. The source audit shows that every measurement appears in multiple *published* splits, so those published split fields are not used for evaluation. The dataset does not document enough session, subject, or target identity to prove that different measurement IDs are independent. Shared recording sessions or repeated targets could therefore remain across our partitions. This is a documented limitation, not a claim of independent generalization.

The manifest totals are 50,491 train segments, 11,047 validation segments, and 11,050 test segments after reflector exclusion. Exact class coverage must be checked from the manifest before training; rare fine labels such as pigeon and raven cannot be expected in every partition. Results apply only to the proposed coarse labels and this target-centered dataset.

## Baseline and neural-network boundary

The baseline computes five per-segment magnitude statistics (mean, standard deviation, maximum, and 25th/75th percentiles) and predicts by nearest class centroid fitted on training measurements only. It reports accuracy, macro F1, per-class precision/recall/F1, and a row-normalized-by-count confusion matrix in `radar-baseline-metrics.json`. It requires the official file supplied through `--data`; the raw dataset is not committed.

`src/radar_neural_network.py` records the next model contract: a train-from-scratch network using the same grouped manifest, training-only preprocessing, and the same held-out metrics. It intentionally contains no unmeasured performance claim. Framework and architecture selection remain open until the baseline and resource constraints are reviewed.

Run the baseline after downloading and verifying the official file:

```bash
.venv/bin/python src/radar_baseline.py \
  --data /absolute/path/data_SAAB_SIRS_77GHz_FMCW.npy \
  --output results/radar-baseline
```

This phase does not add RGB/thermal verification, event coordination, Lattice integration, or physical response behavior.
