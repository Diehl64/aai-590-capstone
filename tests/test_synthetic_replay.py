import unittest

from src.synthetic_replay import EvidenceStatus, SensorEvidence, SensorType, create_scenario


class SyntheticReplayTests(unittest.TestCase):
    def test_scenario_requires_human_review(self):
        scenario = create_scenario([
            SensorEvidence("event-1", "2026-11-16T18:00:00Z", SensorType.RF, EvidenceStatus.AVAILABLE, "machine", .7, "rf-v5", "rf://test"),
            SensorEvidence("event-1", "2026-11-16T18:00:00Z", SensorType.RADAR, EvidenceStatus.AVAILABLE, "drone", .9, "radar-v1", "radar://test"),
            SensorEvidence("event-1", "2026-11-16T18:00:00Z", SensorType.ACOUSTIC, EvidenceStatus.AVAILABLE, "drone", .9, "acoustic-v1", "acoustic://test"),
        ])
        self.assertTrue(scenario.simulated)
        self.assertTrue(scenario.review_required)
        self.assertEqual(len(scenario.evidence), 3)

    def test_scenario_rejects_mismatched_event(self):
        records = [
            SensorEvidence("event-1", "2026-11-16T18:00:00Z", SensorType.RF, EvidenceStatus.AVAILABLE, "machine", .7, "rf-v5", "rf://test"),
            SensorEvidence("event-2", "2026-11-16T18:00:00Z", SensorType.RADAR, EvidenceStatus.AVAILABLE, "drone", .9, "radar-v1", "radar://test"),
        ]
        with self.assertRaisesRegex(ValueError, "event ID"):
            create_scenario(records)

    def test_missing_evidence_can_have_no_prediction(self):
        record = SensorEvidence("event-1", "2026-11-16T18:00:00Z", SensorType.THERMAL, EvidenceStatus.MISSING, None, None, "thermal-v1", "thermal://missing")
        self.assertIsNone(record.prediction)


if __name__ == "__main__":
    unittest.main()
