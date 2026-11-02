import csv
import tempfile
import unittest
from pathlib import Path

from src.validate_model_outputs import REQUIRED_COLUMNS, validate


class ModelOutputHandoffTests(unittest.TestCase):
    def write_rows(self, rows):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "outputs.csv"
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=sorted(REQUIRED_COLUMNS))
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(directory.cleanup)
        return path

    def row(self, **updates):
        base = {
            "output_id": "radar-test-001", "sensor_type": "radar", "source_observation_id": "measurement-1-segment-2",
            "split": "test", "timestamp": "source-time-unavailable", "predicted_label": "drone", "score": "0.91",
            "model_version": "radar-cnn-v1", "dataset_id": "kth_77ghz_v2", "source_output_ref": "results/radar.csv",
        }
        base.update(updates)
        return base

    def test_valid_held_out_output(self):
        self.assertEqual(validate(self.write_rows([self.row()])), 1)

    def test_rejects_non_test_output(self):
        with self.assertRaisesRegex(ValueError, "held-out test"):
            validate(self.write_rows([self.row(split="validation")]))

    def test_rejects_out_of_range_score(self):
        with self.assertRaisesRegex(ValueError, "between zero and one"):
            validate(self.write_rows([self.row(score="1.2")]))


if __name__ == "__main__":
    unittest.main()
