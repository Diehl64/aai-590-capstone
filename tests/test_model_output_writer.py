import tempfile
import unittest
from pathlib import Path

from src.model_output_handoff import write_handoff
from src.validate_model_outputs import validate


class ModelOutputWriterTests(unittest.TestCase):
    def test_written_handoff_passes_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "outputs.csv"
            write_handoff(path, [{
                "output_id": "radar-test-000001", "sensor_type": "radar", "source_observation_id": "measurement-1-segment-2",
                "split": "test", "timestamp": "source-time-unavailable", "predicted_label": "drone", "score": .91,
                "model_version": "RadarCNN-seed-590", "dataset_id": "kth_77ghz_v2", "source_output_ref": "results/radar-test-outputs.csv",
            }])
            self.assertEqual(validate(path), 1)
