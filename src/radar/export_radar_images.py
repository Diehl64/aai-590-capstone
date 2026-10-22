"""Export the SAAB/SIRS 77 GHz FMCW segments as a three-class PNG dataset.

The source file is never modified.  It is a pickled NumPy object array, so
memory mapping is unsupported; this script loads the container once and then
processes its embedded signal matrices in small column batches.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image


SOURCE_TO_CLASS = {
    "D1": "Drone", "D2": "Drone", "D3": "Drone", "D4": "Drone",
    "D5": "Drone", "D6": "Drone",
    "human_walk": "Human", "human_run": "Human",
    "seagull": "Bird", "pigeon": "Bird", "raven": "Bird",
    "seagull and black-headed gull": "Bird", "black-headed gull": "Bird",
    "heron": "Bird",
}
SPLITS = {1: "train", 2: "val", 3: "test"}


def scalar_label(value: object) -> str:
    """Convert the source's one-element label arrays to ordinary strings."""
    array = np.asarray(value).reshape(-1)
    if array.size != 1:
        raise ValueError(f"Expected one label, received shape {np.asarray(value).shape}")
    return str(array[0])


def calibration_limits(data: np.ndarray, sample_per_session: int, seed: int) -> tuple[float, float]:
    """Estimate fixed global dB limits from a reproducible, bounded sample."""
    generator = np.random.default_rng(seed)
    chunks: list[np.ndarray] = []
    for session in range(data.shape[0]):
        label = scalar_label(data[session, 0])
        if label not in SOURCE_TO_CLASS:
            continue
        signal = np.asarray(data[session, 1])
        count = min(sample_per_session, signal.size)
        flat_indices = generator.choice(signal.size, size=count, replace=False)
        values = signal.reshape(-1, order="F")[flat_indices]
        chunks.append(20.0 * np.log10(np.maximum(np.abs(values), np.finfo(np.float64).tiny)))
    sampled_db = np.concatenate(chunks)
    low, high = np.percentile(sampled_db, (1.0, 99.0))
    if not math.isfinite(low) or not math.isfinite(high) or high <= low:
        raise ValueError(f"Invalid calibration limits: {low}, {high}")
    return float(low), float(high)


def png_pixels(complex_segment: np.ndarray, db_low: float, db_high: float) -> np.ndarray:
    """Make a native-resolution 5-by-256 uint8 image with fixed global scaling."""
    if complex_segment.shape != (1280,):
        raise ValueError(f"Expected a 1280-value segment, got {complex_segment.shape}")
    # Source ordering: first 256 values are range cell 1, then range cell 2, etc.
    db = 20.0 * np.log10(np.maximum(np.abs(complex_segment), np.finfo(np.float64).tiny))
    db = db.reshape(5, 256)
    scaled = np.clip((db - db_low) / (db_high - db_low), 0.0, 1.0)
    return np.rint(scaled * 255.0).astype(np.uint8)


def verify_png(path: Path) -> None:
    """Verify a PNG, retrying briefly for Windows filesystem visibility."""
    last_error: Exception | None = None
    for _ in range(5):
        try:
            with Image.open(path) as check:
                check.verify()
            with Image.open(path) as check:
                if check.size != (256, 5) or check.mode != "L":
                    raise ValueError(f"Unexpected PNG properties: {check.mode} {check.size}")
            return
        except Exception as error:
            last_error = error
            time.sleep(0.02)
    raise last_error  # type: ignore[misc]


def save_png_atomically(pixels: np.ndarray, destination: Path) -> None:
    temporary = destination.with_suffix(".png.tmp")
    Image.fromarray(pixels, mode="L").save(temporary, format="PNG", optimize=False)
    last_error: Exception | None = None
    for _ in range(10):
        try:
            os.replace(temporary, destination)
            return
        except PermissionError as error:
            last_error = error
            time.sleep(0.05)
    raise last_error  # type: ignore[misc]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data_SAAB_SIRS_77GHz_FMCW.npy"))
    parser.add_argument("--output", type=Path, default=Path("data/radar"))
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--sample-per-session", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=20261021)
    args = parser.parse_args()

    # An existing output is treated as an interrupted export. Existing PNGs are
    # re-verified and retained; only missing images are created.
    if not args.source.is_file():
        raise FileNotFoundError(args.source)
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")

    print(f"Loading object container: {args.source}")
    data = np.load(args.source, allow_pickle=True)
    if data.shape != (130, 6) or data.dtype != object:
        raise ValueError(f"Unexpected source structure: shape={data.shape}, dtype={data.dtype}")

    db_low, db_high = calibration_limits(data, args.sample_per_session, args.seed)
    print(f"Using global 1st/99th percentile dB limits: {db_low:.6f}, {db_high:.6f}")

    output = args.output
    for split in SPLITS.values():
        for target_class in ("Drone", "Human", "Bird"):
            (output / split / target_class).mkdir(parents=True, exist_ok=True)

    metadata_path = output / "metadata.csv"
    metadata_temporary_path = output / "metadata.csv.tmp"
    source_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    class_split_counts: Counter[tuple[str, str]] = Counter()
    written_paths: set[str] = set()
    global_index = 0
    written = 0
    reused = 0
    errors: list[dict[str, object]] = []

    try:
        with metadata_temporary_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=[
                "image_path", "global_segment_index", "session_index", "session_segment_index",
                "source_label", "class_label", "split", "center_range_m", "time_s", "edge_flag",
                "image_width", "image_height", "db_low", "db_high",
            ])
            writer.writeheader()
            for session in range(data.shape[0]):
                source_label = scalar_label(data[session, 0])
                signal = np.asarray(data[session, 1])
                ranges = np.asarray(data[session, 2]).reshape(-1)
                times = np.asarray(data[session, 3]).reshape(-1)
                split_codes = np.asarray(data[session, 4]).reshape(-1)
                edge_flags = np.asarray(data[session, 5]).reshape(-1)
                segment_count = signal.shape[1]
                if signal.shape[0] != 1280 or not np.iscomplexobj(signal):
                    raise ValueError(f"Session {session}: unexpected signal shape/dtype {signal.shape}/{signal.dtype}")
                if not all(len(v) == segment_count for v in (ranges, times, split_codes, edge_flags)):
                    raise ValueError(f"Session {session}: metadata lengths do not match {segment_count} segments")

                for start in range(0, segment_count, args.batch_size):
                    end = min(start + args.batch_size, segment_count)
                    for local_index in range(start, end):
                        segment_global_index = global_index
                        global_index += 1
                        if source_label not in SOURCE_TO_CLASS:  # CR is deliberately excluded.
                            continue
                        target_class = SOURCE_TO_CLASS[source_label]
                        split_code = int(split_codes[local_index])
                        if split_code not in SPLITS:
                            raise ValueError(f"Session {session}, segment {local_index}: unknown split {split_code}")
                        split = SPLITS[split_code]
                        relative = Path(split) / target_class / f"{target_class}_segment_{segment_global_index:06d}.png"
                        destination = output / relative
                        needs_write = not destination.exists()
                        if not needs_write:
                            try:
                                verify_png(destination)
                            except Exception:
                                # A previous run may have been interrupted while this
                                # file was being written. It is safe to replace only
                                # this generated target with its deterministic source.
                                needs_write = True
                            else:
                                reused += 1
                        if needs_write:
                            pixels = png_pixels(signal[:, local_index], db_low, db_high)
                            save_png_atomically(pixels, destination)
                        # Verify every retained or written file, including native dimensions.
                        verify_png(destination)
                        key = relative.as_posix()
                        if key in written_paths:
                            raise ValueError(f"Duplicate output path: {key}")
                        written_paths.add(key)
                        writer.writerow({
                            "image_path": key, "global_segment_index": segment_global_index,
                            "session_index": session, "session_segment_index": local_index,
                            "source_label": source_label, "class_label": target_class, "split": split,
                            "center_range_m": f"{float(ranges[local_index]):.9g}",
                            "time_s": f"{float(times[local_index]):.9g}", "edge_flag": int(edge_flags[local_index]),
                            "image_width": 256, "image_height": 5,
                            "db_low": f"{db_low:.9g}", "db_high": f"{db_high:.9g}",
                        })
                        source_counts[source_label] += 1
                        split_counts[split] += 1
                        class_split_counts[(split, target_class)] += 1
                        written += 1
                        if written % 1000 == 0:
                            print(f"Validated {written:,} images ({reused:,} resumed); session {session + 1}/{data.shape[0]}", flush=True)
    except Exception:
        print("Export stopped due to an error; partial output was intentionally retained for diagnosis.", file=sys.stderr)
        raise

    os.replace(metadata_temporary_path, metadata_path)

    filesystem_counts = Counter()
    for split in SPLITS.values():
        for target_class in ("Drone", "Human", "Bird"):
            filesystem_counts[(split, target_class)] = len(list((output / split / target_class).glob("*.png")))
    if filesystem_counts != class_split_counts:
        raise RuntimeError(f"Filesystem/metadata count mismatch: {filesystem_counts} != {class_split_counts}")
    if written != len(written_paths):
        raise RuntimeError("Duplicate paths or count mismatch detected")

    report = {
        "source_file": str(args.source.resolve()), "source_modified": False,
        "excluded_source_labels": ["CR"], "output_root": str(output.resolve()),
        "image_representation": "uint8 grayscale, native 256 azimuth-sweep columns by 5 range-cell rows; 20*log10(abs(complex signal))",
        "normalization": {"method": "global sampled 1st/99th dB percentiles", "db_low": db_low, "db_high": db_high,
                          "sample_per_session": args.sample_per_session, "seed": args.seed},
        "images_written": written, "images_created_this_run": written - reused, "images_resumed": reused,
        "source_label_counts": dict(sorted(source_counts.items())),
        "split_counts": dict(sorted(split_counts.items())),
        "split_class_counts": {f"{split}/{label}": count for (split, label), count in sorted(class_split_counts.items())},
        "png_validation": "Every written file was reopened, verified, and checked as 256x5 grayscale.",
        "duplicate_output_paths": 0, "errors": errors,
        "leakage_note": "The supplied split is preserved, but all parent sessions contain segments in multiple splits; adjacent segments may be correlated across splits.",
    }
    (output / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "export_config.json").write_text(json.dumps({"source_to_class": SOURCE_TO_CLASS, "splits": SPLITS}, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
