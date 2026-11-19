import csv
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import run_real_output_replay as replay

COLUMNS = [
    "output_id",
    "sensor_type",
    "source_observation_id",
    "split",
    "timestamp",
    "predicted_label",
    "score",
    "model_version",
    "dataset_id",
    "source_output_ref",
]


class RealOutputReplayTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write_csv(self, name, rows):
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def row(self, **updates):
        base = {
            "output_id": "row-1",
            "sensor_type": "radar",
            "source_observation_id": "measurement-1",
            "split": "test",
            "timestamp": "source-time-unavailable",
            "predicted_label": "drone",
            "score": "0.90",
            "model_version": "fixture",
            "dataset_id": "fixture",
            "source_output_ref": "fixture.csv",
        }
        base.update(updates)
        return base

    def fixture_csvs(self):
        radar = self.write_csv("radar.csv", [
            self.row(output_id="radar-drone", sensor_type="radar", predicted_label="drone"),
            self.row(output_id="radar-bird", sensor_type="radar", predicted_label="bird", source_observation_id="measurement-2"),
            self.row(output_id="radar-human", sensor_type="radar", predicted_label="human", source_observation_id="measurement-3"),
        ])
        thermal = self.write_csv("thermal.csv", [
            self.row(output_id="thermal-drone", sensor_type="thermal", predicted_label="drone"),
            self.row(output_id="thermal-none", sensor_type="thermal", predicted_label="no_drone", source_observation_id="frame-2"),
        ])
        acoustic = self.write_csv("acoustic.csv", [
            self.row(output_id="acoustic-drone", sensor_type="acoustic", predicted_label="drone", source_observation_id="dads-row-1-start-0"),
            self.row(output_id="acoustic-drone-later", sensor_type="acoustic", predicted_label="drone", source_observation_id="dads-row-1-start-16000"),
            self.row(output_id="acoustic-quiet", sensor_type="acoustic", predicted_label="no_drone", source_observation_id="dads-row-2-start-0"),
            self.row(output_id="acoustic-quiet-later", sensor_type="acoustic", predicted_label="no_drone", source_observation_id="dads-row-2-start-16000"),
        ])
        return radar, thermal, acoustic

    def run_replay(self):
        radar, thermal, acoustic = self.fixture_csvs()
        output = self.root / "replay.json"
        argv = [
            "run_real_output_replay.py",
            "--radar", str(radar),
            "--thermal", str(thermal),
            "--acoustic", str(acoustic),
            "--output", str(output),
        ]
        with patch("sys.argv", argv), redirect_stdout(io.StringIO()):
            replay.main()
        return json.loads(output.read_text(encoding="utf-8"))

    def test_acoustic_evidence_is_present_and_rf_stays_missing(self):
        result = self.run_replay()
        self.assertEqual(result["available_sensor_types"], ["rf", "radar", "thermal", "acoustic"])
        self.assertEqual(result["missing_sensor_types"], [])
        self.assertEqual(len(result["scenarios"]), 23)
        for item in result["scenarios"]:
            evidence = {row["sensor_type"]: row for row in item["record"]["evidence"]}
            self.assertIn("acoustic", evidence)
            number = int(item["record"]["event_id"].rsplit("-", 1)[-1])
            if number <= 16:
                self.assertEqual(evidence["rf"]["status"], "missing")
                self.assertIsNone(evidence["rf"]["prediction"])
        by_id = {item["record"]["event_id"]: item for item in result["scenarios"]}
        agreed = {row["sensor_type"]: row for row in by_id["sim-real-017"]["record"]["evidence"]}
        self.assertEqual(agreed["rf"]["status"], "available")
        self.assertEqual(agreed["rf"]["prediction"], "Machine")
        false_alarm = {row["sensor_type"]: row for row in by_id["sim-real-018"]["record"]["evidence"]}
        self.assertEqual(false_alarm["rf"]["prediction"], "Machine")
        self.assertEqual(false_alarm["radar"]["prediction"], "human")

    def test_every_scenario_is_simulated_and_requires_review(self):
        result = self.run_replay()
        self.assertGreaterEqual(len(result["scenarios"]), 1)
        for item in result["scenarios"]:
            self.assertTrue(item["record"]["simulated"])
            self.assertTrue(item["record"]["review_required"])

    def test_non_test_split_is_rejected(self):
        path = self.write_csv("train-split.csv", [self.row(split="train")])
        with self.assertRaisesRegex(ValueError, "held-out test"):
            replay.load_rows(path)

    def test_rf_picker_skips_a_wrong_class_and_a_duplicate(self):
        rows = [
            self.row(output_id="rf-wrong", sensor_type="rf", predicted_label="Machine", source_observation_id="wrong.png"),
            self.row(output_id="rf-copy", sensor_type="rf", predicted_label="Machine", source_observation_id="copy.png"),
            self.row(output_id="rf-clean", sensor_type="rf", predicted_label="Machine", source_observation_id="clean.png"),
        ]
        manifest = {"wrong.png": "Benign", "copy.png": "Machine", "clean.png": "Machine"}
        picked = replay.first_clean_rf(rows, "Machine", manifest, excluded=frozenset({"copy.png"}))
        self.assertEqual(picked["output_id"], "rf-clean")
        error = replay.first_clean_rf(rows, "Machine", manifest, excluded=frozenset(), true_class="Benign")
        self.assertEqual(error["output_id"], "rf-wrong")

    def test_missing_acoustic_row_is_missing_evidence(self):
        radar = self.row(output_id="radar-drone", sensor_type="radar")
        thermal = self.row(output_id="thermal-drone", sensor_type="thermal")
        item = replay.scenario("sim-real-014", "acoustic_missing", radar, thermal)
        evidence = {row["sensor_type"]: row for row in item["record"]["evidence"]}
        self.assertEqual(evidence["acoustic"]["status"], "missing")
        self.assertIsNone(evidence["acoustic"]["prediction"])


if __name__ == "__main__":
    unittest.main()
