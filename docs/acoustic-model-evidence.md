# Acoustic model evidence

Acoustic drone-sound detection was added to the capstone scope on 2026-11-01. It is evaluated independently from RF, radar, and thermal/vision models. The datasets are not synchronized; later local-replay records are simulated and do not establish real-world sensor-fusion performance.

## Team-reported results awaiting repository artifacts

Mostafa reported two transformer experiments in the Group 1 Slack channel:

| Dataset | Reported setup | Reported held-out result | Important limitation |
| --- | --- | --- | --- |
| Kaggle Drone Sound Audio Detection | 11,704 clips; whole recordings kept in one split; one-second log-mel windows | 0.991 accuracy, 0.964 drone F1, 0.998 ROC-AUC; 187 of 190 drones detected with 11 false alarms | Validation drone F1 was 0.835 on different held-out recordings. |
| DADS drone-audio samples | 180,320 mono 16 kHz clips; whole files kept in one split; 128 × 98 log-mel windows; small spectrogram transformer | 0.999 accuracy, 0.999 drone F1, 1.000 ROC-AUC; 0.8% realized false-alarm rate at a validation-selected operating point | The reported data lacks a source/site label, so the result does not measure new-site generalization. |

These are team-reported values, not yet independently reproducible from this repository. Before inclusion in the final report or local replay, commit the code, environment/dependency specification, dataset-license record, split manifest, saved metrics, and model-output file. Record any augmentation or controlled-noise robustness check separately from the clean held-out evaluation.
