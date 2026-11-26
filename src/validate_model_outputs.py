#!/usr/bin/env python3
"""Validate held-out single-model outputs before synthetic replay use."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Mapping


REQUIRED_COLUMNS = {
    "output_id", "sensor_type", "source_observation_id", "split", "timestamp",
    "predicted_label", "score", "model_version", "dataset_id", "source_output_ref",
}
SENSOR_TYPES = {"rf", "radar", "thermal", "acoustic"}


def load_dataset_registry(manifest: Path, aliases: Path | None = None) -> dict[str, str]:
    """Resolve exact dataset names to manifest IDs without changing saved outputs.

    Alias targets must be canonical manifest IDs; chains, duplicate definitions,
    and aliases that shadow a canonical ID are rejected.
    """
    registry: dict[str, str] = {}
    with manifest.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if "dataset_id" not in (reader.fieldnames or []):
            raise ValueError("dataset manifest requires a dataset_id column")
        for line, row in enumerate(reader, start=2):
            dataset_id = (row.get("dataset_id") or "").strip()
            if not dataset_id:
                raise ValueError(f"dataset manifest line {line}: empty dataset_id")
            if dataset_id in registry:
                raise ValueError(f"ambiguous dataset_id in manifest: {dataset_id!r}")
            registry[dataset_id] = dataset_id
    if not registry:
        raise ValueError("dataset manifest has no dataset IDs")
    canonical_ids = set(registry)
    if aliases is not None:
        with aliases.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            if not {"alias_id", "dataset_id"}.issubset(reader.fieldnames or []):
                raise ValueError("dataset aliases require alias_id and dataset_id columns")
            for line, row in enumerate(reader, start=2):
                alias_id = (row.get("alias_id") or "").strip()
                dataset_id = (row.get("dataset_id") or "").strip()
                if not alias_id or not dataset_id:
                    raise ValueError(f"dataset aliases line {line}: empty alias_id or dataset_id")
                if dataset_id not in canonical_ids:
                    raise ValueError(f"unknown canonical dataset_id for alias {alias_id!r}: {dataset_id!r}")
                if alias_id in registry:
                    raise ValueError(f"ambiguous dataset alias: {alias_id!r}")
                registry[alias_id] = dataset_id
    return registry


def validate(path: Path, *, dataset_registry: Mapping[str, str] | None = None) -> int:
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
        if dataset_registry is not None and row["dataset_id"] not in dataset_registry:
            raise ValueError(f"line {line}: unknown dataset_id {row['dataset_id']!r}")
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
    parser.add_argument("--dataset-manifest", type=Path, help="also check dataset IDs against this manifest")
    parser.add_argument("--dataset-aliases", type=Path, help="explicit alias CSV; requires --dataset-manifest")
    args = parser.parse_args()
    if args.dataset_aliases is not None and args.dataset_manifest is None:
        parser.error("--dataset-aliases requires --dataset-manifest")
    registry = (
        load_dataset_registry(args.dataset_manifest, args.dataset_aliases)
        if args.dataset_manifest is not None else None
    )
    print(f"validated {validate(args.path, dataset_registry=registry)} held-out model outputs")


if __name__ == "__main__":
    main()
