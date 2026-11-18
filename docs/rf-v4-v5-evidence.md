# RF CNN v4 versus v5 evidence

This record summarizes saved outputs embedded in Mostafa's committed RF evaluation notebook at `origin/mostafa` commit `fe57243`. The RF model evaluates six RF-spectrogram classes: Benign, Broadband_Jam, Human, Machine, Narrowband_Jam, and Wildlife. It is evaluated independently from radar, thermal/IR, and acoustic work.

## Class semantics

Checked the Kaggle card for `hector484/unified-multi-class-rf-intrusion-dataset` on 2026-11-18. Its class list gives one sentence each. It does not give a frequency band, a protocol, or a way to separate a drone link from other mechanical targets. The same card says the images mix 77 GHz FMCW radar captures of humans, birds, and drones, DroneRF UAV recordings, SDR scans, and interference recordings, and it does not say which source produced a given image.

The folder names in this project are `Benign`, `Broadband_Jam`, `Human`, `Machine`, `Narrowband_Jam`, and `Wildlife`. The card writes the jam classes as "Broadband Jam" and "Narrowband Jam". `LABEL_MAP` in `src/agent_interface.py` on branch `agent-pipeline` (commit `0642645`) lowercases the label and turns spaces and hyphens into underscores, so both spellings use the same key. That file is not on this branch. The comment on the map marks it as proposed for team review. The hypothesis column below is that map.

| RF class | Meaning on the Kaggle card | Agent hypothesis |
| --- | --- | --- |
| Machine | RF signatures indicating mechanical or UAV-like targets. The card does not define this class as a confirmed drone. | `drone_like`: a drone-like cue that still needs confirmation |
| Benign | Normal background RF activity and routine ambient transmissions. The card does not name those transmissions. | `not_drone` |
| Human | Radar reflections and micro-Doppler patterns from human motion. | `not_drone` |
| Wildlife | Biological signatures, with birds as the example, included so a model can avoid false alarms. The card does not list the species. | `not_drone` |
| Broadband_Jam | Wideband interference, described as denial-of-service or heavy jamming. The card gives no bandwidth or power cutoff. | `other`: an alert, not a drone |
| Narrowband_Jam | Localized, single-frequency interference. The card gives no frequency. | `other`: an alert, not a drone |

`uncertain` is in the same map and is not one of the six dataset classes. A `drone_like` or `not_drone` label is read as `uncertain` when its score is below the RF score floor. That floor is the placeholder 0.60 in `DEFAULT_SCORE_FLOOR`. A jam label stays `other`.

A Machine prediction is the drone-like cue. Confirmation still depends on acoustic, radar, or thermal evidence and on operator review.

## Decision: v5 as a first-stage screen

The validation Machine-recall target is **0.90**, set before any new test scoring. RF is the first stage of the cascade. A Machine call is confirmed by acoustic, radar, or thermal evidence and by operator review. A Machine event called Benign is not checked again. Macro F1 treats those two errors as equal, so it is the wrong objective for a screen.

v5 can trade the two errors with the Machine loss weight and a calibrated threshold. v4 has one fixed operating point. v5 scores are temperature-calibrated on validation, which the agent needs. The earlier stand-alone rule compared a three-seed validation mean with v4's single test macro F1, 0.8865. The highest v5 mean was 0.8831, short by 0.0034, so that rule kept v4. v4 stays the best stand-alone classifier.

The screen rule, applied on validation only:

1. Candidates are v5 at Machine loss weights 1.00–1.50, using the seed-42 checkpoints. Seeds 43 and 44 are reported for stability only.
2. For each candidate, fit temperature scaling on validation, then sweep the Machine threshold from 0.10 to 0.90 in steps of 0.05 on the calibrated validation probabilities.
3. Keep the weight and threshold pairs with validation Machine recall of at least 0.90.
4. Among those, choose the fewest Benign→Machine errors on validation. Ties go to higher macro F1, then the lower weight.
5. If no pair reaches the target, choose the highest validation Machine recall and report that the target was not met.
6. Score the test set once with the chosen pair. Report Machine recall, Benign→Machine and Machine→Benign counts, the confusion matrix, macro F1, and expected calibration error before and after calibration.

That test scoring has not been run yet. The comparison below is the earlier exploratory sweep.

## Held-out test comparison

The notebook rebuilds the AAI-540 assignment split from the predecessor's committed metadata: 9,600 training images, 2,400 validation images, 2,400 held-out test images, and 9,600 production images. The v4 test confusion matrix is embedded in the notebook. The v5 values below are notebook-run results; no retraining was performed for this documentation.

| Version | Machine loss weight | Test accuracy | Macro F1 | Machine recall | Machine precision | Machine false negatives predicted Benign |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v4 | 1.00 | 0.8875 | 0.8865 | 0.6450 | 0.7500 | 118 |
| v5 (unweighted run) | 1.00 | 0.8904 | 0.8889 | 0.6325 | 0.7737 | 128 |
| v5.1 | 1.25 | 0.8850 | 0.8846 | 0.6625 | 0.7162 | 110 |
| v5.2 | 1.30 | 0.8904 | 0.8889 | 0.6400 | 0.7688 | 119 |
| v5.3 | 1.35 | 0.8888 | 0.8888 | 0.6925 | 0.7103 | 98 |
| v5.4 | 1.40 | 0.8875 | 0.8871 | 0.6800 | 0.7391 | 99 |
| v5.5 | 1.45 | 0.8788 | 0.8804 | 0.7450 | 0.6667 | 87 |
| v5.6 | 1.50 | 0.8871 | 0.8879 | 0.7425 | 0.6843 | 80 |

The loss-weight sweep exposes a trade-off. Higher Machine recall reduces Machine-to-Benign errors but can lower Benign recall, accuracy, or macro F1. Section 6 scored the test set before the screen rule was written. That table does not choose the screen.

## Reproducibility and handoff status

The notebook is committed, but its saved model, metrics JSON, sweep CSV, and per-image test predictions were written to a temporary Colab artifact directory and are not committed in this repository. Therefore no RF output CSV has been added to `data/model-outputs/` and RF data must not replace a simulated replay placeholder yet.

To complete the handoff without retraining, obtain Mostafa's existing downloaded artifact or saved per-image test predictions. Export one row per held-out test image using the shared schema in `data/model-output-handoff-template.csv`, including the exact model version, predicted class, raw score, dataset ID, and stable source reference. The replay must remain explicitly simulated and require human review.
