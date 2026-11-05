# Acoustic model evidence

Binary acoustic drone detection was added to the capstone scope on 2026-11-01 (plan row 6, Nov 9–13, owner Mostafa). It is evaluated independently from the RF, radar, and thermal/vision models. The datasets are not synchronized, so later local-replay records are simulated and do not establish real-world sensor-fusion performance.

## Selected dataset

The submitted introduction names the Hugging Face **Drone Audio Detection Samples** dataset as the acoustic source ([Z121mm/drone-audio-detection-samples](https://huggingface.co/datasets/Z121mm/drone-audio-detection-samples), `dads_drone_audio` in the manifest). It contains about 180,000 WAV clips with binary drone / no-drone labels. The introduction states that it is released under the MIT license. Record verification of that license in `data/dataset-manifest.csv` before final use.

The Kaggle Drone Sound Audio Detection set (`drone_sound_kaggle`) was an earlier experiment. It is kept as a secondary reference only and is not the capstone's primary acoustic dataset.

## Team-reported results awaiting repository artifacts

Mostafa reported the following transformer experiments in the Group 1 Slack channel:

| Dataset | Role | Reported setup | Reported held-out result | Important limitation |
| --- | --- | --- | --- | --- |
| DADS drone-audio samples (Hugging Face) | Primary | 180,320 mono 16 kHz clips; whole files kept in one split; 128 × 98 log-mel windows; small spectrogram transformer | 0.999 accuracy, 0.999 drone F1, 1.000 ROC-AUC; 0.8% realized false-alarm rate at a validation-selected operating point | The data lacks a source/site label, so the result does not measure new-site generalization. |
| Kaggle Drone Sound Audio Detection | Secondary reference | 11,704 clips; whole recordings kept in one split; one-second log-mel windows | 0.991 accuracy, 0.964 drone F1, 0.998 ROC-AUC; 187 of 190 drones detected with 11 false alarms | Validation drone F1 was 0.835 on different held-out recordings. |

These are team-reported values and are not yet reproducible from this repository.

## Noise-robustness evaluation (plan row 6)

Controlled environmental noise is added only to test-time copies of held-out clips. Source audio and the clean test set stay unchanged. Report the following separately from the clean held-out results:

- the noise sources and their licenses;
- the signal-to-noise ratio levels tested;
- drone recall, false-alarm rate, and F1 at each level; and
- the operating threshold, which is fixed from clean validation data.

## Required before report or replay use

Commit the following to the repository:

- code and environment/dependency specification;
- dataset-license record;
- split manifest;
- saved metrics;
- noise-robustness results; and
- a validated held-out output CSV following the [model-output handoff](model-output-handoff.md).

Calibration evidence is needed only if acoustic scores will be described as calibrated. The output must state the source/site-generalization limitation above.
