"""Create curated held-out Thermal-IR decision panels from saved evaluation data.

The panels are report artifacts, not a new evaluation: all image categories are
read from ``test_image_decisions.csv`` at the recorded operating threshold.
"""

from __future__ import annotations

import ast
import csv
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPOSITORY_ROOT / "results" / "thermal-ir" / "evaluation" / "experiment_a_dataset2_only_batch32"
DECISIONS_PATH = EVALUATION_ROOT / "test_image_decisions.csv"
PREDICTIONS_PATH = EVALUATION_ROOT / "test_predictions.csv"
OUTPUT_DIRECTORY = EVALUATION_ROOT / "error_analysis"
DECISION_THRESHOLD = 0.25
PANEL_SPECS = (
    ("true_positive", "True-positive drones", "Drone present and correctly reported", 4),
    ("false_negative", "Missed drones", "Drone present but not reported at the 0.25 threshold", 4),
    ("true_negative", "Correct bird rejections", "Bird frame correctly reported as no drone", 4),
    ("false_positive", "Bird false positives", "Bird frame incorrectly reported as a drone", 5),
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
        boxes.append([
            (x_center - box_width / 2) * width,
            (y_center - box_height / 2) * height,
            (x_center + box_width / 2) * width,
            (y_center + box_height / 2) * height,
        ])
    return boxes


def choose_examples(rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    """Prefer distinct recordings, then use confidence to select informative frames."""
    by_recording: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_recording[row["source_sequence"]].append(row)
    best_per_recording = []
    for candidates in by_recording.values():
        best_per_recording.append(max(candidates, key=lambda row: float(row["max_confidence"])))
    selected = sorted(best_per_recording, key=lambda row: float(row["max_confidence"]), reverse=True)[:limit]
    if len(selected) < limit:
        chosen_paths = {row["image_path"] for row in selected}
        remaining = sorted(
            (row for row in rows if row["image_path"] not in chosen_paths),
            key=lambda row: float(row["max_confidence"]),
            reverse=True,
        )
        selected.extend(remaining[: limit - len(selected)])
    return selected


def draw_box(draw: ImageDraw.ImageDraw, box: list[float], color: str, label: str, label_position: str, image_width: int, image_height: int) -> None:
    left, top, right, bottom = (round(value) for value in box)
    draw.rectangle((left, top, right, bottom), outline=color, width=3)
    label_bounds = draw.textbbox((0, 0), label)
    label_width = label_bounds[2] - label_bounds[0]
    label_height = label_bounds[3] - label_bounds[1]
    label_x = max(2, right - label_width - 3)
    if label_position == "top_right":
        label_y = max(2, top - label_height - 4)
    elif label_position == "bottom_right":
        label_x = min(right + 6, max(2, image_width - label_width - 2))
        label_y = min(bottom + 5, max(2, image_height - label_height - 2))
    else:
        raise ValueError(f"Unsupported label position: {label_position}")
    draw.text((label_x, label_y), label, fill=color, stroke_width=1, stroke_fill="black")


def annotate(row: dict[str, str], predictions: dict[str, list[dict[str, str]]]) -> Image.Image:
    image_path = REPOSITORY_ROOT / row["image_path"]
    label_path = REPOSITORY_ROOT / row["label_path"]
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    for box in yolo_ground_truth(label_path, image.width, image.height):
        draw_box(draw, box, "#32d583", "ground truth", "top_right", image.width, image.height)
    for prediction in predictions.get(row["image_path"], []):
        confidence = float(prediction["confidence"] or 0.0)
        if confidence >= DECISION_THRESHOLD:
            box = parse_box(prediction["predicted_xyxy"])
            if box:
                draw_box(draw, box, "#ff625f", f"prediction {confidence:.2f}", "bottom_right", image.width, image.height)
    return image


def make_panel(title: str, subtitle: str, rows: list[dict[str, str]], predictions: dict[str, list[dict[str, str]]], output_path: Path) -> None:
    tile_width, tile_height, caption_height = 480, 360, 54
    columns = 2
    panel_rows = math.ceil(len(rows) / columns)
    title_height = 64
    canvas = Image.new("RGB", (columns * tile_width, title_height + panel_rows * (tile_height + caption_height)), "#101827")
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 10), title, fill="white", font=ImageFont.load_default())
    draw.text((16, 32), subtitle, fill="#cbd5e1", font=ImageFont.load_default())
    for index, row in enumerate(rows):
        annotated = annotate(row, predictions)
        annotated.thumbnail((tile_width, tile_height))
        x = (index % columns) * tile_width + (tile_width - annotated.width) // 2
        y = title_height + (index // columns) * (tile_height + caption_height) + (tile_height - annotated.height) // 2
        canvas.paste(annotated, (x, y))
        caption_y = title_height + (index // columns) * (tile_height + caption_height) + tile_height + 5
        caption = f"{row['source_sequence']} frame {row['original_frame']} | max confidence {float(row['max_confidence']):.2f}"
        draw.text((index % columns * tile_width + 8, caption_y), caption, fill="white", font=ImageFont.load_default())
    canvas.save(output_path, quality=95)


def main() -> None:
    with DECISIONS_PATH.open(newline="", encoding="utf-8") as handle:
        decisions = list(csv.DictReader(handle))
    with PREDICTIONS_PATH.open(newline="", encoding="utf-8") as handle:
        raw_predictions = list(csv.DictReader(handle))
    predictions: dict[str, list[dict[str, str]]] = defaultdict(list)
    for prediction in raw_predictions:
        predictions[prediction["image_path"]].append(prediction)
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    selections = []
    for outcome, title, subtitle, limit in PANEL_SPECS:
        candidates = [row for row in decisions if row["binary_outcome"] == outcome]
        selected = choose_examples(candidates, limit)
        make_panel(title, subtitle, selected, predictions, OUTPUT_DIRECTORY / f"{outcome}_panel.jpg")
        for rank, row in enumerate(selected, start=1):
            selections.append({"panel": outcome, "rank": rank, **row})
    with (OUTPUT_DIRECTORY / "selection_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=selections[0].keys())
        writer.writeheader()
        writer.writerows(selections)


if __name__ == "__main__":
    main()
