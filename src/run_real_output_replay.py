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
from validate_model_outputs import validate


def load_rows(path: Path) -> list[dict[str, str]]:
    validate(path)
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def first_with_label(rows: list[dict[str, str]], label: str) -> dict[str, str]:
    for row in rows:
        if row["predicted_label"] == label:
            return row
    raise ValueError(f"No saved output has predicted_label={label!r}")


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
) -> dict[str, object]:
    timestamp = f"simulated-event:{event_id}"
    evidence = [
        missing_evidence(event_id, timestamp, SensorType.RF),
        missing_evidence(event_id, timestamp, SensorType.ACOUSTIC),
    ]

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
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/real-output-replay/real-output-replay.json"),
    )
    args = parser.parse_args()

    radar = load_rows(args.radar)
    thermal = load_rows(args.thermal)

    scenarios = [
        scenario(
            "sim-real-001",
            "both_predict_drone",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
        ),
        scenario(
            "sim-real-002",
            "radar_drone_thermal_no_drone",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "no_drone"),
        ),
        scenario(
            "sim-real-003",
            "radar_bird_thermal_no_drone",
            first_with_label(radar, "bird"),
            first_with_label(thermal, "no_drone"),
        ),
        scenario(
            "sim-real-004",
            "radar_human_thermal_drone",
            first_with_label(radar, "human"),
            first_with_label(thermal, "drone"),
        ),
        scenario(
            "sim-real-005",
            "thermal_missing",
            first_with_label(radar, "drone"),
            None,
        ),
        scenario(
            "sim-real-006",
            "thermal_delayed",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
            thermal_status=EvidenceStatus.DELAYED,
        ),
        scenario(
            "sim-real-007",
            "radar_missing",
            None,
            first_with_label(thermal, "drone"),
        ),
        scenario(
            "sim-real-008",
            "radar_delayed",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
            radar_status=EvidenceStatus.DELAYED,
        ),
        scenario(
            "sim-real-009",
            "thermal_low_quality",
            first_with_label(radar, "drone"),
            first_with_label(thermal, "drone"),
            thermal_status=EvidenceStatus.LOW_QUALITY,
        ),
        scenario(
            "sim-real-010",
            "both_non_drone_predictions",
            first_with_label(radar, "human"),
            first_with_label(thermal, "no_drone"),
        ),
    ]

    output = {
        "workflow": "partial_real_output_simulated_replay",
        "simulated_only": True,
        "not_a_measured_fusion_evaluation": True,
        "review_required_for_every_scenario": True,
        "available_sensor_types": ["radar", "thermal"],
        "missing_sensor_types": ["rf", "acoustic"],
        "scenarios": scenarios,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
