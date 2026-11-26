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
        rf = self.write_csv("rf.csv", [
            self.row(output_id="rf-false-alarm", sensor_type="rf", predicted_label="Machine", source_observation_id="false-alarm.png", score="0.50"),
            self.row(output_id='rf-Machine', sensor_type="rf", predicted_label="Machine", source_observation_id="machine.png", score="0.80"),
            self.row(output_id='rf-Benign', sensor_type="rf", predicted_label="Benign", source_observation_id="benign.png", score="0.70"),
            self.row(output_id='rf-Broadband_Jam', sensor_type="rf", predicted_label="Broadband_Jam", source_observation_id="jam.png", score="0.99"),
        ])
        return radar, thermal, acoustic, rf

    def run_replay(self, sensors=4, **extra_options):
        radar, thermal, acoustic, rf = self.fixture_csvs()
        manifest = self.root / "rf-manifest.csv"
        manifest.write_text("filename,class,split\nfalse-alarm.png,Benign,test\n"
                            "machine.png,Machine,test\nbenign.png,Benign,test\n"
                            "jam.png,Broadband_Jam,test\n", encoding="utf-8")
        registry = self.root / "dataset-manifest.csv"
        registry.write_text("dataset_id\nfixture\n", encoding="utf-8")
        aliases = self.root / "dataset-id-aliases.csv"
        aliases.write_text("alias_id,dataset_id\n", encoding="utf-8")
        output = self.root / "replay.json"
        argv = [
            "run_real_output_replay.py",
            "--radar", str(radar),
            "--thermal", str(thermal),
            "--dataset-manifest", str(registry),
            "--dataset-aliases", str(aliases),
            "--output", str(output),
        ]
        argv.extend(["--acoustic", str(acoustic)] if sensors >= 3 else ["--no-acoustic"])
        if sensors == 4:
            argv.extend(["--rf", str(rf), "--rf-manifest", str(manifest)])
        else:
            rf.unlink()
            manifest.unlink()
        if sensors == 2:
            acoustic.unlink()
        for flag, value in extra_options.items():
            argv.extend(["--" + flag.replace("_", "-"), str(value)])
        with patch("sys.argv", argv), redirect_stdout(io.StringIO()):
            replay.main()
        return json.loads(output.read_text(encoding="utf-8"))

    def test_acoustic_and_rf_evidence_are_present(self):
        result = self.run_replay()
        self.assertEqual(result["available_sensor_types"], ["rf", "radar", "thermal", "acoustic"])
        self.assertEqual(result["missing_sensor_types"], [])
        self.assertEqual(len(result["scenarios"]), 25)
        early_rf = {
            "sim-real-001": "Machine",
            "sim-real-002": "Benign",
            "sim-real-003": "Benign",
            "sim-real-004": "Machine",
            "sim-real-005": "Machine",
            "sim-real-006": "Machine",
            "sim-real-007": "Machine",
            "sim-real-008": "Machine",
            "sim-real-009": "Machine",
            "sim-real-010": "Benign",
            "sim-real-011": "Machine",
            "sim-real-012": "Benign",
            "sim-real-013": "Benign",
            "sim-real-014": "Machine",
            "sim-real-015": "Machine",
            "sim-real-016": "Machine",
        }
        by_id = {item["record"]["event_id"]: item for item in result["scenarios"]}
        for item in result["scenarios"]:
            evidence = {row["sensor_type"]: row for row in item["record"]["evidence"]}
            self.assertIn("acoustic", evidence)
        for event_id, label in early_rf.items():
            evidence = {row["sensor_type"]: row for row in by_id[event_id]["record"]["evidence"]}
            self.assertEqual(evidence["rf"]["status"], "available")
            self.assertEqual(evidence["rf"]["prediction"], label)
        expected = {
            "sim-real-017": ("available", "Machine"),
            "sim-real-018": ("available", "Machine"),
            "sim-real-019": ("available", "Benign"),
            "sim-real-020": ("available", "Machine"),
            "sim-real-021": ("available", "Broadband_Jam"),
            "sim-real-022": ("delayed", "Machine"),
            "sim-real-023": ("low_quality", "Machine"),
        }
        for event_id, (status, label) in expected.items():
            evidence = {row["sensor_type"]: row for row in by_id[event_id]["record"]["evidence"]}
            self.assertEqual(evidence["rf"]["status"], status)
            self.assertEqual(evidence["rf"]["prediction"], label)
        only_rf = {row["sensor_type"]: row for row in by_id["sim-real-020"]["record"]["evidence"]}
        self.assertEqual(only_rf["radar"]["status"], "missing")
        self.assertEqual(only_rf["thermal"]["status"], "missing")
        self.assertEqual(only_rf["acoustic"]["status"], "missing")
        rf_missing = {row["sensor_type"]: row for row in by_id["sim-real-024"]["record"]["evidence"]}
        self.assertEqual(rf_missing["rf"]["status"], "missing")
        self.assertIsNone(rf_missing["rf"]["prediction"])
        self.assertEqual(rf_missing["radar"]["status"], "available")
        radar_low = {row["sensor_type"]: row for row in by_id["sim-real-025"]["record"]["evidence"]}
        self.assertEqual(radar_low["radar"]["status"], "low_quality")
        self.assertEqual(radar_low["rf"]["status"], "available")

    def test_every_scenario_is_simulated_and_requires_review(self):
        for sensors in (2, 3, 4):
            with self.subTest(sensors=sensors):
                result = self.run_replay(sensors)
                for item in result["scenarios"]:
                    self.assertTrue(item["record"]["simulated"])
                    self.assertTrue(item["record"]["review_required"])
                    for evidence in item["record"]["evidence"]:
                        if evidence["status"] == "missing":
                            self.assertIsNone(evidence["prediction"])
                            self.assertIsNone(evidence["score"])
                        else:
                            self.assertIn("#output_id=", evidence["source_ref"])

    def test_two_sensor_mode_needs_no_acoustic_or_rf_file(self):
        result = self.run_replay(2)
        self.assertEqual(len(result["scenarios"]), 10)
        self.assertEqual(result["available_sensor_types"], ["radar", "thermal"])
        self.assertEqual(result["missing_sensor_types"], ["rf", "acoustic"])
        self.assertEqual(result["scenarios"][0]["scenario"], "radar_thermal_predict_drone")
        for item in result["scenarios"]:
            for row in item["record"]["evidence"]:
                if row["sensor_type"] in ("rf", "acoustic"):
                    self.assertEqual(row["status"], "missing")

    def test_three_sensor_mode_keeps_rf_missing(self):
        result = self.run_replay(3)
        self.assertEqual(len(result["scenarios"]), 16)
        self.assertEqual(result["missing_sensor_types"], ["rf"])
        self.assertNotIn("rf", result["input_files"])
        for item in result["scenarios"]:
            rf = next(row for row in item["record"]["evidence"] if row["sensor_type"] == "rf")
            self.assertEqual(rf["status"], "missing")
            self.assertIsNone(rf["prediction"])

    def test_explicit_missing_rf_manifest_does_not_fall_back(self):
        with self.assertRaises(FileNotFoundError):
            self.run_replay(rf_manifest=self.root / "absent.csv")

    def test_fixture_run_is_independent_of_current_directory(self):
        from contextlib import chdir
        with chdir(self.root):
            self.assertEqual(len(self.run_replay()["scenarios"]), 25)

    def test_rf_machine_remains_machine_with_raw_score(self):
        result = self.run_replay()
        item = next(item for item in result["scenarios"] if item["record"]["event_id"] == "sim-real-017")
        self.assertEqual(item["scenario"], "rf_machine_with_three_drone_predictions")
        rf = next(row for row in item["record"]["evidence"] if row["sensor_type"] == "rf")
        self.assertEqual(rf["prediction"], "Machine")
        self.assertEqual(rf["score"], 0.80)

    def test_acoustic_tail_is_not_silently_used(self):
        rows = [self.row(sensor_type="acoustic", source_observation_id="clip-start-0")]
        with self.assertRaisesRegex(ValueError, "full-length"):
            replay.first_full_length(rows, "drone")

    def test_csv_for_wrong_sensor_is_rejected(self):
        path = self.write_csv("wrong.csv", [self.row(sensor_type="thermal")])
        with self.assertRaisesRegex(ValueError, "expected only radar"):
            replay.load_rows(path, "radar")

    def test_rf_manifest_rejects_duplicate_test_ids(self):
        path = self.root / "duplicate-manifest.csv"
        path.write_text("filename,class,split\nsame.png,Machine,test\nsame.png,Benign,test\n")
        with self.assertRaisesRegex(ValueError, "unique"):
            replay.load_rf_manifest(path)

    def test_rf_csv_with_non_test_split_is_rejected(self):
        path = self.write_csv("rf-train.csv", [
            self.row(output_id="rf-train", sensor_type="rf", predicted_label="Machine", split="train"),
        ])
        with self.assertRaisesRegex(ValueError, "held-out test"):
            replay.load_rows(path)

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
