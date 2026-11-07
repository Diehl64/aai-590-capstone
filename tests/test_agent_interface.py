import json
import unittest

from src.agent_interface import (
    Alert, AlertStatus, AgentObservation, Hypothesis, VERIFICATION_TO_ALERT, build_alert, map_label,
    observation_from_handoff, recommend_requests, to_dict,
)
from src.replay_workflow import VerificationStatus
from src.synthetic_replay import EvidenceStatus, SensorEvidence, SensorType

ALL = (SensorType.RF, SensorType.RADAR, SensorType.THERMAL, SensorType.ACOUSTIC)
DEADLINE = 10.0


def obs(sensor, prediction, score, arrival=1.0, status=EvidenceStatus.AVAILABLE, event="sim-1"):
    evidence = SensorEvidence(event, "2026-11-16T18:00:00Z", sensor, status, prediction, score,
                              f"{sensor.value}-test", f"{sensor.value}://test", True)
    return AgentObservation(evidence, arrival)


class LabelMappingTests(unittest.TestCase):
    def test_each_modality_maps_its_own_labels(self):
        self.assertEqual(map_label(SensorType.RF, "Machine"), Hypothesis.DRONE_LIKE)
        self.assertEqual(map_label(SensorType.RF, "Broadband_Jam"), Hypothesis.OTHER)
        self.assertEqual(map_label(SensorType.RADAR, "bird"), Hypothesis.NOT_DRONE)
        self.assertEqual(map_label(SensorType.ACOUSTIC, "no-drone"), Hypothesis.NOT_DRONE)
        self.assertEqual(map_label(SensorType.THERMAL, "no drone"), Hypothesis.NOT_DRONE)
        self.assertEqual(map_label(SensorType.THERMAL, "Bird"), Hypothesis.NOT_DRONE)

    def test_unknown_label_is_rejected_not_guessed(self):
        with self.assertRaisesRegex(ValueError, "no mapping"):
            map_label(SensorType.RADAR, "corner_reflector")

    def test_low_score_becomes_uncertain(self):
        self.assertEqual(obs(SensorType.RF, "machine", .55).hypothesis(), Hypothesis.UNCERTAIN)
        self.assertEqual(obs(SensorType.RF, "machine", .75).hypothesis(), Hypothesis.DRONE_LIKE)

    def test_score_at_floor_is_definitive(self):
        self.assertEqual(obs(SensorType.RF, "machine", .60).hypothesis(), Hypothesis.DRONE_LIKE)

    def test_invalid_scores_are_rejected(self):
        for bad in (float("nan"), float("inf"), -0.1, 1.5, 7.0):
            with self.subTest(score=bad), self.assertRaisesRegex(ValueError, "score must"):
                obs(SensorType.RF, "machine", bad)


class StatusRuleTests(unittest.TestCase):
    def test_two_supporting_modalities_confirm(self):
        alert = build_alert("sim-1", [
            obs(SensorType.RF, "machine", .72), obs(SensorType.RADAR, "drone", .91),
            obs(SensorType.THERMAL, "drone", .88), obs(SensorType.ACOUSTIC, "drone", .93),
        ], ALL, DEADLINE)
        self.assertEqual(alert.status, AlertStatus.CONFIRMED)
        self.assertEqual(alert.leading_hypothesis, Hypothesis.DRONE_LIKE)

    def test_disagreement_is_conflicting_even_with_majority(self):
        alert = build_alert("sim-1", [
            obs(SensorType.RF, "benign", .76), obs(SensorType.RADAR, "drone", .82),
            obs(SensorType.THERMAL, "no_drone", .79), obs(SensorType.ACOUSTIC, "drone", .89),
        ], ALL, DEADLINE)
        self.assertEqual(alert.status, AlertStatus.CONFLICTING)
        self.assertIsNone(alert.leading_hypothesis)

    def test_conflict_outranks_missing_evidence(self):
        alert = build_alert("sim-1", [
            obs(SensorType.RADAR, "drone", .9), obs(SensorType.ACOUSTIC, "no_drone", .9),
        ], ALL, DEADLINE)
        self.assertEqual(alert.status, AlertStatus.CONFLICTING)
        self.assertEqual(set(alert.missing_sensors), {"rf", "thermal"})

    def test_single_support_with_gap_is_unverified(self):
        alert = build_alert("sim-1", [
            obs(SensorType.RF, "machine", .55), obs(SensorType.RADAR, "drone", .84),
            obs(SensorType.THERMAL, None, None, None, EvidenceStatus.MISSING),
        ], ALL, DEADLINE)
        self.assertEqual(alert.status, AlertStatus.UNVERIFIED)
        self.assertEqual(alert.leading_hypothesis, Hypothesis.DRONE_LIKE)
        self.assertIn("thermal_missing", alert.reasons)

    def test_late_arrival_counts_as_delayed_not_usable(self):
        alert = build_alert("sim-1", [
            obs(SensorType.RADAR, "drone", .9), obs(SensorType.ACOUSTIC, "drone", .9, arrival=12.0),
        ], (SensorType.RADAR, SensorType.ACOUSTIC), DEADLINE)
        self.assertEqual(alert.status, AlertStatus.UNVERIFIED)
        self.assertEqual(alert.delayed_sensors, ("acoustic",))

    def test_all_uncertain_is_unknown(self):
        alert = build_alert("sim-1", [
            obs(SensorType.RF, "machine", .5), obs(SensorType.RADAR, "drone", .4),
        ], (SensorType.RF, SensorType.RADAR), DEADLINE)
        self.assertEqual(alert.status, AlertStatus.UNKNOWN)
        self.assertIn("no_definitive_evidence", alert.reasons)

    def test_non_drone_agreement_is_confirmed_non_drone_and_still_reviewed(self):
        alert = build_alert("sim-5", [
            obs(SensorType.RF, "human", .7, event="sim-5"), obs(SensorType.RADAR, "human", .8, event="sim-5"),
            obs(SensorType.THERMAL, "no_drone", .8, event="sim-5"), obs(SensorType.ACOUSTIC, "no_drone", .9, event="sim-5"),
        ], ALL, DEADLINE)
        self.assertEqual(alert.status, AlertStatus.CONFIRMED)
        self.assertEqual(alert.leading_hypothesis, Hypothesis.NOT_DRONE)
        self.assertTrue(alert.review_required)


class AlertSchemaTests(unittest.TestCase):
    def test_alert_cannot_skip_review(self):
        with self.assertRaisesRegex(ValueError, "operator review"):
            Alert("sim-1", AlertStatus.CONFIRMED, None, (), (), (), (), DEADLINE, review_required=False)

    def test_alert_cannot_claim_real_data(self):
        with self.assertRaisesRegex(ValueError, "simulated"):
            Alert("sim-1", AlertStatus.CONFIRMED, None, (), (), (), (), DEADLINE, simulated=False)

    def test_rejects_mixed_events(self):
        with self.assertRaisesRegex(ValueError, "event ID"):
            build_alert("sim-1", [obs(SensorType.RADAR, "drone", .9, event="sim-2")], ALL, DEADLINE)

    def test_rejects_two_observations_from_one_sensor(self):
        with self.assertRaisesRegex(ValueError, "one observation per sensor"):
            build_alert("sim-1", [obs(SensorType.RADAR, "drone", .9), obs(SensorType.RADAR, "bird", .8)],
                        ALL, DEADLINE)

    def test_rejects_unexpected_sensor_instead_of_dropping_it(self):
        with self.assertRaisesRegex(ValueError, "unexpected sensors"):
            build_alert("sim-1", [obs(SensorType.RADAR, "drone", .9), obs(SensorType.ACOUSTIC, "drone", .9)],
                        (SensorType.RADAR,), DEADLINE)

    def test_status_rule_can_be_replaced(self):
        def always_unknown(observations, expected, deadline_s, score_floor):
            return AlertStatus.UNKNOWN, None, ("custom_rule",)
        alert = build_alert("sim-1", [obs(SensorType.RADAR, "drone", .9), obs(SensorType.ACOUSTIC, "drone", .9)],
                            (SensorType.RADAR, SensorType.ACOUSTIC), DEADLINE, status_rule=always_unknown)
        self.assertEqual(alert.status, AlertStatus.UNKNOWN)
        self.assertEqual(alert.reasons, ("custom_rule",))
        self.assertTrue(alert.review_required)

    def test_alert_serializes_to_json(self):
        alert = build_alert("sim-1", [obs(SensorType.RADAR, "drone", .9)], ALL, DEADLINE)
        data = json.loads(json.dumps(to_dict(alert)))
        self.assertEqual(data["status"], "unverified")
        self.assertTrue(data["review_required"])
        self.assertNotIn("fused_probability", data)

    def test_existing_verification_states_map_to_alert_status(self):
        self.assertEqual(VERIFICATION_TO_ALERT[VerificationStatus.TIMEOUT], AlertStatus.UNVERIFIED)
        self.assertEqual(len(VERIFICATION_TO_ALERT), len(VerificationStatus))


class RequestRecommendationTests(unittest.TestCase):
    def test_uncertain_rf_asks_for_acoustic_then_radar(self):
        observations = [obs(SensorType.RF, "machine", .55)]
        self.assertEqual(
            recommend_requests(observations, ALL, DEADLINE),
            (SensorType.ACOUSTIC, SensorType.RADAR, SensorType.THERMAL),
        )

    def test_delayed_sensor_is_requested_again(self):
        observations = [obs(SensorType.RF, "machine", .8), obs(SensorType.ACOUSTIC, "drone", .9, arrival=12.0)]
        self.assertEqual(recommend_requests(observations, (SensorType.RF, SensorType.ACOUSTIC), DEADLINE),
                         (SensorType.ACOUSTIC,))

    def test_no_request_once_confirmed(self):
        observations = [obs(SensorType.RF, "machine", .8), obs(SensorType.ACOUSTIC, "drone", .9)]
        self.assertEqual(recommend_requests(observations, ALL, DEADLINE), ())

    def test_conflict_goes_to_operator_not_more_sensors(self):
        observations = [obs(SensorType.RF, "benign", .8), obs(SensorType.ACOUSTIC, "drone", .9)]
        self.assertEqual(recommend_requests(observations, ALL, DEADLINE), ())


class HandoffAdapterTests(unittest.TestCase):
    ROW = {
        "output_id": "radar-test-001", "sensor_type": "radar", "source_observation_id": "m1-s2", "split": "test",
        "timestamp": "relative_seconds:1.2", "predicted_label": "drone", "score": "0.91",
        "model_version": "radar-cnn-v1", "dataset_id": "kth_77ghz_v2", "source_output_ref": "radar-test-outputs.csv",
    }

    def test_raw_score_is_marked_uncalibrated(self):
        item = observation_from_handoff(self.ROW, "sim-1", "2026-11-16T18:00:00Z", 2.0)
        self.assertFalse(item.score_calibrated)
        self.assertEqual(item.evidence.score, .91)
        self.assertEqual(item.evidence.source_ref, "radar-test-outputs.csv#radar-test-001")

    def test_calibrated_score_is_used_when_present(self):
        row = dict(self.ROW, calibrated_score="0.83")
        item = observation_from_handoff(row, "sim-1", "2026-11-16T18:00:00Z", 2.0)
        self.assertTrue(item.score_calibrated)
        self.assertEqual(item.evidence.score, .83)

    def test_non_test_rows_are_rejected(self):
        for split in ("train", "validation", "production", ""):
            with self.subTest(split=split), self.assertRaisesRegex(ValueError, "not held-out"):
                observation_from_handoff(dict(self.ROW, split=split), "sim-1", "2026-11-16T18:00:00Z", 2.0)


if __name__ == "__main__":
    unittest.main()
