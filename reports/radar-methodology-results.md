# Radar methodology and results draft

The project uses the checksum-verified KTH 77 GHz FMCW radar dataset (130 measurements and 75,868 segments; CC BY 4.0). D1–D6 map to `drone`, bird labels map to `bird`, and human_run/human_walk map to `human`. The 19 corner-reflector measurements are explicitly excluded. Complete measurement IDs define the split: 50,491 train, 11,047 validation, and 11,050 test segments. Preprocessing is fitted on training data only.

The nearest-centroid baseline uses five magnitude statistics per segment. The RadarCNN is trained from scratch on normalized magnitude reshaped to five range cells by 256 azimuth samples. It uses PyTorch 2.11.0+cu128 on an NVIDIA RTX 5080 and selects its checkpoint by validation macro F1.

| Model | Test accuracy | Test macro F1 |
| --- | ---: | ---: |
| Nearest centroid | 0.5807 | 0.4882 |
| RadarCNN, selected epoch 7 | **0.9439** | **0.8910** |

The CNN test confusion matrix, in drone/bird/human order, is `[[8556, 173, 153], [98, 1075, 3], [193, 0, 799]]`. Per-class precision/recall/F1 are drone 0.9671/0.9633/0.9652, bird 0.8614/0.9141/0.8870, and human 0.8366/0.8054/0.8207.

The source metadata does not prove that different measurement IDs are independent sessions, subjects, or targets. These results therefore do not establish unseen-session generalization, continuous detection rates, calibrated probabilities, geographic tracking, or field readiness. Replay scenarios are simulated and reported separately; RGB/thermal verification and Lattice integration were not evaluated.
