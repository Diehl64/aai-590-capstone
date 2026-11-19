"""Write the coordination agent's decision log.

Two CSVs join on event_id. Observations are one row per sensor. Alerts are
one row per event, including the rule version and score floors that produced
the decision. operator_disposition is left empty for a later operator decision.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

OBSERVATION_FIELDS = (
    "event_id",
    "sensor",
    "state",
    "prediction",
    "hypothesis",
    "score",
    "score_calibrated",
    "model_version",
    "source_ref",
    "arrival_s",
)

ALERT_FIELDS = (
    "event_id",
    "scenario",
    "status",
    "leading_hypothesis",
    "reasons",
    "missing_sensors",
    "delayed_sensors",
    "recommended_requests",
    "rule_version",
    "floors_used",
    "deadline_s",
    "operator_disposition",
    "created_at",
)


def _cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _join(values: object) -> str:
    if not values:
        return ""
    return ";".join(_cell(item) for item in values)


def _floors(floors: dict[str, float]) -> str:
    return ";".join(f"{sensor}={floor}" for sensor, floor in floors.items())


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_agent_log(alerts: dict, observations_path: Path, alerts_path: Path,
                     created_at: str | None = None) -> None:
    """Write agent-observations.csv and agent-alerts.csv for one agent run.

    ``alerts`` is the document written to agent-alerts.json: rule version,
    floors, deadline, and one entry per scenario.
    """
    stamped = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    rule_version = alerts["rule_version"]
    floors = _floors(alerts["floors_used"])
    deadline = _cell(alerts["deadline_s"])

    observations: list[dict[str, str]] = []
    alert_rows: list[dict[str, str]] = []
    for entry in alerts["scenarios"]:
        alert = entry["alert"]
        event_id = alert["event_id"]
        for sensor in alert["sensors"]:
            observations.append({
                "event_id": event_id,
                "sensor": _cell(sensor["sensor"]),
                "state": _cell(sensor["state"]),
                "prediction": _cell(sensor["prediction"]),
                "hypothesis": _cell(sensor["hypothesis"]),
                "score": _cell(sensor["score"]),
                "score_calibrated": _cell(sensor["score_calibrated"]),
                "model_version": _cell(sensor["model_version"]),
                "source_ref": _cell(sensor["source_ref"]),
                "arrival_s": _cell(sensor["arrival_s"]),
            })
        alert_rows.append({
            "event_id": event_id,
            "scenario": entry["scenario"],
            "status": _cell(alert["status"]),
            "leading_hypothesis": _cell(alert["leading_hypothesis"]),
            "reasons": _join(alert["reasons"]),
            "missing_sensors": _join(alert["missing_sensors"]),
            "delayed_sensors": _join(alert["delayed_sensors"]),
            "recommended_requests": _join(entry["recommended_requests"]),
            "rule_version": rule_version,
            "floors_used": floors,
            "deadline_s": deadline,
            "operator_disposition": "",
            "created_at": stamped,
        })

    _write_csv(Path(observations_path), OBSERVATION_FIELDS, observations)
    _write_csv(Path(alerts_path), ALERT_FIELDS, alert_rows)
