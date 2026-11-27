import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.agent_log import ALERT_FIELDS, OBSERVATION_FIELDS, write_agent_log
from src.run_agent_comparison import COMPARISON_FIELDS, write_fixed_vs_cascade
from src.run_agent_replay import DEFAULT_DEADLINE_S, run_replay, write_alerts


FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "agent-replay-fixture.json"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return tuple(reader.fieldnames), list(reader)


class AgentReplayTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.tmp = TemporaryDirectory()
        self.output = Path(self.tmp.name)
        self.result = run_replay(FIXTURE, DEFAULT_DEADLINE_S)
        write_alerts(self.result, self.output)
        write_agent_log(
            self.result,
            self.output / "agent-observations.csv",
            self.output / "agent-alerts.csv",
        )
        write_fixed_vs_cascade(FIXTURE, self.output, DEFAULT_DEADLINE_S)
        self.written = json.loads((self.output / "agent-alerts.json").read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def entry(self, name):
        for item in self.written["scenarios"]:
            if item["scenario"] == name:
                return item
        self.fail(f"missing scenario {name}")

    def test_every_alert_is_simulated_and_requires_review(self):
        self.assertEqual(len(self.written["scenarios"]), len(self.fixture["scenarios"]))
        for item in self.written["scenarios"]:
            self.assertTrue(item["alert"]["simulated"])
            self.assertTrue(item["alert"]["review_required"])

    def test_all_four_drone_like_is_confirmed(self):
        self.assertEqual(self.entry("all_four_drone_like")["alert"]["status"], "confirmed")

    def test_rf_false_alarm_is_conflicting(self):
        self.assertEqual(self.entry("rf_false_alarm")["alert"]["status"], "conflicting")

    def test_missing_sensor_is_unverified_and_requested(self):
        item = self.entry("rf_only")
        self.assertEqual(item["alert"]["status"], "unverified")
        missing = item["alert"]["missing_sensors"]
        self.assertTrue(missing)
        for sensor in missing:
            self.assertIn(sensor, item["recommended_requests"])

    def test_delayed_sensor_is_unverified_and_requested(self):
        item = self.entry("acoustic_delayed_radar_low_quality")
        self.assertEqual(item["alert"]["status"], "unverified")
        delayed = item["alert"]["delayed_sensors"]
        self.assertTrue(delayed)
        for sensor in delayed:
            self.assertIn(sensor, item["recommended_requests"])

    def test_decision_log_joins_on_event_id(self):
        observation_fields, observations = read_csv(self.output / "agent-observations.csv")
        alert_fields, alerts = read_csv(self.output / "agent-alerts.csv")
        evidence_rows = sum(len(item["record"]["evidence"]) for item in self.fixture["scenarios"])
        self.assertEqual(observation_fields, OBSERVATION_FIELDS)
        self.assertEqual(alert_fields, ALERT_FIELDS)
        self.assertEqual(len(observations), evidence_rows)
        self.assertEqual(len(alerts), len(self.fixture["scenarios"]))
        alert_ids = {row["event_id"] for row in alerts}
        self.assertTrue(all(row["event_id"] in alert_ids for row in observations))

    def test_cascade_never_uses_more_sensors_than_the_fixed_rule(self):
        fields, rows = read_csv(self.output / "fixed-vs-cascade.csv")
        self.assertEqual(fields, COMPARISON_FIELDS)
        self.assertEqual(len(rows), len(self.fixture["scenarios"]))
        for row in rows:
            self.assertLessEqual(int(row["cascade_sensors_used"]), int(row["fixed_sensors_used"]))


    def comparison(self, name):
        _, rows = read_csv(self.output / "fixed-vs-cascade.csv")
        for row in rows:
            if row["scenario"] == name:
                return row
        self.fail(f"missing comparison row {name}")

    def test_early_confirmation_that_masks_a_conflict_is_flagged(self):
        row = self.comparison("early_confirmation_masks_radar_conflict")
        self.assertEqual(row["cascade_status"], "confirmed")
        self.assertEqual(row["fixed_status"], "conflicting")
        self.assertEqual(row["cascade_revealed_sensors"], "rf;acoustic")
        self.assertEqual(row["cascade_unrevealed_sensors"], "radar;thermal")
        self.assertEqual(row["unrevealed_disagreeing_sensors"], "radar")
        self.assertEqual(row["early_stop_masks_conflict"], "true")

    def test_agreeing_unrevealed_sensors_are_not_flagged(self):
        row = self.comparison("all_four_drone_like")
        self.assertEqual(row["cascade_unrevealed_sensors"], "radar;thermal")
        self.assertEqual(row["unrevealed_disagreeing_sensors"], "")
        self.assertEqual(row["early_stop_masks_conflict"], "false")

    def test_a_masked_conflict_always_names_the_hidden_sensor(self):
        _, rows = read_csv(self.output / "fixed-vs-cascade.csv")
        for row in rows:
            revealed = set(filter(None, row["cascade_revealed_sensors"].split(";")))
            unrevealed = set(filter(None, row["cascade_unrevealed_sensors"].split(";")))
            self.assertFalse(revealed & unrevealed)
            self.assertEqual(len(revealed), int(row["cascade_sensors_used"]))
            if row["early_stop_masks_conflict"] == "true":
                self.assertTrue(row["unrevealed_disagreeing_sensors"])
            if not unrevealed:
                self.assertEqual(row["cascade_status"], row["fixed_status"])


class HandoffScoreTests(unittest.TestCase):
    def test_rf_floor_uses_calibrated_score_when_raw_score_is_below_it(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            handoff = root / "rf-test.csv"
            handoff.write_text(
                "output_id,sensor_type,source_observation_id,split,timestamp,predicted_label,"
                "score,model_version,dataset_id,source_output_ref,calibrated_score\n"
                "rf-low-raw,rf,image.png,test,source-time-unavailable,Machine,"
                "0.40,rf-v5,rf_intrusion,rf-test.csv,0.50\n",
                encoding="utf-8",
            )
            replay = root / "replay.json"
            evidence = []
            for sensor, status, prediction, score, source_ref in (
                ("rf", "available", "Machine", 0.40,
                 "rf-test.csv#output_id=rf-low-raw;source_timestamp=source-time-unavailable"),
                ("acoustic", "missing", None, None, "not-provided"),
                ("radar", "missing", None, None, "not-provided"),
                ("thermal", "missing", None, None, "not-provided"),
            ):
                evidence.append({
                    "event_id": "sim-score-001",
                    "timestamp": "simulated-event:sim-score-001",
                    "sensor_type": sensor,
                    "status": status,
                    "prediction": prediction,
                    "score": score,
                    "model_version": "fixture" if prediction else "not-provided",
                    "source_ref": source_ref,
                    "placeholder_value": False,
                })
            replay.write_text(json.dumps({
                "input_files": {"rf": str(handoff)},
                "scenarios": [{
                    "scenario": "rf_raw_below_floor",
                    "record": {
                        "event_id": "sim-score-001",
                        "timestamp": "simulated-event:sim-score-001",
                        "evidence": evidence,
                        "simulated": True,
                        "review_required": True,
                    },
                }],
            }), encoding="utf-8")
            result = run_replay(replay, DEFAULT_DEADLINE_S)
            rf = result["scenarios"][0]["alert"]["sensors"][0]
            self.assertEqual(result["score_types"]["rf"], "calibrated_score")
            self.assertEqual(rf["score"], 0.50)
            self.assertTrue(rf["score_calibrated"])
            self.assertEqual(rf["hypothesis"], "drone_like")


if __name__ == "__main__":
    unittest.main()
