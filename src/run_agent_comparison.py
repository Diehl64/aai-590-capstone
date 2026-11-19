"""Compare the fixed parallel rule with the agent cascade.

Both strategies read the same replay scenarios, score floors, and deadline.
The cascade does not contact a sensor: requesting one reveals its saved record.
See the comparison definition in the agent-replay notes. This describes software
behavior on simulated pairings and does not measure detection performance.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:  # `python src/run_agent_comparison.py` puts src/ on the path
    from agent_interface import DEFAULT_SCORE_FLOOR, AlertStatus, decide_status, recommend_requests
    from run_agent_replay import (
        DEFAULT_DEADLINE_S,
        DEFAULT_OUTPUT_DIR,
        DEFAULT_REPLAY,
        EXPECTED_SENSORS,
        observation_from_evidence,
    )
    from synthetic_replay import SensorType
except ImportError:  # imported as src.run_agent_comparison
    from src.agent_interface import DEFAULT_SCORE_FLOOR, AlertStatus, decide_status, recommend_requests
    from src.run_agent_replay import (
        DEFAULT_DEADLINE_S,
        DEFAULT_OUTPUT_DIR,
        DEFAULT_REPLAY,
        EXPECTED_SENSORS,
        observation_from_evidence,
    )
    from src.synthetic_replay import SensorType


COMPARISON_FIELDS = (
    "scenario",
    "fixed_status",
    "fixed_leading_hypothesis",
    "fixed_sensors_used",
    "cascade_status",
    "cascade_leading_hypothesis",
    "cascade_sensors_used",
    "status_differs",
)

_STOP = (AlertStatus.CONFIRMED, AlertStatus.CONFLICTING)


def _observations(evidence: list[dict], deadline_s: float) -> dict[SensorType, object]:
    by_sensor = {}
    for record in evidence:
        observation = observation_from_evidence(record, deadline_s)
        by_sensor[observation.sensor] = observation
    return by_sensor


def _fixed(by_sensor: dict, deadline_s: float):
    """Read every expected sensor at once. Sensors used is always all four."""
    observations = tuple(by_sensor[sensor] for sensor in EXPECTED_SENSORS if sensor in by_sensor)
    status, leading, _ = decide_status(observations, EXPECTED_SENSORS, deadline_s, DEFAULT_SCORE_FLOOR)
    return status, leading, len(EXPECTED_SENSORS)


def _cascade(by_sensor: dict, deadline_s: float):
    """RF opens the event. Request one sensor at a time until the status settles.

    A sensor not yet requested stays missing. A requested sensor counts as used
    even when its record is missing, delayed, or low quality. Sensors that are
    never requested do not count.
    """
    used = [SensorType.RF]
    observations = [by_sensor[SensorType.RF]] if SensorType.RF in by_sensor else []
    while True:
        status, leading, _ = decide_status(
            observations, EXPECTED_SENSORS, deadline_s, DEFAULT_SCORE_FLOOR,
        )
        if status in _STOP:
            break
        requests = recommend_requests(
            observations, EXPECTED_SENSORS, deadline_s, DEFAULT_SCORE_FLOOR,
        )
        nxt = next((sensor for sensor in requests if sensor not in used), None)
        if nxt is None:
            break
        used.append(nxt)
        if nxt in by_sensor:
            observations.append(by_sensor[nxt])
    return status, leading, len(used)


def _cell(status: AlertStatus, leading) -> tuple[str, str]:
    return status.value, "" if leading is None else leading.value


def compare_replay(replay_path: Path, deadline_s: float) -> list[dict[str, str]]:
    payload = json.loads(Path(replay_path).read_text(encoding="utf-8"))
    rows = []
    for item in payload["scenarios"]:
        by_sensor = _observations(item["record"]["evidence"], deadline_s)
        fixed_status, fixed_leading, fixed_used = _fixed(by_sensor, deadline_s)
        cascade_status, cascade_leading, cascade_used = _cascade(by_sensor, deadline_s)
        fixed_status_text, fixed_leading_text = _cell(fixed_status, fixed_leading)
        cascade_status_text, cascade_leading_text = _cell(cascade_status, cascade_leading)
        rows.append({
            "scenario": item["scenario"],
            "fixed_status": fixed_status_text,
            "fixed_leading_hypothesis": fixed_leading_text,
            "fixed_sensors_used": str(fixed_used),
            "cascade_status": cascade_status_text,
            "cascade_leading_hypothesis": cascade_leading_text,
            "cascade_sensors_used": str(cascade_used),
            "status_differs": "true" if fixed_status != cascade_status else "false",
        })
    return rows


def summary(rows: list[dict[str, str]]) -> str:
    count = len(rows)
    changed = sum(row["status_differs"] == "true" for row in rows)
    average = sum(int(row["cascade_sensors_used"]) for row in rows) / count if count else 0
    average_text = f"{average:.2f}".rstrip("0").rstrip(".")
    return (
        f"{changed} of {count} scenarios change status\n"
        f"cascade uses {average_text} sensors on average"
    )


def write_fixed_vs_cascade(replay_path: Path, output_dir: Path, deadline_s: float) -> tuple[Path, str]:
    rows = compare_replay(replay_path, deadline_s)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "fixed-vs-cascade.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COMPARISON_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path, summary(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare the fixed parallel rule with the agent cascade.")
    parser.add_argument("--replay", type=Path, default=DEFAULT_REPLAY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--deadline", type=float, default=DEFAULT_DEADLINE_S, help="seconds")
    args = parser.parse_args()
    if args.deadline < 0:
        raise SystemExit("--deadline cannot be negative")
    path, text = write_fixed_vs_cascade(args.replay, args.output_dir, args.deadline)
    print(text)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
