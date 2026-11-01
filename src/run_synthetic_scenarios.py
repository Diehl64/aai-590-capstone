#!/usr/bin/env python3
"""Write placeholder-only scenarios for developing the local replay contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from synthetic_replay import EvidenceStatus, SensorEvidence, SensorType, create_scenario, to_dict


def evidence(event_id: str, sensor_type: SensorType, prediction: str | None, score: float | None,
             status: EvidenceStatus = EvidenceStatus.AVAILABLE) -> SensorEvidence:
    return SensorEvidence(event_id, "2026-11-16T18:00:00Z", sensor_type, status, prediction, score,
                          "placeholder-not-a-model", f"placeholder://{event_id}/{sensor_type.value}", True)


def scenarios() -> dict[str, object]:
    return {
        "supporting_evidence": create_scenario([
            evidence("sim-001", SensorType.RF, "machine", .72),
            evidence("sim-001", SensorType.RADAR, "drone", .91),
            evidence("sim-001", SensorType.THERMAL, "drone", .88),
        ]),
        "rf_uncertain_radar_and_thermal_support": create_scenario([
            evidence("sim-002", SensorType.RF, "uncertain", .50),
            evidence("sim-002", SensorType.RADAR, "drone", .86),
            evidence("sim-002", SensorType.THERMAL, "drone", .83),
        ]),
        "thermal_missing": create_scenario([
            evidence("sim-003", SensorType.RF, "machine", .69),
            evidence("sim-003", SensorType.RADAR, "drone", .84),
            evidence("sim-003", SensorType.THERMAL, None, None, EvidenceStatus.MISSING),
        ]),
        "conflicting_evidence": create_scenario([
            evidence("sim-004", SensorType.RF, "benign", .76),
            evidence("sim-004", SensorType.RADAR, "drone", .82),
            evidence("sim-004", SensorType.THERMAL, "no_drone", .79),
        ]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/synthetic-replay"))
    args = parser.parse_args()
    output = {
        "workflow": "evidence_based_local_replay",
        "simulated_only": True,
        "placeholder_values_only": True,
        "not_a_measured_fusion_evaluation": True,
        "scenarios": [{"scenario": name, "record": to_dict(record)} for name, record in scenarios().items()],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "synthetic-scenarios.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
