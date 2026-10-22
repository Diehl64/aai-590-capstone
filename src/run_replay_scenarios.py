#!/usr/bin/env python3
"""Run deterministic simulated replay cases for the local review contract."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from replay_workflow import RadarResult, VerificationResult, VerificationStatus, create_review, to_dict

def scenarios():
    radar = RadarResult("event-001", "measurement-42-segment-7", "drone", {"drone": .91, "bird": .06, "human": .03}, "RadarCNN-cuda-590", "2026-10-22T20:00:00Z")
    return {
        "agreement": (radar, VerificationResult(radar.event_id, VerificationStatus.CONFIRMED, "simulated-rgb-001", "drone"), "accepted"),
        "conflict": (radar, VerificationResult(radar.event_id, VerificationStatus.CONFLICTING, "simulated-rgb-002", "bird", "simulated evidence disagrees"), "required"),
        "timeout": (radar, VerificationResult(radar.event_id, VerificationStatus.TIMEOUT, reason="verification deadline elapsed"), "required"),
        "unavailable": (radar, None, "required"),
    }

def main():
    p = argparse.ArgumentParser(); p.add_argument("--output", type=Path, default=Path("results/replay-scenarios")); a = p.parse_args(); records = []
    for name, (radar, verification, expected) in scenarios().items():
        record = create_review(radar, verification); actual = record.review_status.value
        if actual != expected: raise AssertionError(f"{name}: expected {expected}, got {actual}")
        records.append({"scenario": name, "simulated": True, "expected_review_status": expected, "record": to_dict(record)})
    result = {"workflow": "local_replay_operator_review", "simulated_only": True, "scenarios": records}
    a.output.mkdir(parents=True, exist_ok=True); (a.output / "replay-scenarios.json").write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2))

if __name__ == "__main__": main()
