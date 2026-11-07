"""Agent interface: shared sensor observation, label mapping, alert schema, and status rules.

Plan row 10. This module defines what the coordination agent consumes and produces.
It may recommend which evidence to request next, but it cannot control sensors or
drones, schedule anything, or initiate a response, and it never calculates a fused
probability. Every alert requires human review; the schema rejects any alert that does not.
The status rule is passed in as a function so the evidence-combination step can be
replaced later (for example, by a model trained on synchronized recordings) without
changing the alert schema. See docs/agent-coordination.md.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence

try:  # imported as src.agent_interface (tests) or run from src/ (scripts)
    from .synthetic_replay import EvidenceStatus, SensorEvidence, SensorType
    from .replay_workflow import VerificationStatus
except ImportError:  # pragma: no cover
    from synthetic_replay import EvidenceStatus, SensorEvidence, SensorType
    from replay_workflow import VerificationStatus


class Hypothesis(str, Enum):
    """Common hypothesis each modality's label is mapped to for status rules only."""

    DRONE_LIKE = "drone_like"
    NOT_DRONE = "not_drone"
    OTHER = "other"
    UNCERTAIN = "uncertain"


DEFINITIVE = (Hypothesis.DRONE_LIKE, Hypothesis.NOT_DRONE)


class AlertStatus(str, Enum):
    CONFIRMED = "confirmed"
    CONFLICTING = "conflicting"
    UNKNOWN = "unknown"
    UNVERIFIED = "unverified"


class ObservationState(str, Enum):
    """Whether an observation can be used by the status rules."""

    USABLE = "usable"
    MISSING = "missing"
    DELAYED = "delayed"
    LOW_QUALITY = "low_quality"


# Source labels are normalized (lowercase, "-" and " " become "_") before lookup.
# Proposed mapping for team review in plan row 10; see docs/agent-coordination.md.
LABEL_MAP: dict[SensorType, dict[str, Hypothesis]] = {
    SensorType.RF: {
        "machine": Hypothesis.DRONE_LIKE,
        "benign": Hypothesis.NOT_DRONE,
        "human": Hypothesis.NOT_DRONE,
        "wildlife": Hypothesis.NOT_DRONE,
        "broadband_jam": Hypothesis.OTHER,
        "narrowband_jam": Hypothesis.OTHER,
        "uncertain": Hypothesis.UNCERTAIN,
    },
    SensorType.RADAR: {
        "drone": Hypothesis.DRONE_LIKE,
        "bird": Hypothesis.NOT_DRONE,
        "human": Hypothesis.NOT_DRONE,
    },
    SensorType.THERMAL: {
        "drone": Hypothesis.DRONE_LIKE,
        "bird": Hypothesis.NOT_DRONE,  # Dataset 2 labels drones and birds
        "no_drone": Hypothesis.NOT_DRONE,
    },
    SensorType.ACOUSTIC: {
        "drone": Hypothesis.DRONE_LIKE,
        "no_drone": Hypothesis.NOT_DRONE,
    },
}

# A score below a modality's floor maps to UNCERTAIN. These are development
# placeholders: final values must be chosen from validation outputs, never test.
DEFAULT_SCORE_FLOOR: dict[SensorType, float] = {
    SensorType.RF: 0.60,
    SensorType.RADAR: 0.60,
    SensorType.THERMAL: 0.60,
    SensorType.ACOUSTIC: 0.60,
}

# Only held-out test predictions may enter replay scenarios (matches the RF notebook's handoff check).
# Training and validation rows would leak; production rows are not part of replay.
HELD_OUT_SPLITS = frozenset({"test"})

# Order in which missing evidence is recommended: passive sensors first, then radar,
# then thermal verification. Development default; a strategy can pass its own order.
DEFAULT_REQUEST_ORDER: tuple[SensorType, ...] = (
    SensorType.ACOUSTIC, SensorType.RADAR, SensorType.THERMAL,
)

_STATE_FROM_EVIDENCE = {
    EvidenceStatus.AVAILABLE: ObservationState.USABLE,
    EvidenceStatus.MISSING: ObservationState.MISSING,
    EvidenceStatus.DELAYED: ObservationState.DELAYED,
    EvidenceStatus.LOW_QUALITY: ObservationState.LOW_QUALITY,
}

# Maps the radar-only replay contract onto the shared alert status.
VERIFICATION_TO_ALERT: dict[VerificationStatus, AlertStatus] = {
    VerificationStatus.CONFIRMED: AlertStatus.CONFIRMED,
    VerificationStatus.CONFLICTING: AlertStatus.CONFLICTING,
    VerificationStatus.PENDING: AlertStatus.UNVERIFIED,
    VerificationStatus.TIMEOUT: AlertStatus.UNVERIFIED,
    VerificationStatus.UNAVAILABLE: AlertStatus.UNVERIFIED,
}


def normalize_label(label: str) -> str:
    return label.strip().lower().replace("-", "_").replace(" ", "_")


def map_label(sensor: SensorType, label: str) -> Hypothesis:
    """Map a source label to the common hypothesis; unknown labels raise."""
    key = normalize_label(label)
    try:
        return LABEL_MAP[sensor][key]
    except KeyError as exc:
        raise ValueError(f"no mapping for {sensor.value} label {label!r}") from exc


@dataclass(frozen=True)
class AgentObservation:
    """One sensor record as the agent sees it: the replay evidence plus arrival and calibration."""

    evidence: SensorEvidence
    arrival_s: float | None  # seconds after the event opened; None if never received
    score_calibrated: bool = False

    def __post_init__(self) -> None:
        if self.arrival_s is not None and self.arrival_s < 0:
            raise ValueError("arrival_s cannot be negative")
        if self.evidence.status == EvidenceStatus.AVAILABLE and self.arrival_s is None:
            raise ValueError("available evidence requires an arrival time")
        score = self.evidence.score
        # NaN would slip past the score floor (every comparison with NaN is False).
        if score is not None and not (math.isfinite(score) and 0.0 <= score <= 1.0):
            raise ValueError(f"score must be a finite value in [0, 1], got {score!r}")

    @property
    def sensor(self) -> SensorType:
        return self.evidence.sensor_type

    def state(self, deadline_s: float) -> ObservationState:
        state = _STATE_FROM_EVIDENCE[self.evidence.status]
        if state == ObservationState.USABLE and self.arrival_s is not None and self.arrival_s > deadline_s:
            return ObservationState.DELAYED
        return state

    def hypothesis(self, score_floor: Mapping[SensorType, float] = DEFAULT_SCORE_FLOOR) -> Hypothesis | None:
        """Hypothesis for a usable record, or None when the record has no prediction."""
        if self.evidence.prediction is None:
            return None
        mapped = map_label(self.sensor, self.evidence.prediction)
        score = self.evidence.score
        if mapped in DEFINITIVE and score is not None and score < score_floor.get(self.sensor, 0.0):
            return Hypothesis.UNCERTAIN
        return mapped


def observation_from_handoff(row: Mapping[str, str], event_id: str, event_timestamp: str,
                             arrival_s: float) -> AgentObservation:
    """Build an observation from one validated model-output handoff row (docs/model-output-handoff.md)."""
    split = str(row.get("split", "")).strip().lower()
    if split not in HELD_OUT_SPLITS:
        raise ValueError(
            f"handoff row {row.get('output_id')!r} is not held-out (split={row.get('split')!r}); "
            f"allowed: {sorted(HELD_OUT_SPLITS)}"
        )
    calibrated = "calibrated_score" in row and str(row["calibrated_score"]).strip() != ""
    score = float(row["calibrated_score"] if calibrated else row["score"])
    evidence = SensorEvidence(
        event_id=event_id,
        timestamp=event_timestamp,
        sensor_type=SensorType(row["sensor_type"]),
        status=EvidenceStatus.AVAILABLE,
        prediction=row["predicted_label"],
        score=score,
        model_version=row["model_version"],
        source_ref=f'{row["source_output_ref"]}#{row["output_id"]}',
    )
    return AgentObservation(evidence, arrival_s, score_calibrated=calibrated)


@dataclass(frozen=True)
class SensorSummary:
    sensor: str
    state: str
    prediction: str | None
    hypothesis: str | None
    score: float | None
    score_calibrated: bool
    model_version: str
    source_ref: str
    placeholder_value: bool
    arrival_s: float | None


@dataclass(frozen=True)
class Alert:
    """Structured alert for operator review. It is never an autonomous decision."""

    event_id: str
    status: AlertStatus
    leading_hypothesis: Hypothesis | None
    reasons: tuple[str, ...]
    sensors: tuple[SensorSummary, ...]
    missing_sensors: tuple[str, ...]
    delayed_sensors: tuple[str, ...]
    deadline_s: float
    simulated: bool = True
    review_required: bool = True
    operator_disposition: str | None = None
    notes: tuple[str, ...] = field(default=(
        "No fused detection probability is calculated.",
        "Scores are raw model outputs unless score_calibrated is true.",
    ))

    def __post_init__(self) -> None:
        if not self.review_required:
            raise ValueError("every alert requires operator review")
        if not self.simulated:
            raise ValueError("the current datasets are unsynchronized; alerts must be marked simulated")


def decide_status(observations: Iterable[AgentObservation], expected: Iterable[SensorType],
                  deadline_s: float,
                  score_floor: Mapping[SensorType, float] = DEFAULT_SCORE_FLOOR,
                  ) -> tuple[AlertStatus, Hypothesis | None, tuple[str, ...]]:
    """Apply the status rules (docs/agent-coordination.md) in priority order.

    1. conflicting: usable modalities disagree between drone_like and not_drone.
    2. confirmed: at least two usable modalities share one definitive hypothesis.
    3. unverified: an expected modality is missing, delayed, or low quality.
    4. unknown: everything else (all uncertain/other, or a single supporting modality).
    """
    by_sensor = {item.sensor: item for item in observations}
    expected = tuple(expected)
    gaps: list[str] = []
    votes: dict[Hypothesis, list[str]] = {}
    for sensor in expected:
        item = by_sensor.get(sensor)
        state = ObservationState.MISSING if item is None else item.state(deadline_s)
        if state != ObservationState.USABLE:
            gaps.append(f"{sensor.value}_{state.value}")
            continue
        hypothesis = item.hypothesis(score_floor)
        if hypothesis is not None:
            votes.setdefault(hypothesis, []).append(sensor.value)

    drone = votes.get(Hypothesis.DRONE_LIKE, [])
    not_drone = votes.get(Hypothesis.NOT_DRONE, [])
    reasons = [f"{h.value}:{','.join(s)}" for h, s in sorted(votes.items(), key=lambda kv: kv[0].value)]

    if drone and not_drone:
        return AlertStatus.CONFLICTING, None, tuple(reasons + gaps)
    for hypothesis, supporters in ((Hypothesis.DRONE_LIKE, drone), (Hypothesis.NOT_DRONE, not_drone)):
        if len(supporters) >= 2:
            return AlertStatus.CONFIRMED, hypothesis, tuple(reasons + gaps)
    leading = Hypothesis.DRONE_LIKE if drone else Hypothesis.NOT_DRONE if not_drone else None
    if gaps:
        return AlertStatus.UNVERIFIED, leading, tuple(reasons + gaps)
    note = ["single_modality_support"] if leading else ["no_definitive_evidence"]
    return AlertStatus.UNKNOWN, leading, tuple(reasons + note)


StatusRule = Callable[
    [Iterable[AgentObservation], Iterable[SensorType], float, Mapping[SensorType, float]],
    tuple[AlertStatus, Hypothesis | None, tuple[str, ...]],
]


def recommend_requests(observations: Iterable[AgentObservation], expected: Iterable[SensorType],
                       deadline_s: float,
                       score_floor: Mapping[SensorType, float] = DEFAULT_SCORE_FLOOR,
                       order: Sequence[SensorType] = DEFAULT_REQUEST_ORDER,
                       status_rule: StatusRule = decide_status) -> tuple[SensorType, ...]:
    """Recommend which expected sensors to request next. Advisory only: nothing is triggered.

    No request is made once the event is confirmed or conflicting (conflicts go to the operator).
    Otherwise every expected sensor without usable evidence is listed in ``order``.
    """
    observations = tuple(observations)
    expected = tuple(expected)
    status, _, _ = status_rule(observations, expected, deadline_s, score_floor)
    if status in (AlertStatus.CONFIRMED, AlertStatus.CONFLICTING):
        return ()
    by_sensor = {item.sensor: item for item in observations}
    needed = [s for s in expected
              if s not in by_sensor or by_sensor[s].state(deadline_s) != ObservationState.USABLE]
    ranked = [s for s in order if s in needed] + [s for s in needed if s not in order]
    return tuple(ranked)


def build_alert(event_id: str, observations: Iterable[AgentObservation], expected: Iterable[SensorType],
                deadline_s: float, score_floor: Mapping[SensorType, float] = DEFAULT_SCORE_FLOOR,
                status_rule: StatusRule = decide_status) -> Alert:
    observations = tuple(observations)
    expected = tuple(expected)
    if any(item.evidence.event_id != event_id for item in observations):
        raise ValueError("all observations must share the alert's event ID")
    sensors_seen = [item.sensor for item in observations]
    if len(sensors_seen) != len(set(sensors_seen)):
        raise ValueError("an alert accepts only one observation per sensor")
    unexpected = sorted(s.value for s in set(sensors_seen) - set(expected))
    if unexpected:
        raise ValueError(f"observations from unexpected sensors would be dropped: {unexpected}")

    status, leading, reasons = status_rule(observations, expected, deadline_s, score_floor)
    by_sensor = {item.sensor: item for item in observations}
    summaries, missing, delayed = [], [], []
    for sensor in expected:
        item = by_sensor.get(sensor)
        if item is None:
            missing.append(sensor.value)
            continue
        state = item.state(deadline_s)
        if state == ObservationState.MISSING:
            missing.append(sensor.value)
        elif state == ObservationState.DELAYED:
            delayed.append(sensor.value)
        hypothesis = item.hypothesis(score_floor) if state == ObservationState.USABLE else None
        ev = item.evidence
        summaries.append(SensorSummary(
            sensor.value, state.value, ev.prediction, hypothesis.value if hypothesis else None, ev.score,
            item.score_calibrated, ev.model_version, ev.source_ref, ev.placeholder_value, item.arrival_s,
        ))
    return Alert(event_id, status, leading, reasons, tuple(summaries), tuple(missing), tuple(delayed), deadline_s)


def to_dict(alert: Alert) -> dict[str, Any]:
    data = asdict(alert)
    data["status"] = alert.status.value
    data["leading_hypothesis"] = alert.leading_hypothesis.value if alert.leading_hypothesis else None
    return data
