import csv
import tempfile
import unittest
from pathlib import Path

from src.validate_model_outputs import REQUIRED_COLUMNS, load_dataset_registry, validate


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

    def write_registry(self, canonical_ids, alias_rows=()):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        manifest = Path(directory.name) / "manifest.csv"
        aliases = Path(directory.name) / "aliases.csv"
        with manifest.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["dataset_id"])
            writer.writerows([dataset_id] for dataset_id in canonical_ids)
        with aliases.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["alias_id", "dataset_id"])
            writer.writerows(alias_rows)
        return manifest, aliases

    def test_valid_held_out_output(self):
        self.assertEqual(validate(self.write_rows([self.row()])), 1)

    def test_rejects_non_test_output(self):
        with self.assertRaisesRegex(ValueError, "held-out test"):
            validate(self.write_rows([self.row(split="validation")]))

    def test_rejects_out_of_range_score(self):
        with self.assertRaisesRegex(ValueError, "between zero and one"):
            validate(self.write_rows([self.row(score="1.2")]))

    def test_registry_accepts_canonical_ids_and_preserves_aliased_outputs(self):
        manifest, aliases = self.write_registry(
            ["kth_77ghz_v2", "drone_detection_dataset2", "rf_intrusion_spectrogram"],
            [
                ("drone_detection_dataset_2", "drone_detection_dataset2"),
                ("unified_multi_class_rf_intrusion", "rf_intrusion_spectrogram"),
            ],
        )
        registry = load_dataset_registry(manifest, aliases)
        self.assertEqual(registry["drone_detection_dataset_2"], "drone_detection_dataset2")
        self.assertEqual(registry["unified_multi_class_rf_intrusion"], "rf_intrusion_spectrogram")
        path = self.write_rows([
            self.row(),
            self.row(output_id="thermal-1", sensor_type="thermal", dataset_id="drone_detection_dataset_2"),
            self.row(output_id="rf-1", sensor_type="rf", dataset_id="unified_multi_class_rf_intrusion"),
        ])
        original = path.read_bytes()
        self.assertEqual(validate(path, dataset_registry=registry), 3)
        self.assertEqual(path.read_bytes(), original)

    def test_unknown_dataset_is_rejected_only_when_registry_is_supplied(self):
        manifest, _ = self.write_registry(["kth_77ghz_v2"])
        path = self.write_rows([self.row(dataset_id="unregistered-fixture")])
        self.assertEqual(validate(path), 1)
        with self.assertRaisesRegex(ValueError, "unknown dataset_id"):
            validate(path, dataset_registry=load_dataset_registry(manifest))

    def test_alias_requires_explicit_registry_entry(self):
        manifest, aliases = self.write_registry(
            ["drone_detection_dataset2"],
            [("drone_detection_dataset_2", "drone_detection_dataset2")],
        )
        path = self.write_rows([self.row(dataset_id="drone_detection_dataset_2")])
        with self.assertRaisesRegex(ValueError, "unknown dataset_id"):
            validate(path, dataset_registry=load_dataset_registry(manifest))
        self.assertEqual(validate(path, dataset_registry=load_dataset_registry(manifest, aliases)), 1)

    def test_duplicate_canonical_dataset_ids_are_rejected(self):
        manifest, _ = self.write_registry(["same-id", "same-id"])
        with self.assertRaisesRegex(ValueError, "ambiguous dataset_id"):
            load_dataset_registry(manifest)

    def test_duplicate_or_shadowing_aliases_are_rejected(self):
        for alias_rows in (
            [("alias", "first"), ("alias", "second")],
            [("alias", "first"), ("alias", "first")],
            [("first", "second")],
        ):
            with self.subTest(aliases=alias_rows):
                manifest, aliases = self.write_registry(["first", "second"], alias_rows)
                with self.assertRaisesRegex(ValueError, "ambiguous dataset alias"):
                    load_dataset_registry(manifest, aliases)

    def test_alias_targets_must_be_canonical_manifest_ids(self):
        for alias_rows in (
            [("alias", "unknown")],
            [("alias", "canonical"), ("chained-alias", "alias")],
        ):
            with self.subTest(aliases=alias_rows):
                manifest, aliases = self.write_registry(["canonical"], alias_rows)
                with self.assertRaisesRegex(ValueError, "unknown canonical dataset_id"):
                    load_dataset_registry(manifest, aliases)


if __name__ == "__main__":
    unittest.main()
