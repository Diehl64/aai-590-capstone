#!/usr/bin/env python3
"""Validate held-out single-model outputs before synthetic replay use."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


REQUIRED_COLUMNS = {
    "output_id", "sensor_type", "source_observation_id", "split", "timestamp",
    "predicted_label", "score", "model_version", "dataset_id", "source_output_ref",
}
SENSOR_TYPES = {"rf", "radar", "thermal", "acoustic"}


def validate(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    if not rows:
        raise ValueError("output file has no rows")
    seen_ids: set[str] = set()
    for line, row in enumerate(rows, start=2):
        empty = [key for key in REQUIRED_COLUMNS if not row.get(key, "").strip()]
        if empty:
            raise ValueError(f"line {line}: empty required values: {', '.join(sorted(empty))}")
        if row["output_id"] in seen_ids:
            raise ValueError(f"line {line}: duplicate output_id {row['output_id']!r}")
        seen_ids.add(row["output_id"])
        if row["sensor_type"] not in SENSOR_TYPES:
            raise ValueError(f"line {line}: unsupported sensor_type {row['sensor_type']!r}")
        if row["split"] != "test":
            raise ValueError(f"line {line}: only held-out test outputs are allowed")
        try:
            score = float(row["score"])
        except ValueError as exc:
            raise ValueError(f"line {line}: score is not numeric") from exc
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"line {line}: score must be between zero and one")
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(f"validated {validate(args.path)} held-out model outputs")


if __name__ == "__main__":
    main()
