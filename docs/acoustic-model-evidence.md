# Acoustic model evidence

Acoustic drone-sound detection is evaluated on its own. The DADS recordings are not synchronized with the RF, radar, or thermal sets, so a later replay that pairs their rows is simulated and is not a measured fusion result.

The selected model is CNN-Tuned, run C of the small spectrogram CNN. It was trained on rewindowed one-second log-mel windows. Run C keeps the trial chosen on validation only, then applies temperature scaling fit on clean validation. The exported model version is `cnn-tuned-epoch-5-temperature-1.000`. Temperature is 1.000, so the scaled score matches the raw score. In [`results/acoustic/acoustic-test-outputs.csv`](../results/acoustic/acoustic-test-outputs.csv) the `score` and `calibrated_score` columns are the probability of the predicted class.

## Clean operating point

The drone decision uses threshold **0.344**, the 1% false-alarm point chosen on clean validation and applied once to the rewindowed test windows. The handoff export recomputed that same rule as 0.343736. The test set has 57,015 windows (28,681 drone, 28,334 no drone).

| Windows | Recall | False-alarm rate | F1 | ROC-AUC |
| --- | ---: | ---: | ---: | ---: |
| All 57,015 | 0.996 | 0.012 | 0.992 | 0.999 |
| Full-length drone windows | 0.977 | 0.012 | 0.951 | 0.997 |

Clean recall over files, rather than windows, has a 95% interval of 0.994 to 0.998. Full-length windows are the clips that already filled the one-second window. Originally short windows are reported with the padding check below.

## Noise, kept separate from the clean result

Noise is an ESC-50 outdoor and mechanical mix (rain, sea waves, wind, thunderstorm, engine, train, helicopter, airplane, crackling fire, chainsaw), added only at test time. The clean-validation threshold stays fixed. Helicopter, airplane, and engine can sound like a drone, so a higher false-alarm rate at low SNR can be the added clip. License and citation are in [`results/acoustic/noise_robustness.json`](../results/acoustic/noise_robustness.json).

**Full-length recall is the noise headline.** A short window padded with digital zeros gives the model a silent tail, so overall recall mixes that cue with the sound.

For CNN-Tuned, fold-5 noise on the rewindowed test windows, still at 0.344:

| SNR | Full-length recall | False-alarm rate on all no-drone windows |
| --- | ---: | ---: |
| 20 dB | 0.971 | 0.014 |
| 10 dB | 0.949 | 0.020 |
| 5 dB | 0.901 | 0.028 |
| 0 dB | 0.775 | 0.047 |
| −5 dB | 0.518 | 0.071 |

The 95% file interval for full-length recall at 20 dB is 0.951 to 0.983. Overall recall stays higher than full-length recall because the originally short windows remain easy after the tail is filled with quiet background.

The earlier check on the three saved models, trained on zero-padded windows, is the committed noise table. At 20 dB their full-length recall is 0.991 (transformer), 0.936 (CNN), and 0.912 (forest), while recall on the padded drone windows falls to 0.186, 0.357, and 0.012. That gap is why the headline is the full-length number. Tables and figures:

- [`results/acoustic/noise_robustness.csv`](../results/acoustic/noise_robustness.csv)
- [`results/acoustic/noise_robustness_by_padding.csv`](../results/acoustic/noise_robustness_by_padding.csv)
- [`results/acoustic/recall_vs_snr.png`](../results/acoustic/recall_vs_snr.png)
- [`results/acoustic/recall_vs_snr_by_padding.png`](../results/acoustic/recall_vs_snr_by_padding.png)

## Padding and the partial-window caveat

On the original test split, 24,341 of 28,681 drone windows are zero-padded (84.9%) and 47 of 28,334 no-drone windows are zero-padded (0.2%). A classifier that sees only the padded flag has test ROC-AUC 0.924. Counts, the flag scores, and the figure:

- [`results/acoustic/padding_counts.csv`](../results/acoustic/padding_counts.csv)
- [`results/acoustic/padding_baseline.json`](../results/acoustic/padding_baseline.json)
- [`results/acoustic/padding_roc.png`](../results/acoustic/padding_roc.png)

The three saved models were not retrained on that check. Their clean scores are partly the zero tail, so a short clip is not evidence that the model heard a drone for the whole second. CNN-Tuned is the later model: short tails were rewindowed with low-level background before training, and the metrics above are on those rewindowed windows. Full-length recall remains the number to quote when the claim is about the sound rather than the tail.

## Source and site

DADS has no source or site label, so these acoustic scores do not measure generalization to a new site. That limit is required for the acoustic handoff in [`docs/model-output-handoff.md`](model-output-handoff.md).
