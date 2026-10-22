# Radar model results

The models use the proposed `drone`, `bird`, and `human` mapping. The 19 corner-reflector measurements are excluded from training and metrics. Measurements, rather than individual segments, define the split: 50,491 train segments, 11,047 validation segments, and 11,050 test segments. The test partition was used once after model selection.

| Model | Test accuracy | Test macro F1 | Test segments |
| --- | ---: | ---: | ---: |
| Nearest-centroid magnitude-statistics baseline | 0.5807 | 0.4882 | 11,050 |
| RadarCNN, selected epoch 7 | **0.9439** | **0.8910** | 11,050 |

The baseline uses five magnitude statistics per segment and class centroids fitted from training measurements. The CNN uses normalized magnitude reshaped to five range cells by 256 azimuth samples, is trained from scratch for eight epochs, and selects its checkpoint by validation macro F1. The recorded run used PyTorch 2.11.0 with CUDA 12.8 on an NVIDIA RTX 5080. Results are stored in `results/radar-baseline/` and `results/radar-neural-network/`.

For the CNN test partition, drone precision/recall/F1 are 0.9671/0.9633/0.9652, bird 0.8614/0.9141/0.8870, and human 0.8366/0.8054/0.8207. The test confusion matrix is `[[8556, 173, 153], [98, 1075, 3], [193, 0, 799]]` in the class order drone, bird, human.

The CNN improvement is measured on this checksum-verified, target-centered dataset and this grouped split. The source does not establish that different measurement IDs are independent sessions, subjects, or targets; repeated recording context may remain across partitions. Therefore these results do not establish unseen-session generalization, continuous perimeter detection, false alerts per operating hour, calibrated probabilities, geographic tracking, or field deployment readiness. No RGB/thermal verification or Lattice integration was evaluated.
