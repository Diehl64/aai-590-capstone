"""Create simulated replay cases from saved individual-model outputs.

This does not pair real-world sensor observations or calculate fusion accuracy.
Every generated scenario requires human review.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from synthetic_replay import (
    EvidenceStatus,
    SensorEvidence,
    SensorType,
    create_scenario,
    to_dict,
)
from validate_model_outputs import load_dataset_registry, validate


def load_rows(
    path: Path,
    expected_sensor_type: str | None = None,
    dataset_registry: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    validate(path, dataset_registry=dataset_registry)
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if expected_sensor_type and any(row["sensor_type"] != expected_sensor_type for row in rows):
        raise ValueError(f"{path}: expected only {expected_sensor_type} outputs")
    return rows


def first_with_label(rows: list[dict[str, str]], label: str) -> dict[str, str]:
    for row in rows:
        if row["predicted_label"] == label:
            return row
    raise ValueError(f"No saved output has predicted_label={label!r}")


def file_and_start(row: dict[str, str]) -> tuple[str, int] | None:
    observation_id = row["source_observation_id"]
    marker = "-start-"
    if marker not in observation_id:
        return None
    file_id, start = observation_id.rsplit(marker, 1)
    try:
        return file_id, int(start)
    except ValueError:
        return None


def first_full_length(rows: list[dict[str, str]], label: str) -> dict[str, str]:
    """Pick a 1-second window that is not the short tail of its recording.

    The handoff has no padding column. A window is full length when the same
    recording has another window starting at least 16,000 samples later.
    """
    starts = set()
    labeled = []
    for row in rows:
        located = file_and_start(row)
        if located is None:
            continue
        starts.add(located)
        if row["predicted_label"] == label:
            labeled.append((located, row))
    for (file_id, start), row in labeled:
        if (file_id, start + 16_000) in starts:
            return row
    raise ValueError(f"No demonstrably full-length acoustic window for label {label!r}")


# Test images with a byte-identical copy outside the test split, from the
# 2026-11-18 check of the assignment images. Retained from PR #55 and checked
# against the committed rf_integrity_checks.json when preparing this integration.
RF_TEST_FILENAMES_WITH_COPY_OUTSIDE_TEST = frozenset({
    "aug_Broadband_Jam_000773.png",
    "aug_Broadband_Jam_000862.png",
    "aug_Narrowband_Jam_000129.png",
    "aug_Narrowband_Jam_000360.png",
    "aug_Narrowband_Jam_000459.png",
    "aug_Narrowband_Jam_000462.png",
    "aug_Narrowband_Jam_000770.png",
    "aug_Narrowband_Jam_001317.png",
    "aug_Narrowband_Jam_001462.png",
    "aug_Narrowband_Jam_001497.png",
    "aug_Narrowband_Jam_001510.png",
    "aug_Narrowband_Jam_001566.png",
    "aug_Narrowband_Jam_001662.png",
    "aug_Narrowband_Jam_001678.png",
    "aug_Narrowband_Jam_001816.png",
    "aug_Narrowband_Jam_001959.png",
    "aug_Narrowband_Jam_002101.png",
    "aug_Narrowband_Jam_002127.png",
    "aug_Narrowband_Jam_002194.png",
    "aug_Narrowband_Jam_002233.png",
    "aug_Narrowband_Jam_002261.png",
    "aug_Narrowband_Jam_002915.png",
    "aug_Narrowband_Jam_002931.png",
    "aug_Narrowband_Jam_003366.png",
    "aug_Narrowband_Jam_003448.png",
    "aug_Narrowband_Jam_003497.png",
    "aug_Narrowband_Jam_003514.png",
    "aug_Narrowband_Jam_003795.png",
    "aug_Narrowband_Jam_003880.png",
    "dronerf_090083.png",
    "jam_Broadband_Jam_001323.png",
    "jam_Narrowband_Jam_000125.png",
    "radar_011894.png",
    "radar_011902.png",
    "radar_011903.png",
    "radar_011904.png",
    "radar_011906.png",
    "radar_011908.png",
    "radar_011911.png",
    "radar_013276.png",
    "radar_013302.png",
})


def load_rf_manifest(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row["split"] == "test"]
    names = [row["filename"] for row in rows]
    if not names or any(not name or not name.strip() for name in names) or len(names) != len(set(names)):
        raise ValueError("RF manifest must have unique, nonempty test filenames")
    return {row["filename"]: row["class"] for row in rows}


def first_clean_rf(
    rows: list[dict[str, str]],
    label: str,
    manifest: dict[str, str],
    excluded: frozenset[str] = RF_TEST_FILENAMES_WITH_COPY_OUTSIDE_TEST,
    true_class: str | None = None,
) -> dict[str, str]:
    """Pick an RF row whose manifest class matches, skipping duplicate images.

    `true_class` defaults to `label`. Pass a different class only for a
    scenario that is meant to show a wrong prediction.
    """
    expected = label if true_class is None else true_class
    for row in rows:
        if row["predicted_label"] != label:
            continue
        filename = row["source_observation_id"]
        if filename in excluded:
            continue
        if manifest.get(filename) != expected:
            continue
        return row
    raise ValueError(
        f"No RF row for predicted_label={label!r} with true class {expected!r}"
    )


def actual_evidence(
    event_id: str,
    timestamp: str,
    row: dict[str, str],
    status: EvidenceStatus = EvidenceStatus.AVAILABLE,
) -> SensorEvidence:
    source_ref = (
        f"{row['source_output_ref']}#output_id={row['output_id']}"
        f";source_timestamp={row['timestamp']}"
    )
    return SensorEvidence(
        event_id=event_id,
        timestamp=timestamp,
        sensor_type=SensorType(row["sensor_type"]),
        status=status,
        prediction=row["predicted_label"],
        score=float(row["score"]),
        model_version=row["model_version"],
        source_ref=source_ref,
    )


def missing_evidence(
    event_id: str,
    timestamp: str,
    sensor_type: SensorType,
) -> SensorEvidence:
    return SensorEvidence(
        event_id=event_id,
        timestamp=timestamp,
        sensor_type=sensor_type,
        status=EvidenceStatus.MISSING,
        prediction=None,
        score=None,
        model_version="not-provided",
        source_ref="not-provided",
    )


def scenario(
    event_id: str,
    name: str,
    radar_row: dict[str, str] | None,
    thermal_row: dict[str, str] | None,
    radar_status: EvidenceStatus = EvidenceStatus.AVAILABLE,
    thermal_status: EvidenceStatus = EvidenceStatus.AVAILABLE,
    acoustic_row: dict[str, str] | None = None,
    acoustic_status: EvidenceStatus = EvidenceStatus.AVAILABLE,
    rf_row: dict[str, str] | None = None,
    rf_status: EvidenceStatus = EvidenceStatus.AVAILABLE,
) -> dict[str, object]:
    timestamp = f"simulated-event:{event_id}"
    if rf_row is None:
        evidence = [missing_evidence(event_id, timestamp, SensorType.RF)]
    else:
        evidence = [actual_evidence(event_id, timestamp, rf_row, rf_status)]
    if acoustic_row is None:
        evidence.append(missing_evidence(event_id, timestamp, SensorType.ACOUSTIC))
    else:
        evidence.append(actual_evidence(event_id, timestamp, acoustic_row, acoustic_status))

    if radar_row is None:
        evidence.append(missing_evidence(event_id, timestamp, SensorType.RADAR))
    else:
        evidence.append(actual_evidence(event_id, timestamp, radar_row, radar_status))

    if thermal_row is None:
        evidence.append(missing_evidence(event_id, timestamp, SensorType.THERMAL))
    else:
        evidence.append(actual_evidence(event_id, timestamp, thermal_row, thermal_status))

    return {"scenario": name, "record": to_dict(create_scenario(evidence))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--radar",
        type=Path,
        default=Path("data/model-outputs/radar-cnn-test-outputs.csv"),
    )
    parser.add_argument(
        "--thermal",
        type=Path,
        default=Path("data/model-outputs/thermal-dataset2-batch32-test-outputs.csv"),
    )
    acoustic_group = parser.add_mutually_exclusive_group()
    acoustic_group.add_argument(
        "--acoustic",
        type=Path,
        default=Path("data/model-outputs/acoustic-cnn-tuned-test-outputs.csv"),
    )
    acoustic_group.add_argument("--no-acoustic", action="store_const", const=None, dest="acoustic")
    parser.add_argument(
        "--rf",
        type=Path,
        default=None,
        help="Explicit saved RF CSV; omit to keep RF missing.",
    )
    parser.add_argument(
        "--rf-manifest",
        type=Path,
        default=Path("data/rf-split-manifest.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/real-output-replay/real-output-replay.json"),
    )
    parser.add_argument("--dataset-manifest", type=Path, default=Path("data/dataset-manifest.csv"))
    parser.add_argument("--dataset-aliases", type=Path, default=Path("data/dataset-id-aliases.csv"))
    args = parser.parse_args()
    if args.rf is not None and args.acoustic is None:
        parser.error("RF scenarios require acoustic input; omit --rf for the two-sensor replay")

    registry = load_dataset_registry(args.dataset_manifest, args.dataset_aliases)
    radar = load_rows(args.radar, "radar", registry)
    thermal = load_rows(args.thermal, "thermal", registry)
    acoustic = load_rows(args.acoustic, "acoustic", registry) if args.acoustic else None
    acoustic_drone = first_full_length(acoustic, "drone") if acoustic else None
    acoustic_no_drone = first_full_length(acoustic, "no_drone") if acoustic else None
    rf_machine = rf_benign = rf_jam = rf_false_alarm = None
    if args.rf:
        rf = load_rows(args.rf, "rf", registry)
        manifest = load_rf_manifest(args.rf_manifest)
        source_ids = [row["source_observation_id"] for row in rf]
        if len(source_ids) != len(set(source_ids)) or set(source_ids) != set(manifest):
            raise ValueError("RF outputs must match the manifest test IDs exactly once")
        rf_machine = first_clean_rf(rf, "Machine", manifest)
        rf_benign = first_clean_rf(rf, "Benign", manifest)
        rf_jam = first_clean_rf(rf, "Broadband_Jam", manifest)
        rf_false_alarm = first_clean_rf(rf, "Machine", manifest, true_class="Benign")

    scenarios = [
        scenario(
            "sim-real-001",
            "all_three_predict_drone" if acoustic else "radar_thermal_predict_drone",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
            acoustic_row=acoustic_drone,
            rf_row=rf_machine,
        ),
        scenario(
            "sim-real-002",
            "radar_drone_thermal_no_drone",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "no_drone"),
            acoustic_row=acoustic_no_drone,
            rf_row=rf_benign,
        ),
        scenario(
            "sim-real-003",
            "radar_bird_thermal_no_drone",
            first_with_label(radar, "bird"),
            first_with_label(thermal, "no_drone"),
            acoustic_row=acoustic_no_drone,
            rf_row=rf_benign,
        ),
        scenario(
            "sim-real-004",
            "radar_human_thermal_drone",
            first_with_label(radar, "human"),
            first_with_label(thermal, "drone"),
            acoustic_row=acoustic_drone,
            rf_row=rf_machine,
        ),
        scenario(
            "sim-real-005",
            "thermal_missing",
            first_with_label(radar, "drone"),
            None,
            acoustic_row=acoustic_drone,
            rf_row=rf_machine,
        ),
        scenario(
            "sim-real-006",
            "thermal_delayed",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
            thermal_status=EvidenceStatus.DELAYED,
            acoustic_row=acoustic_drone,
            rf_row=rf_machine,
        ),
        scenario(
            "sim-real-007",
            "radar_missing",
            None,
            first_with_label(thermal, "drone"),
            acoustic_row=acoustic_drone,
            rf_row=rf_machine,
        ),
        scenario(
            "sim-real-008",
            "radar_delayed",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
            radar_status=EvidenceStatus.DELAYED,
            acoustic_row=acoustic_drone,
            rf_row=rf_machine,
        ),
        scenario(
            "sim-real-009",
            "thermal_low_quality",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
            thermal_status=EvidenceStatus.LOW_QUALITY,
            acoustic_row=acoustic_drone,
            rf_row=rf_machine,
        ),
        scenario(
            "sim-real-010",
            "all_non_drone_predictions",
            first_with_label(radar, "human"),
            first_with_label(thermal, "no_drone"),
            acoustic_row=acoustic_no_drone,
            rf_row=rf_benign,
        ),
    ]
    if acoustic:
        scenarios.extend([
            scenario(
                "sim-real-011",
                "radar_and_thermal_missing" if args.rf else "acoustic_only_sensor_available",
                None,
                None,
                acoustic_row=acoustic_drone,
                rf_row=rf_machine,
            ),
            scenario(
                "sim-real-012",
                "radar_thermal_drone_acoustic_disagrees",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_no_drone,
                rf_row=rf_benign,
            ),
            scenario(
                "sim-real-013",
                "only_acoustic_hears_drone",
                first_with_label(radar, "human"),
                first_with_label(thermal, "no_drone"),
                acoustic_row=acoustic_drone,
                rf_row=rf_benign,
            ),
            scenario(
                "sim-real-014",
                "acoustic_missing",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                rf_row=rf_machine,
            ),
            scenario(
                "sim-real-015",
                "acoustic_delayed",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
                acoustic_status=EvidenceStatus.DELAYED,
                rf_row=rf_machine,
            ),
            scenario(
                "sim-real-016",
                "acoustic_low_quality",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
                acoustic_status=EvidenceStatus.LOW_QUALITY,
                rf_row=rf_machine,
            ),
        ])
    if args.rf:
        scenarios.extend([
            scenario(
                "sim-real-017",
                "rf_machine_with_three_drone_predictions",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
                rf_row=rf_machine,
            ),
            scenario(
                "sim-real-018",
                "rf_machine_false_alarm_others_no_drone",
                first_with_label(radar, "human"),
                first_with_label(thermal, "no_drone"),
                acoustic_row=acoustic_no_drone,
                rf_row=rf_false_alarm,
            ),
            scenario(
                "sim-real-019",
                "rf_benign_others_drone",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
                rf_row=rf_benign,
            ),
            scenario(
                "sim-real-020",
                "rf_only_sensor_available",
                None,
                None,
                rf_row=rf_machine,
            ),
            scenario(
                "sim-real-021",
                "rf_jamming_others_drone",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
                rf_row=rf_jam,
            ),
            scenario(
                "sim-real-022",
                "rf_delayed",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
                rf_row=rf_machine,
                rf_status=EvidenceStatus.DELAYED,
            ),
            scenario(
                "sim-real-023",
                "rf_low_quality",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
                rf_row=rf_machine,
                rf_status=EvidenceStatus.LOW_QUALITY,
            ),
            scenario(
                "sim-real-024",
                "rf_missing",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                acoustic_row=acoustic_drone,
            ),
            scenario(
                "sim-real-025",
                "radar_low_quality",
                first_with_label(radar, "drone"),
                first_with_label(thermal, "drone"),
                radar_status=EvidenceStatus.LOW_QUALITY,
                acoustic_row=acoustic_drone,
                rf_row=rf_machine,
            ),
        ])

    available = ["radar", "thermal"] + (["acoustic"] if acoustic else [])
    if args.rf:
        available.insert(0, "rf")
    output = {
        "workflow": "partial_real_output_simulated_replay",
        "simulated_only": True,
        "not_a_measured_fusion_evaluation": True,
        "review_required_for_every_scenario": True,
        "available_sensor_types": available,
        "missing_sensor_types": [sensor for sensor in ("rf", "acoustic") if sensor not in available],
        "input_files": {
            sensor: str(path) for sensor, path in (
                ("radar", args.radar), ("thermal", args.thermal),
                ("acoustic", args.acoustic), ("rf", args.rf),
            ) if path is not None
        },
        "rf_manifest": str(args.rf_manifest) if args.rf else None,
        "score_semantics": "Unmodified per-model scores; interpretation depends on modality; not fused or calibrated confidence.",
        "scenarios": scenarios,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
