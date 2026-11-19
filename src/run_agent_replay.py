"""Run the coordination agent over simulated replay scenarios.

Each scenario becomes one alert for operator review, plus a decision log that
records the rule version and score floors, and a fixed-rule versus cascade
comparison. The run describes software behavior on simulated pairings and does
not measure detection performance. See docs/agent-coordination.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:  # `python src/run_agent_replay.py` puts src/ on the path
    from agent_interface import (
        DEFAULT_SCORE_FLOOR,
        AgentObservation,
        build_alert,
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


def observation_from_evidence(record: dict, deadline_s: float) -> AgentObservation:
    """Turn one replay evidence record into the observation the agent reads.

    Available evidence arrived at the open of the event. Delayed evidence
    arrived after the deadline, so it cannot vote. Missing evidence has no
    arrival. Low-quality evidence is kept and stays low quality.
    """
    status = EvidenceStatus(record["status"])
    if status == EvidenceStatus.AVAILABLE:
        arrival_s = 0.0
    elif status == EvidenceStatus.DELAYED:
        arrival_s = deadline_s + DELAYED_AFTER_DEADLINE_S
    elif status == EvidenceStatus.MISSING:
        arrival_s = None
    elif status == EvidenceStatus.LOW_QUALITY:
        arrival_s = 0.0
    else:
        raise ValueError(f"unsupported evidence status {status.value!r}")

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
    return AgentObservation(evidence, arrival_s)


def floors_used() -> dict[str, float]:
    return {sensor.value: floor for sensor, floor in DEFAULT_SCORE_FLOOR.items()}


def run_replay(replay_path: Path, deadline_s: float) -> dict:
    """Build one alert and one request list per scenario."""
    payload = json.loads(replay_path.read_text(encoding="utf-8"))
    scenarios = payload["scenarios"]
    entries = []
    for item in scenarios:
        record = item["record"]
        observations = tuple(
            observation_from_evidence(evidence, deadline_s) for evidence in record["evidence"]
        )
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
