"""Phase 2 neural-network boundary.

The data loader and grouped manifest in ``radar_baseline.py`` are the stable
inputs for a train-from-scratch neural network. This module deliberately does
not claim a trained model until its architecture, training seed, and held-out
results are reviewed and recorded.
"""

MODEL_CONTRACT = {
    "input": "five-range-cell x 256-azimuth segment, represented by documented preprocessing",
    "classes": ["drone", "bird", "human"],
    "training": "from scratch; preprocessing fitted on train measurements only",
    "evaluation": "measurement-disjoint validation and untouched test; accuracy, macro F1, per-class metrics, confusion matrix",
    "framework": "to be selected and pinned after baseline review",
}
