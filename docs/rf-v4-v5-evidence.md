# RF CNN v4 versus v5 evidence

This record summarizes saved outputs embedded in Mostafa's committed RF evaluation notebook at `origin/mostafa` commit `fe57243`. The RF model evaluates six RF-spectrogram classes: Benign, Broadband_Jam, Human, Machine, Narrowband_Jam, and Wildlife. It is evaluated independently from radar, thermal/IR, and acoustic work.

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

The loss-weight sweep exposes a trade-off. Higher Machine recall reduces Machine-to-Benign errors but can lower Benign recall, accuracy, or macro F1. The team must select a version based on the intended false-positive/false-negative trade-off; this document does not declare a winner.

## Reproducibility and handoff status

The notebook is committed, but its saved model, metrics JSON, sweep CSV, and per-image test predictions were written to a temporary Colab artifact directory and are not committed in this repository. Therefore no RF output CSV has been added to `data/model-outputs/` and RF data must not replace a simulated replay placeholder yet.

To complete the handoff without retraining, obtain Mostafa's existing downloaded artifact or saved per-image test predictions. Export one row per held-out test image using the shared schema in `data/model-output-handoff-template.csv`, including the exact model version, predicted class, raw score, dataset ID, and stable source reference. The replay must remain explicitly simulated and require human review.
