"""Create curated held-out Thermal-IR decision panels from saved evaluations.

Categories always come from saved ``test_image_decisions.csv`` at its recorded
threshold. If an evaluation lacks saved boxes, inference is replayed only for
the selected panel images; it never recalculates metrics or decisions.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALUATION_ROOT = REPOSITORY_ROOT / "results" / "thermal-ir" / "evaluation" / "experiment_a_dataset2_only_batch32"
PANEL_SPECS = (
    ("true_positive", "True-positive drones", "Drone present and correctly reported", 4),
    ("false_negative", "Missed drones", "Drone present but not reported at the recorded threshold", 4),
    ("true_negative", "Correct negative decisions", "No-drone frame correctly reported as no drone", 4),
    ("false_positive", "False positives", "No-drone frame incorrectly reported as a drone", 5),
)


def parse_box(value: str | None) -> list[float] | None:
    if not value:
        return None
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return None
    return [float(item) for item in parsed] if parsed else None


def yolo_ground_truth(label_path: Path, width: int, height: int) -> list[list[float]]:
    if not label_path.is_file():
        return []
    boxes = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        _, x_center, y_center, box_width, box_height = (float(value) for value in line.split())
        boxes.append([(x_center - box_width / 2) * width, (y_center - box_height / 2) * height,
                      (x_center + box_width / 2) * width, (y_center + box_height / 2) * height])
    return boxes


def choose_examples(rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    """Prefer distinct recordings, then select the highest-confidence examples."""
    by_recording: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_recording[row["source_sequence"]].append(row)
    selected = sorted(
        (max(candidates, key=lambda row: float(row["max_confidence"])) for candidates in by_recording.values()),
        key=lambda row: float(row["max_confidence"]), reverse=True,
    )[:limit]
    if len(selected) < limit:
        chosen_paths = {row["image_path"] for row in selected}
        remaining = sorted((row for row in rows if row["image_path"] not in chosen_paths),
                           key=lambda row: float(row["max_confidence"]), reverse=True)
        selected.extend(remaining[:limit - len(selected)])
    return selected


def load_predictions(predictions_path: Path) -> dict[str, list[dict[str, str]]]:
    predictions: dict[str, list[dict[str, str]]] = defaultdict(list)
    with predictions_path.open(newline="", encoding="utf-8") as handle:
        for prediction in csv.DictReader(handle):
            predictions[prediction["image_path"]].append(prediction)
    return predictions


def replay_predictions(rows: list[dict[str, str]], weights_path: Path, output_path: Path, device: str) -> dict[str, list[dict[str, str]]]:
    """Save boxes for selected images without changing their recorded outcomes."""
    from ultralytics import YOLO

    model = YOLO(weights_path)
    image_paths = [str(REPOSITORY_ROOT / row["image_path"]) for row in rows]
    predictions: dict[str, list[dict[str, str]]] = defaultdict(list)
    exported = []
    results = model.predict(image_paths, imgsz=640, conf=0.001, device=device, verbose=False, stream=True)
    for row, result in zip(rows, results):
        if result.boxes is None:
            continue
        for xyxy, confidence, class_id in zip(result.boxes.xyxy.cpu().tolist(), result.boxes.conf.cpu().tolist(), result.boxes.cls.cpu().tolist()):
            prediction = {"image_path": row["image_path"], "predicted_class_id": str(int(class_id)),
                          "confidence": f"{confidence:.8f}", "predicted_xyxy": str([round(value, 4) for value in xyxy])}
            predictions[row["image_path"]].append(prediction)
            exported.append(prediction)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image_path", "predicted_class_id", "confidence", "predicted_xyxy"])
        writer.writeheader()
        writer.writerows(exported)
    return predictions


def draw_box(draw: ImageDraw.ImageDraw, box: list[float], color: str, label: str, position: str, width: int, height: int) -> None:
    left, top, right, bottom = (round(value) for value in box)
    draw.rectangle((left, top, right, bottom), outline=color, width=3)
    bounds = draw.textbbox((0, 0), label)
    label_width, label_height = bounds[2] - bounds[0], bounds[3] - bounds[1]
    label_x = max(2, right - label_width - 3)
    if position == "top":
        label_y = max(2, top - label_height - 4)
    else:
        label_x = min(right + 6, max(2, width - label_width - 2))
        label_y = min(bottom + 5, max(2, height - label_height - 2))
    draw.text((label_x, label_y), label, fill=color, stroke_width=1, stroke_fill="black")


def annotate(row: dict[str, str], predictions: dict[str, list[dict[str, str]]], threshold: float) -> Image.Image:
    with Image.open(REPOSITORY_ROOT / row["image_path"]) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    for box in yolo_ground_truth(REPOSITORY_ROOT / row["label_path"], image.width, image.height):
        draw_box(draw, box, "#32d583", "ground truth", "top", image.width, image.height)
    for prediction in predictions.get(row["image_path"], []):
        confidence = float(prediction["confidence"] or 0.0)
        box = parse_box(prediction["predicted_xyxy"])
        if confidence >= threshold and box:
            draw_box(draw, box, "#ff625f", f"prediction {confidence:.2f}", "bottom", image.width, image.height)
    return image


def make_panel(title: str, subtitle: str, rows: list[dict[str, str]], predictions: dict[str, list[dict[str, str]]], output_path: Path, threshold: float) -> None:
    tile_width, tile_height, caption_height, columns, title_height = 480, 360, 54, 2, 64
    panel_rows = max(1, math.ceil(len(rows) / columns))
    canvas = Image.new("RGB", (columns * tile_width, title_height + panel_rows * (tile_height + caption_height)), "#101827")
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 10), title, fill="white", font=ImageFont.load_default())
    draw.text((16, 32), subtitle, fill="#cbd5e1", font=ImageFont.load_default())
    if not rows:
        draw.text((16, title_height + 16), "No held-out examples at the recorded threshold.", fill="white", font=ImageFont.load_default())
    for index, row in enumerate(rows):
        annotated = annotate(row, predictions, threshold)
        annotated.thumbnail((tile_width, tile_height))
        x = (index % columns) * tile_width + (tile_width - annotated.width) // 2
        y = title_height + (index // columns) * (tile_height + caption_height) + (tile_height - annotated.height) // 2
        canvas.paste(annotated, (x, y))
        caption_y = title_height + (index // columns) * (tile_height + caption_height) + tile_height + 5
        caption = f"{row['source_sequence']} frame {row['original_frame']} | max confidence {float(row['max_confidence']):.2f}"
        draw.text((index % columns * tile_width + 8, caption_y), caption, fill="white", font=ImageFont.load_default())
    canvas.save(output_path, quality=95)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation-root", type=Path, default=DEFAULT_EVALUATION_ROOT)
    parser.add_argument("--weights", type=Path, help="Required if test_predictions.csv is absent.")
    parser.add_argument("--threshold", type=float, help="Defaults to test_decision_metrics.json.")
    parser.add_argument("--device", default="0", help="Ultralytics inference device; use cpu if needed.")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    root = args.evaluation_root.resolve()
    decisions_path, metrics_path = root / "test_image_decisions.csv", root / "test_decision_metrics.json"
    if not decisions_path.is_file() or not metrics_path.is_file():
        raise FileNotFoundError(f"Expected decision artifacts under {root}")
    threshold = args.threshold if args.threshold is not None else float(json.loads(metrics_path.read_text(encoding="utf-8"))["decision_threshold"])
    with decisions_path.open(newline="", encoding="utf-8") as handle:
        decisions = list(csv.DictReader(handle))
    selected_by_outcome = {outcome: choose_examples([row for row in decisions if row["binary_outcome"] == outcome], limit)
                           for outcome, _, _, limit in PANEL_SPECS}
    selections = [{"panel": outcome, "rank": rank, **row}
                  for outcome, _, _, _ in PANEL_SPECS
                  for rank, row in enumerate(selected_by_outcome[outcome], start=1)]
    output_directory = root / "error_analysis"
    saved_predictions = root / "test_predictions.csv"
    if saved_predictions.is_file():
        predictions, box_source = load_predictions(saved_predictions), "saved_test_predictions"
    else:
        if args.weights is None:
            raise FileNotFoundError("No test_predictions.csv found; supply --weights to replay boxes for selected images.")
        predictions = replay_predictions(selections, args.weights.resolve(), output_directory / "replayed_selected_predictions.csv", args.device)
        box_source = "replayed_selected_predictions"
    output_directory.mkdir(parents=True, exist_ok=True)
    for outcome, title, subtitle, _ in PANEL_SPECS:
        make_panel(title, subtitle, selected_by_outcome[outcome], predictions, output_directory / f"{outcome}_panel.jpg", threshold)
    with (output_directory / "selection_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["panel", "rank", *decisions[0].keys()])
        writer.writeheader()
        writer.writerows(selections)
    (output_directory / "README.txt").write_text(
        f"Panel outcomes are from {decisions_path.name} at recorded threshold {threshold:.2f}.\n"
        f"Box source: {box_source}. Replayed boxes are visualization-only and do not change saved decisions or metrics.\n",
        encoding="utf-8",
    )
    print(f"Wrote panels to {output_directory}")


if __name__ == "__main__":
    main()
