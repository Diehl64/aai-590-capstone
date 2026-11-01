"""Contracts for explicitly simulated RF, radar, and thermal replay events.

This module combines evidence records for operator review. It does not calculate
a fused probability or establish performance on paired real-world observations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class SensorType(str, Enum):
    RF = "rf"
    RADAR = "radar"
    THERMAL = "thermal"


class EvidenceStatus(str, Enum):
    AVAILABLE = "available"
    MISSING = "missing"
    DELAYED = "delayed"
    LOW_QUALITY = "low_quality"


@dataclass(frozen=True)
class SensorEvidence:
    """One sensor result assigned to an explicitly simulated event."""

    event_id: str
    timestamp: str
    sensor_type: SensorType
    status: EvidenceStatus
    prediction: str | None
    score: float | None
    model_version: str
    source_ref: str
    placeholder_value: bool = False

    def __post_init__(self) -> None:
        if self.status == EvidenceStatus.AVAILABLE and self.prediction is None:
            raise ValueError("available evidence requires a prediction")
        if self.score is not None and not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between zero and one")


@dataclass(frozen=True)
class SyntheticScenario:
    """A same-timestamp comparison record for human review."""

    event_id: str
    timestamp: str
    evidence: tuple[SensorEvidence, ...]
    simulated: bool = True
    review_required: bool = True
    review_reason: str = "simulated_evidence_requires_human_review"


def create_scenario(evidence: list[SensorEvidence]) -> SyntheticScenario:
    """Validate and assemble a simulated event from separate model outputs."""
    if not evidence:
        raise ValueError("a scenario needs at least one evidence record")
    event_ids = {item.event_id for item in evidence}
    timestamps = {item.timestamp for item in evidence}
    sensor_types = [item.sensor_type for item in evidence]
    if len(event_ids) != 1:
        raise ValueError("all evidence records must share an event ID")
    if len(timestamps) != 1:
        raise ValueError("all evidence records must share a timestamp")
    if len(sensor_types) != len(set(sensor_types)):
        raise ValueError("a scenario accepts only one record per sensor type")
    return SyntheticScenario(event_ids.pop(), timestamps.pop(), tuple(evidence))


def to_dict(scenario: SyntheticScenario) -> dict[str, Any]:
    return asdict(scenario)
