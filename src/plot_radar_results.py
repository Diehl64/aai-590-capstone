"""Create report figures from saved RadarCNN test metrics without retraining."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

repo = Path(__file__).resolve().parents[1]
metrics_path = repo / "results" / "radar-neural-network" / "radar-neural-network-metrics.json"
metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
test = metrics["test"]
classes = test["classes"]
matrix = np.array(test["confusion_matrix"])
output_dir = metrics_path.parent

fig, ax = plt.subplots(figsize=(7, 6))
image = ax.imshow(matrix, cmap="Blues")
fig.colorbar(image, ax=ax, label="Segments")
ax.set(
    xticks=range(len(classes)),
    yticks=range(len(classes)),
    xticklabels=classes,
    yticklabels=classes,
    xlabel="Predicted class",
    ylabel="Actual class",
    title="RadarCNN held-out test confusion matrix",
)

for row in range(len(classes)):
    for column in range(len(classes)):
        color = "white" if matrix[row, column] > matrix.max() / 2 else "black"
        ax.text(column, row, matrix[row, column],
                ha="center", va="center", color=color)

fig.tight_layout()
fig.savefig(output_dir / "radar-cnn-test-confusion-matrix.png", dpi=200)
plt.close(fig)

measures = ("precision", "recall", "f1")
values = np.array([
    [test["per_class"][label][measure] for measure in measures]
    for label in classes
])
positions = np.arange(len(classes))
width = 0.24

fig, ax = plt.subplots(figsize=(8, 5))
for index, measure in enumerate(measures):
    ax.bar(
        positions + (index - 1) * width,
        values[:, index],
        width,
        label=measure.title(),
    )

ax.set(
    xticks=positions,
    xticklabels=classes,
    ylim=(0, 1),
    ylabel="Score",
    title="RadarCNN held-out test metrics by class",
)
ax.legend()
fig.tight_layout()
fig.savefig(output_dir / "radar-cnn-per-class-metrics.png", dpi=200)
plt.close(fig)