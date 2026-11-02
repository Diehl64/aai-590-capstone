import unittest
import numpy as np
from src.radar_baseline import coarse_label, evaluate, grouped_split
from src.replay_workflow import RadarResult, VerificationResult, VerificationStatus, ReviewStatus, create_review

class RadarWorkflowTests(unittest.TestCase):
    def test_mapping_and_reflector_policy(self):
        self.assertEqual(coarse_label("D1"), "drone"); self.assertEqual(coarse_label("seagull"), "bird"); self.assertEqual(coarse_label("human_walk"), "human"); self.assertEqual(coarse_label("CR"), "reflector")
    def test_grouped_split_reproducible(self):
        ms = [{"measurement_id": i, "class": c, "segments": 10 + i} for i, c in enumerate(("drone", "bird", "human") * 4)]
        self.assertEqual(grouped_split(ms, 590), grouped_split(ms, 590))
    def test_metrics(self):
        r = evaluate(np.array(["drone", "bird", "human"]), np.array(["drone", "bird", "human"]), ["drone", "bird", "human"]); self.assertEqual(r["accuracy"], 1.0)
    def test_conflict_requires_review(self):
        radar = RadarResult("e", "o", "drone", {"drone": .9}, "model", "2026-01-01T00:00:00Z"); v = VerificationResult("e", VerificationStatus.CONFLICTING, predicted_class="bird"); self.assertEqual(create_review(radar, v).review_status, ReviewStatus.REQUIRED)

if __name__ == "__main__": unittest.main()
