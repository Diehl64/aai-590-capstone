"""Run the coordination agent over simulated replay scenarios.

Each scenario becomes one alert for operator review, plus a decision log that
records the rule version and score floors, and a fixed-rule versus cascade
comparison. A record that names a handoff output_id is scored from that row,
using calibrated_score when the model's threshold uses it. The run describes
software behavior on simulated pairings and does not measure detection
performance. See docs/agent-coordination.md.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path

try:  # `python src/run_agent_replay.py` puts src/ on the path
    from agent_interface import (
        DEFAULT_SCORE_FLOOR,
        AgentObservation,
        build_alert,
        observation_from_handoff,
        recommend_requests,
        to_dict,
    )
    from agent_log import write_agent_log
    from synthetic_replay import EvidenceStatus, SensorEvidence, SensorType
except ImportError:  # imported as src.run_agent_replay
    from src.agent_interface import (
        DEFAULT_SCORE_FLOOR,
        AgentObservation,
        build_alert,
        observation_from_handoff,
        recommend_requests,
        to_dict,
    )
    from src.agent_log import write_agent_log
    from src.synthetic_replay import EvidenceStatus, SensorEvidence, SensorType


# Names decide_status() in src/agent_interface.py. Bump when those rules change.
RULE_VERSION = "decide_status-v1"

# Every replay event is judged against all four sensors, including ones with no record.
EXPECTED_SENSORS: tuple[SensorType, ...] = (
    SensorType.RF,
    SensorType.ACOUSTIC,
    SensorType.RADAR,
    SensorType.THERMAL,
)

# A delayed record arrived, but not in time to vote.
DELAYED_AFTER_DEADLINE_S = 1.0

DEFAULT_REPLAY = Path("results/real-output-replay/real-output-replay.json")
DEFAULT_OUTPUT_DIR = Path("results/agent-replay")
DEFAULT_DEADLINE_S = 5.0


def arrival_for_status(status: EvidenceStatus, deadline_s: float) -> float | None:
    """Available evidence arrived at the open of the event. Delayed evidence
    arrived after the deadline, so it cannot vote. Missing evidence has no
    arrival. Low-quality evidence is kept and stays low quality.
    """
    if status == EvidenceStatus.AVAILABLE:
        return 0.0
    if status == EvidenceStatus.DELAYED:
        return deadline_s + DELAYED_AFTER_DEADLINE_S
    if status == EvidenceStatus.MISSING:
        return None
    if status == EvidenceStatus.LOW_QUALITY:
        return 0.0
    raise ValueError(f"unsupported evidence status {status.value!r}")


def output_id_from_source_ref(source_ref: str) -> str | None:
    """Return the handoff output_id stored in a replay source_ref, if it has one."""
    marker = "output_id="
    if marker not in source_ref:
        return None
    output_id = source_ref.split(marker, 1)[1].split(";", 1)[0].strip()
    return output_id or None


def index_handoff(path: Path) -> tuple[dict[str, dict[str, str]], str]:
    """Index one handoff CSV by output_id and name the score column its threshold uses."""
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    score_type = "calibrated_score" if "calibrated_score" in fieldnames else "score"
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        output_id = row.get("output_id", "")
        if not output_id:
            raise ValueError(f"{path} has a handoff row with no output_id")
        if output_id in index:
            raise ValueError(f"duplicate output_id {output_id!r} in {path}")
        index[output_id] = row
    return index, score_type


def load_handoffs(payload: dict) -> tuple[dict[str, dict[str, dict[str, str]]], dict[str, str]]:
    """Read input_files from a replay document. Paths are relative to the working directory."""
    handoffs: dict[str, dict[str, dict[str, str]]] = {}
    score_types: dict[str, str] = {}
    for sensor, path in (payload.get("input_files") or {}).items():
        index, score_type = index_handoff(Path(path))
        handoffs[str(sensor)] = index
        score_types[str(sensor)] = score_type
    return handoffs, score_types


def observation_from_evidence(record: dict, deadline_s: float) -> AgentObservation:
    """Turn one replay evidence record into an observation when it has no handoff row.

    The fixture and missing records use this path. A record with an output_id is
    read from the handoff instead, so the score is the one the model's threshold uses.
    """
    status = EvidenceStatus(record["status"])
    evidence = SensorEvidence(
        event_id=record["event_id"],
        timestamp=record["timestamp"],
        sensor_type=SensorType(record["sensor_type"]),
        status=status,
        prediction=record["prediction"],
        score=record["score"],
        model_version=record["model_version"],
        source_ref=record["source_ref"],
        placeholder_value=bool(record.get("placeholder_value", False)),
    )
    return AgentObservation(evidence, arrival_for_status(status, deadline_s))


def observation_for_record(record: dict, deadline_s: float,
                           handoffs: dict[str, dict[str, dict[str, str]]]) -> AgentObservation:
    """Build one observation from the handoff row named in source_ref.

    The replay JSON keeps each model's raw score. The floor is applied to the
    score the model's own threshold uses, which for RF is calibrated_score.
    The scenario status and arrival are then put back on that observation.
    """
    output_id = output_id_from_source_ref(str(record.get("source_ref") or ""))
    if output_id is None:
        return observation_from_evidence(record, deadline_s)
    sensor = str(record["sensor_type"])
    if sensor not in handoffs:
        raise ValueError(f"no handoff file for {sensor} output_id {output_id!r}")
    row = handoffs[sensor].get(output_id)
    if row is None:
        raise ValueError(f"handoff file for {sensor} has no output_id {output_id!r}")
    status = EvidenceStatus(record["status"])
    arrival_s = arrival_for_status(status, deadline_s)
    item = observation_from_handoff(
        row, record["event_id"], record["timestamp"], 0.0 if arrival_s is None else arrival_s,
    )
    if item.sensor.value != sensor:
        raise ValueError(
            f"handoff row {output_id!r} is {item.sensor.value}, not {sensor}"
        )
    evidence = replace(item.evidence, status=status)
    return AgentObservation(evidence, arrival_s, score_calibrated=item.score_calibrated)


def observations_for_evidence(evidence: list[dict], deadline_s: float,
                              handoffs: dict[str, dict[str, dict[str, str]]]) -> tuple[AgentObservation, ...]:
    return tuple(observation_for_record(record, deadline_s, handoffs) for record in evidence)


def floors_used() -> dict[str, float]:
    return {sensor.value: floor for sensor, floor in DEFAULT_SCORE_FLOOR.items()}


def run_replay(replay_path: Path, deadline_s: float) -> dict:
    """Build one alert and one request list per scenario."""
    payload = json.loads(Path(replay_path).read_text(encoding="utf-8"))
    handoffs, score_types = load_handoffs(payload)
    scenarios = payload["scenarios"]
    entries = []
    for item in scenarios:
        record = item["record"]
        observations = observations_for_evidence(record["evidence"], deadline_s, handoffs)
        alert = build_alert(
            record["event_id"],
            observations,
            EXPECTED_SENSORS,
            deadline_s,
            DEFAULT_SCORE_FLOOR,
        )
        requests = recommend_requests(
            observations,
            EXPECTED_SENSORS,
            deadline_s,
            DEFAULT_SCORE_FLOOR,
        )
        entries.append({
            "scenario": item["scenario"],
            "alert": to_dict(alert),
            "recommended_requests": [sensor.value for sensor in requests],
        })
    return {
        "rule_version": RULE_VERSION,
        "floors_used": floors_used(),
        "score_types": score_types,
        "deadline_s": deadline_s,
        "scenarios": entries,
    }


def write_alerts(result: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "agent-alerts.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build coordination-agent alerts for replay scenarios.")
    parser.add_argument("--replay", type=Path, default=DEFAULT_REPLAY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--deadline", type=float, default=DEFAULT_DEADLINE_S, help="seconds")
    args = parser.parse_args()
    if args.deadline < 0:
        raise SystemExit("--deadline cannot be negative")

    result = run_replay(args.replay, args.deadline)
    path = write_alerts(result, args.output_dir)
    observations_path = args.output_dir / "agent-observations.csv"
    alerts_path = args.output_dir / "agent-alerts.csv"
    write_agent_log(result, observations_path, alerts_path)
    try:  # imported here so the comparison module can import this runner
        from run_agent_comparison import write_fixed_vs_cascade
    except ImportError:
        from src.run_agent_comparison import write_fixed_vs_cascade
    comparison_path, comparison_summary = write_fixed_vs_cascade(
        args.replay, args.output_dir, args.deadline,
    )
    print(f"wrote {len(result['scenarios'])} alerts to {path}")
    print(f"wrote decision log to {observations_path} and {alerts_path}")
    print(f"wrote comparison to {comparison_path}")
    print(comparison_summary)


if __name__ == "__main__":
    main()
