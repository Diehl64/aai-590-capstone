import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.rf_duplicate_sensitivity import run


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class DuplicateSensitivityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        root = Path(self.tmp.name)
        self.manifest = root / "manifest.csv"
        self.outputs = root / "outputs.csv"
        self.integrity = root / "integrity.json"
        write_csv(self.manifest, ["filename", "class", "split"], [
            {"filename": "a.png", "class": "Machine", "split": "test"},
            {"filename": "b.png", "class": "Benign", "split": "test"},
            {"filename": "c.png", "class": "Narrowband_Jam", "split": "test"},
            {"filename": "d.png", "class": "Narrowband_Jam", "split": "train"},
        ])
        self.handoff_rows = [
            {"source_observation_id": "a.png", "split": "test", "predicted_label": "Machine", "model_version": "fixture"},
            {"source_observation_id": "b.png", "split": "test", "predicted_label": "Machine", "model_version": "fixture"},
            {"source_observation_id": "c.png", "split": "test", "predicted_label": "Narrowband_Jam", "model_version": "fixture"},
        ]
        self.write_handoff()
        self.integrity.write_text(json.dumps({"groups": [{
            "same_class": True,
            "files": [
                {"filename": "c.png", "class_label": "Narrowband_Jam", "assignment_split": "test"},
                {"filename": "d.png", "class_label": "Narrowband_Jam", "assignment_split": "train"},
            ],
        }]}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write_handoff(self):
        write_csv(self.outputs, ["source_observation_id", "split", "predicted_label", "model_version"], self.handoff_rows)

    def test_cross_split_copy_is_excluded(self):
        result = run(self.outputs, self.manifest, self.integrity)
        self.assertEqual(result["excluded_files"], ["c.png"])
        self.assertEqual(result["all_test_images"]["images"], 3)
        self.assertEqual(result["excluding_copy_outside_test"]["images"], 2)

    def test_benign_machine_counts_are_kept(self):
        result = run(self.outputs, self.manifest, self.integrity)
        for key in ("all_test_images", "excluding_copy_outside_test"):
            self.assertEqual(result[key]["benign_to_machine"], 1)
            self.assertEqual(result[key]["machine_recall"], 1.0)

    def test_non_test_rows_are_rejected(self):
        self.handoff_rows[0]["split"] = "validation"
        self.write_handoff()
        with self.assertRaises(ValueError):
            run(self.outputs, self.manifest, self.integrity)

    def test_duplicate_source_id_cannot_replace_missing_test_image(self):
        self.handoff_rows[1]["source_observation_id"] = "a.png"
        self.write_handoff()
        with self.assertRaisesRegex(ValueError, "source_observation_id values must be unique"):
            run(self.outputs, self.manifest, self.integrity)

    def test_missing_test_image_is_rejected(self):
        self.handoff_rows.pop()
        self.write_handoff()
        with self.assertRaisesRegex(ValueError, "exactly the test split"):
            run(self.outputs, self.manifest, self.integrity)

    def test_unexpected_source_id_is_rejected_even_with_same_row_count(self):
        self.handoff_rows[0]["source_observation_id"] = "d.png"
        self.write_handoff()
        with self.assertRaisesRegex(ValueError, "exactly the test split"):
            run(self.outputs, self.manifest, self.integrity)


if __name__ == "__main__":
    unittest.main()
