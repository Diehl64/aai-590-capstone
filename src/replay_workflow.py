"""Local replay contract for radar evidence and human review.

This module models orchestration only. Verification records may be simulated
or unavailable; no RGB pairing, location, or calibrated probability is inferred.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

class VerificationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CONFLICTING = "conflicting"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"

class ReviewStatus(str, Enum):
    REQUIRED = "required"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEFERRED = "deferred"

@dataclass(frozen=True)
class RadarResult:
    event_id: str
    observation_id: str
    predicted_class: str
    scores: dict[str, float]
    model_version: str
    timestamp: str

@dataclass(frozen=True)
class VerificationResult:
    event_id: str
    status: VerificationStatus
    evidence_ref: str | None = None
    predicted_class: str | None = None
    reason: str | None = None

@dataclass(frozen=True)
class ReviewRecord:
    event_id: str
    verification_status: VerificationStatus
    review_status: ReviewStatus
    reason: str
    radar: RadarResult
    verification: VerificationResult | None = None

def create_review(radar: RadarResult, verification: VerificationResult | None = None) -> ReviewRecord:
    if verification is None:
        return ReviewRecord(radar.event_id, VerificationStatus.PENDING, ReviewStatus.REQUIRED, "verification_not_received", radar)
    if verification.event_id != radar.event_id:
        raise ValueError("radar and verification event IDs must match")
    if verification.status == VerificationStatus.CONFIRMED and verification.predicted_class == radar.predicted_class:
        status, reason = ReviewStatus.ACCEPTED, "modalities_agree"
    elif verification.status in (VerificationStatus.CONFLICTING, VerificationStatus.TIMEOUT, VerificationStatus.UNAVAILABLE):
        status, reason = ReviewStatus.REQUIRED, verification.status.value
    else:
        status, reason = ReviewStatus.REQUIRED, "insufficient_verification_evidence"
    return ReviewRecord(radar.event_id, verification.status, status, reason, radar, verification)

def to_dict(record: ReviewRecord) -> dict[str, Any]:
    return asdict(record)
