"""Write standard held-out model-output files for synthetic replay."""
from __future__ import annotations

import csv
from pathlib import Path


FIELDS = [
    "output_id", "sensor_type", "source_observation_id", "split", "timestamp",
    "predicted_label", "score", "model_version", "dataset_id", "source_output_ref",
]


def write_handoff(path: Path, rows: list[dict[str, object]]) -> None:
    """Write rows using the repository's shared model-output schema."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
