#!/usr/bin/env python3
"""Leakage-aware radar split and a dependency-light baseline classifier.

The official object-array download is intentionally kept outside the repository.
Run with RADAR_DATA_PATH pointing to the checksum-verified file.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

LABEL_MAP = {
    "D1": "drone", "D2": "drone", "D3": "drone", "D4": "drone",
    "D5": "drone", "D6": "drone", "black-headed gull": "bird",
    "heron": "bird", "pigeon": "bird", "raven": "bird", "seagull": "bird",
    "seagull and black-headed gull": "bird", "human_run": "human",
    "human_walk": "human",
}


def coarse_label(label: str) -> str:
    if label == "CR":
        return "reflector"
    try:
        return LABEL_MAP[label]
    except KeyError as exc:
        raise ValueError(f"Unmapped source label: {label!r}") from exc


def load_measurements(path: Path) -> list[dict]:
    data = np.load(path, allow_pickle=True)
    if data.shape != (130, 6):
        raise ValueError(f"expected (130, 6), got {data.shape}")
    measurements = []
    for measurement_id, row in enumerate(data):
        label = str(np.asarray(row[0]).squeeze())
        signal = np.asarray(row[1])
        if signal.ndim != 2 or signal.shape[0] != 1280 or not np.iscomplexobj(signal):
            raise ValueError(f"measurement {measurement_id}: unexpected signal shape/type")
        measurements.append({"measurement_id": measurement_id, "source_label": label,
                             "class": coarse_label(label), "segments": signal.shape[1],
                             "signal": signal})
    return measurements


def grouped_split(measurements: list[dict], seed: int = 590) -> dict[int, str]:
    """Assign whole measurements to train/validation/test, stratified by class.

    The greedy objective targets 70/15/15 percent of segments per class. A
    measurement is never divided between partitions. Reflectors are excluded.
    """
    rng = np.random.default_rng(seed)
    usable = [m for m in measurements if m["class"] != "reflector"]
    assignments: dict[int, str] = {}
    targets = {"train": .70, "validation": .15, "test": .15}
    for cls in ("drone", "bird", "human"):
        group = [m for m in usable if m["class"] == cls]
        order = list(rng.permutation(len(group)))
        totals = sum(m["segments"] for m in group)
        counts = {k: 0 for k in targets}
        # Largest measurements first makes the target proportions less dependent
        # on the arbitrary source ordering.
        for i in sorted(order, key=lambda j: group[j]["segments"], reverse=True):
            split = min(targets, key=lambda k: counts[k] / max(targets[k] * totals, 1))
            assignments[group[i]["measurement_id"]] = split
            counts[split] += group[i]["segments"]
    return assignments


def features(signal: np.ndarray) -> np.ndarray:
    mag = np.abs(signal).astype(np.float32)
    # Compact, deterministic statistics over each segment; no test-set fitting.
    return np.column_stack((mag.mean(0), mag.std(0), mag.max(0),
                            np.quantile(mag, .25, axis=0),
                            np.quantile(mag, .75, axis=0)))


def evaluate(y_true: np.ndarray, y_pred: np.ndarray, classes: list[str]) -> dict:
    matrix = np.zeros((len(classes), len(classes)), dtype=int)
    index = {c: i for i, c in enumerate(classes)}
    for actual, predicted in zip(y_true, y_pred):
        matrix[index[actual], index[predicted]] += 1
    precision, recall, f1 = [], [], []
    for i in range(len(classes)):
        tp = matrix[i, i]
        precision.append(tp / max(matrix[:, i].sum(), 1))
        recall.append(tp / max(matrix[i].sum(), 1))
        f1.append(2 * precision[-1] * recall[-1] / max(precision[-1] + recall[-1], 1e-12))
    return {"accuracy": float(np.trace(matrix) / max(matrix.sum(), 1)),
            "macro_f1": float(np.mean(f1)),
            "per_class": {c: {"precision": precision[i], "recall": recall[i], "f1": f1[i]}
                          for i, c in enumerate(classes)},
            "confusion_matrix": matrix.tolist(), "classes": classes}


def run(data_path: Path, output: Path, seed: int) -> dict:
    measurements = load_measurements(data_path)
    assignment = grouped_split(measurements, seed)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "radar-split-manifest.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["measurement_id", "source_label", "class", "segments", "split"])
        writer.writeheader()
        for m in measurements:
            writer.writerow({k: m[k] for k in ("measurement_id", "source_label", "class", "segments")} |
                            {"split": assignment.get(m["measurement_id"], "excluded_reflector")})
    classes = ["drone", "bird", "human"]
    train = [(features(m["signal"]), m["class"]) for m in measurements
             if assignment.get(m["measurement_id"]) == "train"]
    centroids = {c: np.average(np.vstack([x for x, y in train if y == c]), axis=0) for c in classes}
    metrics = {}
    for split in ("validation", "test"):
        rows = [(features(m["signal"]), m["class"]) for m in measurements
                if assignment.get(m["measurement_id"]) == split]
        x = np.vstack([a for a, _ in rows])
        # Each measurement contributes one source label to every segment.
        y = np.concatenate([np.repeat(b, a.shape[0]) for a, b in rows])
        pred = np.array([min(classes, key=lambda c: np.linalg.norm(v - centroids[c])) for v in x])
        metrics[split] = evaluate(y, pred, classes)
    result = {"seed": seed, "data": str(data_path), "classifier": "nearest_centroid",
              "features": ["mean_magnitude", "std_magnitude", "max_magnitude", "q25_magnitude", "q75_magnitude"],
              "reflector_policy": "excluded_from_drone_bird_human_training_and_metrics",
              "metrics": metrics}
    (output / "radar-baseline-metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/radar-baseline"))
    parser.add_argument("--seed", type=int, default=590)
    args = parser.parse_args()
    print(json.dumps(run(args.data, args.output, args.seed), indent=2))


if __name__ == "__main__":
    main()
