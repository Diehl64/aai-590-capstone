# RF CNN v4 versus v5 evidence

RF classifies 128×128 spectrograms into Benign, Broadband_Jam, Human, Machine, Narrowband_Jam, and Wildlife. This note records the first-stage screen on branch `rf-pipeline`: v5 is the screen, and v4 stays the stand-alone reference. Radar, thermal, and acoustic results are separate. Every number below is in a committed file listed at the end. Rates in the tables are rounded to four decimal places; the JSON and CSV files hold the unrounded values.

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

## Decision

The validation Machine-recall target is **0.90**, set before the screen run. RF is the first stage of the cascade. A Machine call is confirmed by acoustic, radar, or thermal evidence and by operator review. A Machine event called Benign is not checked again. Macro F1 treats those two errors as equal, so it is the wrong objective for a screen.

v5 can trade the two errors with the Machine loss weight and a calibrated threshold. v4 has one fixed operating point. v5 scores are temperature-calibrated on validation, which the agent needs.

v4 remains the stand-alone reference. Its recorded test result, saved in the notebook, is accuracy 0.8875, macro F1 0.8865, and Machine recall 0.6450 (258 of 400). Of the 142 Machine misses, 118 are called Benign. v4 also calls 59 true Benign images Machine.

An earlier stand-alone rule, written up in section 12 of the notebook, kept v4. That write-up compares one v4 test macro F1, 0.8865, with a three-seed validation mean, and records the highest of those means as 0.8831 at weight 1.25, short by 0.0034. The screen rule replaced that comparison before the test score in this note. The three-seed table later in this note is from the screen run and is a stability check, not that earlier comparison.

## Screen rule and the chosen pair

Applied on validation only, seed 42. Seeds 43 and 44 are trained for stability and are not candidates. The rule text is in [`results/rf-intrusion/run_config.json`](../results/rf-intrusion/run_config.json) and in [`results/rf-intrusion/validation_selection/selection_record.json`](../results/rf-intrusion/validation_selection/selection_record.json).

1. Candidates are v5 at Machine loss weights 1.00, 1.25, 1.30, 1.35, 1.40, 1.45, and 1.50, using the seed-42 checkpoints.
2. For each candidate, fit temperature scaling on validation, then sweep the Machine threshold from 0.10 to 0.90 in steps of 0.05 on the calibrated validation probabilities.
3. Keep the weight and threshold pairs with validation Machine recall of at least 0.90.
4. Among those, choose the fewest Benign→Machine errors on validation. Ties go to higher macro F1, then the lower weight.
5. If no pair reaches the target, choose the highest validation Machine recall and report that the target was not met.
6. Score the test set once with the chosen pair.

The target was met. The chosen pair is weight **1.50**, Machine threshold **0.45**, temperature **1.2932965073088454**, seed **42**, `checkpoint_role` `selected`. On validation that pair has Machine recall 0.9025, 262 Benign→Machine, 13 Machine→Benign, and macro F1 0.8382840806086049. Validation negative log-likelihood moves from 0.24542851746082306 to 0.23933258652687073. Fifty pairs reached the recall target. The next fewest Benign→Machine count is 264, at weight 1.00 and threshold 0.35. The full sweep is [`results/rf-intrusion/validation_selection/validation_screen.csv`](../results/rf-intrusion/validation_selection/validation_screen.csv).

## Validation trade-off at the chosen weight

Seed 42, weight 1.50, calibrated probabilities. The chosen threshold is the only row marked chosen. Threshold 0.50 drops validation Machine recall to 0.7750, so it does not qualify. The figure is [`results/rf-intrusion/rf_v5_validation_tradeoff.png`](../results/rf-intrusion/rf_v5_validation_tradeoff.png), and the table is [`results/rf-intrusion/rf_v5_validation_tradeoff.csv`](../results/rf-intrusion/rf_v5_validation_tradeoff.csv).

| Threshold | Machine recall | Benign→Machine | Machine→Benign | Macro F1 | Accuracy | Chosen |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.10 | 0.9775 | 296 | 0 | 0.8125 | 0.8250 | |
| 0.15 | 0.9700 | 296 | 0 | 0.8167 | 0.8304 | |
| 0.20 | 0.9625 | 296 | 0 | 0.8182 | 0.8325 | |
| 0.25 | 0.9575 | 296 | 0 | 0.8198 | 0.8346 | |
| 0.30 | 0.9475 | 296 | 0 | 0.8207 | 0.8358 | |
| 0.35 | 0.9425 | 295 | 0 | 0.8222 | 0.8375 | |
| 0.40 | 0.9325 | 292 | 2 | 0.8242 | 0.8392 | |
| 0.45 | 0.9025 | 262 | 13 | 0.8383 | 0.8475 | yes |
| 0.50 | 0.7750 | 157 | 61 | 0.8713 | 0.8713 | |
| 0.55 | 0.6425 | 56 | 114 | 0.8916 | 0.8929 | |
| 0.60 | 0.5750 | 25 | 139 | 0.8921 | 0.8958 | |
| 0.65 | 0.5525 | 19 | 147 | 0.8908 | 0.8954 | |
| 0.70 | 0.5350 | 14 | 150 | 0.8895 | 0.8950 | |
| 0.75 | 0.5050 | 7 | 158 | 0.8868 | 0.8938 | |
| 0.80 | 0.4700 | 2 | 168 | 0.8841 | 0.8929 | |
| 0.85 | 0.4025 | 0 | 178 | 0.8704 | 0.8833 | |
| 0.90 | 0.3275 | 0 | 194 | 0.8528 | 0.8713 | |

## Seed stability

Three seeds, 42, 43, and 44. These rows are **argmax** validation scores. They are not the calibrated threshold used by the screen. The standard deviation is the sample standard deviation. At weight 1.50 the mean Machine recall is 0.7908 and the mean Benign recall is 0.5883. The file is [`results/rf-intrusion/rf_v5_seed_summary.csv`](../results/rf-intrusion/rf_v5_seed_summary.csv). Per-seed rows are in [`results/rf-intrusion/validation_selection/validation_runs.csv`](../results/rf-intrusion/validation_selection/validation_runs.csv).

| Weight | Machine recall mean (std) | Benign recall mean (std) | Macro F1 mean (std) |
| ---: | --- | --- | --- |
| 1.00 | 0.6000 (0.0200) | 0.8858 (0.0210) | 0.8880 (0.0069) |
| 1.25 | 0.6783 (0.0151) | 0.7492 (0.0309) | 0.8799 (0.0030) |
| 1.30 | 0.6217 (0.0177) | 0.8742 (0.0363) | 0.8896 (0.0014) |
| 1.35 | 0.7425 (0.0517) | 0.6758 (0.0825) | 0.8755 (0.0078) |
| 1.40 | 0.7425 (0.0506) | 0.7108 (0.0641) | 0.8835 (0.0049) |
| 1.45 | 0.7592 (0.0729) | 0.6592 (0.1580) | 0.8758 (0.0149) |
| 1.50 | 0.7908 (0.0350) | 0.5883 (0.0813) | 0.8689 (0.0091) |

## Selected test score

Scored once, after the validation choice, at weight 1.50, threshold 0.45, and seed 42. The 2,400 rows are [`data/model-outputs/rf-cnn-test-outputs.csv`](../data/model-outputs/rf-cnn-test-outputs.csv). The same rows are [`results/rf-intrusion/rf-test-outputs.csv`](../results/rf-intrusion/rf-test-outputs.csv). Model version `rf-intrusion-cnn-v5-w1.50-seed42-selected`. The handoff temperature column is 1.293297; `run_config.json` stores 1.2932965073088454.

From [`results/rf-intrusion/rf_v5_test_metrics.json`](../results/rf-intrusion/rf_v5_test_metrics.json): accuracy 0.85125, macro F1 0.8442349992515298, Machine recall 0.9050 (362 of 400), Machine precision 0.558641975308642 (362 of 648), Benign→Machine 249, Machine→Benign 16. Benign recall on this operating point is 0.3775 (151 of 400).

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Benign | 0.8935 | 0.3775 | 0.5308 | 400 |
| Broadband_Jam | 0.9975 | 0.9950 | 0.9962 | 400 |
| Human | 0.9553 | 0.9625 | 0.9589 | 400 |
| Machine | 0.5586 | 0.9050 | 0.6908 | 400 |
| Narrowband_Jam | 0.9975 | 0.9975 | 0.9975 | 400 |
| Wildlife | 0.9134 | 0.8700 | 0.8912 | 400 |

Confusion matrix, rows true and columns predicted, in the class order above. The figure is [`results/rf-intrusion/rf_v5_test_confusion_matrix.png`](../results/rf-intrusion/rf_v5_test_confusion_matrix.png). The notebook also saved [`results/rf-intrusion/rf_intrusion_cnn_v5_selected_confusion_matrix.png`](../results/rf-intrusion/rf_intrusion_cnn_v5_selected_confusion_matrix.png) from the same test score.

| True \ predicted | Benign | Broadband_Jam | Human | Machine | Narrowband_Jam | Wildlife |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Benign | 151 | 0 | 0 | 249 | 0 | 0 |
| Broadband_Jam | 1 | 398 | 0 | 0 | 1 | 0 |
| Human | 0 | 0 | 385 | 3 | 0 | 12 |
| Machine | 16 | 0 | 1 | 362 | 0 | 21 |
| Narrowband_Jam | 0 | 1 | 0 | 0 | 399 | 0 |
| Wildlife | 1 | 0 | 17 | 34 | 0 | 348 |

Two expected calibration errors are recorded, both with 15 equal-width bins. They use different scores, so they are not interchangeable.

- Section 7, on the full softmax, in [`results/rf-intrusion/validation_selection/calibration_record.json`](../results/rf-intrusion/validation_selection/calibration_record.json): 0.02616624760131039 before calibration and 0.016203877901037517 after. Argmax labels are unchanged. The same pair is in `selection_record.json`.
- Handoff columns, in `rf_v5_test_metrics.json`: confidence before calibration is `score`, the raw softmax probability of the thresholded predicted class, and confidence after calibration is `calibrated_score`, the temperature-scaled probability of that same class. A row is correct when the predicted label matches the metadata class. That ECE is 0.04273572069166662 before and 0.03339788058749988 after.

## Earlier test scores still in the notebook

Section 6 of [`notebooks/rf_machine_detection.ipynb`](../notebooks/rf_machine_detection.ipynb) scored the test set for weights 1.25 through 1.50 before this screen rule. That cell was not run in the Colab session that chose the pair, and those scores were not used to choose it. The saved section 6 table is below. Section 5's saved output also has an earlier weight-1.00 v5 test score: accuracy 0.8983, macro F1 0.8965, Machine recall 0.6375.

| Version | Weight | Accuracy | Macro F1 | Machine recall | Benign recall | Benign→Machine | Machine→Benign |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v4 | 1.00 | 0.8875 | 0.8865 | 0.6450 | 0.8525 | 59 | 118 |
| v5.1 | 1.25 | 0.8746 | 0.8747 | 0.7500 | 0.6525 | 138 | 63 |
| v5.2 | 1.30 | 0.8933 | 0.8929 | 0.6650 | 0.8625 | 55 | 115 |
| v5.3 | 1.35 | 0.8762 | 0.8775 | 0.7600 | 0.6900 | 123 | 77 |
| v5.4 | 1.40 | 0.8842 | 0.8848 | 0.7275 | 0.7700 | 92 | 88 |
| v5.5 | 1.45 | 0.8679 | 0.8672 | 0.8400 | 0.5675 | 167 | 47 |
| v5.6 | 1.50 | 0.8979 | 0.8972 | 0.6700 | 0.8625 | 55 | 110 |

Section 12 of the notebook still describes that earlier stand-alone run. Its closing paragraph names a diagnostic export at temperature 1.5158 and threshold 0.50. The held-out CSV in this repository is the screen export: weight 1.50, threshold 0.45, temperature 1.2932965073088454.

## Split integrity

Checked on 2026-11-18. The full lists are in [`results/rf-intrusion/rf_integrity_checks.json`](../results/rf-intrusion/rf_integrity_checks.json). The assignment is [`data/rf-split-manifest.csv`](../data/rf-split-manifest.csv): 9,600 train, 2,400 validation, 2,400 test, and 9,600 production. Each of the 24,000 filenames is in exactly one split. The notebook reads that file and uses the AAI-540 metadata URL only when the file is missing.

SHA-256 of the file bytes finds 23,764 distinct images. There are 219 groups of byte-identical copies, covering 455 images. 76 groups sit inside one split and 143 cross splits. 41 test images have an identical copy in train, validation, or production. 10 groups carry more than one class label.

The metadata has no recording or session id. This check sees exact copies only. Images from one recording that are not byte-identical can still sit in different splits.

Section 7 scored the test set once, for the chosen pair. Section 10 read the test images again only to write the held-out CSV for that same model.

## Limitations

- Machine is a drone-like cue. The Kaggle card does not define it as a confirmed drone, and it does not say which source produced a given image.
- The metadata has no recording or session id, so exact-copy checks do not prove that train, validation, and test are separate recordings.
- 41 test images have a byte-identical copy outside the test split, and 10 duplicate groups mix class labels.
- The notebook still shows earlier test scores from sections 5 and 6. Those scores were not used to choose the screen.
- The selected operating point spends Benign recall to reach the Machine-recall target: validation Benign→Machine is 262, and the test count is 249. Benign test recall is 0.3775.
- The `.keras` checkpoint and the seven seed-42 `.h5` weight files stay outside git. `results/rf-intrusion/rf-production-outputs.csv` is the 9,600-row production export and is not the handoff.
- Replay of this CSV is still simulated and still requires human review. The placeholder RF score floor remains 0.60.

## Files

- Notebook: [`notebooks/rf_machine_detection.ipynb`](../notebooks/rf_machine_detection.ipynb)
- Split: [`data/rf-split-manifest.csv`](../data/rf-split-manifest.csv)
- Held-out handoff: [`data/model-outputs/rf-cnn-test-outputs.csv`](../data/model-outputs/rf-cnn-test-outputs.csv) and [`results/rf-intrusion/rf-test-outputs.csv`](../results/rf-intrusion/rf-test-outputs.csv)
- Choice: [`results/rf-intrusion/run_config.json`](../results/rf-intrusion/run_config.json), [`results/rf-intrusion/validation_selection/selection_record.json`](../results/rf-intrusion/validation_selection/selection_record.json), [`results/rf-intrusion/validation_selection/calibration_record.json`](../results/rf-intrusion/validation_selection/calibration_record.json)
- Validation sweep and seeds: [`validation_screen.csv`](../results/rf-intrusion/validation_selection/validation_screen.csv), [`validation_runs.csv`](../results/rf-intrusion/validation_selection/validation_runs.csv), [`validation_summary.csv`](../results/rf-intrusion/validation_selection/validation_summary.csv). [`validation_benign_machine_thresholds.csv`](../results/rf-intrusion/validation_selection/validation_benign_machine_thresholds.csv) is the section 8 uncalibrated threshold table.
- Selected test metrics and figures: [`rf_v5_test_metrics.json`](../results/rf-intrusion/rf_v5_test_metrics.json), [`rf_v5_test_confusion_matrix.png`](../results/rf-intrusion/rf_v5_test_confusion_matrix.png), [`rf_intrusion_cnn_v5_selected_confusion_matrix.png`](../results/rf-intrusion/rf_intrusion_cnn_v5_selected_confusion_matrix.png)
- Trade-off and seed summary: [`rf_v5_validation_tradeoff.csv`](../results/rf-intrusion/rf_v5_validation_tradeoff.csv), [`rf_v5_validation_tradeoff.png`](../results/rf-intrusion/rf_v5_validation_tradeoff.png), [`rf_v5_seed_summary.csv`](../results/rf-intrusion/rf_v5_seed_summary.csv)
- Integrity: [`rf_integrity_checks.json`](../results/rf-intrusion/rf_integrity_checks.json)
