import unittest
import numpy as np

from src.radar_baseline import coarse_label, evaluate, grouped_split
from src.replay_workflow import (RadarResult, VerificationResult,
                                  VerificationStatus, ReviewStatus, create_review)


class RadarWorkflowTests(unittest.TestCase):
    def test_mapping_and_reflector_policy(self):
        self.assertEqual(coarse_label("D1"), "drone")
        self.assertEqual(coarse_label("seagull"), "bird")
        self.assertEqual(coarse_label("human_walk"), "human")
        self.assertEqual(coarse_label("CR"), "reflector")

    def test_grouped_split_is_reproducible_and_covers_classes(self):
        ms = [{"measurement_id": i, "class": cls, "segments": 10 + i}
              for i, cls in enumerate(("drone", "bird", "human") * 4)]
        first = grouped_split(ms, 590)
        self.assertEqual(first, grouped_split(ms, 590))
        self.assertEqual(set(first.values()), {"train", "validation", "test"})
        self.assertEqual(len(first), len(ms))

    def test_metric_shape_and_accuracy(self):
        result = evaluate(np.array(["drone", "bird", "human"]),
                          np.array(["drone", "bird", "human"]),
                          ["drone", "bird", "human"])
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["confusion_matrix"], [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    def test_conflicting_verification_requires_review(self):
        radar = RadarResult("e", "o", "drone", {"drone": .9}, "model", "2026-01-01T00:00:00Z")
        verification = VerificationResult("e", VerificationStatus.CONFLICTING, predicted_class="bird")
        self.assertEqual(create_review(radar, verification).review_status, ReviewStatus.REQUIRED)


if __name__ == "__main__":
    unittest.main()
