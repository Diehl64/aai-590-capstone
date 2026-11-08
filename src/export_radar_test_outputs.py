"""Export held-out RadarCNN outputs for simulated replay without retraining."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from model_output_handoff import write_handoff
from radar_neural_network import CLASSES, RadarCNN, load_data, score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("results/radar-neural-network/radar-cnn.pt"),
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        default=Path("results/radar-neural-network/radar-neural-network-metrics.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/model-outputs/radar-cnn-test-outputs.csv"),
    )
    parser.add_argument("--seed", type=int, default=590)
    parser.add_argument("--batch-size", type=int, default=512)
    args = parser.parse_args()

    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    x, y, observation_ids, observation_times, _ = load_data(args.data, args.seed)

    model = RadarCNN().to(device)
    state = torch.load(args.model, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()

    score_batches = []
    with torch.inference_mode():
        for start in range(0, len(x["test"]), args.batch_size):
            batch = torch.from_numpy(
                x["test"][start:start + args.batch_size, None]
            ).to(device)
            score_batches.append(torch.softmax(model(batch), dim=1).cpu().numpy())

    test_scores = np.concatenate(score_batches)
    predictions = test_scores.argmax(axis=1)
    observed = score(y["test"], predictions)

    expected = metrics["test"]
    if observed["n_segments"] != expected["n_segments"]:
        raise RuntimeError("Held-out test count does not match saved metrics.")
    if observed["confusion_matrix"] != expected["confusion_matrix"]:
        raise RuntimeError(
            "Saved checkpoint predictions do not match the recorded confusion matrix."
        )

    selected_epoch = metrics["selected_epoch"]
    model_version = f"RadarCNN-seed-{args.seed}-epoch-{selected_epoch}"

    rows = []
    for index, predicted_index in enumerate(predictions):
        rows.append(
            {
                "output_id": f"radar-test-{index:06d}",
                "sensor_type": "radar",
                "source_observation_id": observation_ids["test"][index],
                "split": "test",
                "timestamp": f"relative_seconds:{observation_times['test'][index]:.9g}",
                "predicted_label": CLASSES[predicted_index],
                "score": float(test_scores[index, predicted_index]),
                "model_version": model_version,
                "dataset_id": "kth_77ghz_v2",
                "source_output_ref": "data/model-outputs/radar-cnn-test-outputs.csv",
            }
        )

    write_handoff(args.output, rows)

    print(
        json.dumps(
            {
                "device": str(device),
                "output": str(args.output),
                "held_out_rows": len(rows),
                "accuracy": observed["accuracy"],
                "macro_f1": observed["macro_f1"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()