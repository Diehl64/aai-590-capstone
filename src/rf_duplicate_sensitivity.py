"""Rescore the selected RF test outputs without cross-split duplicate images.

Reads only committed files: the held-out CSV, the split manifest (true classes),
and the exact-duplicate groups in rf_integrity_checks.json. Nothing is retrained
and no threshold is refit; the test predictions are the ones already handed off.
Writes results/rf-intrusion/rf_v5_test_duplicate_sensitivity.json.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

CLASSES = ("Benign", "Broadband_Jam", "Human", "Machine", "Narrowband_Jam", "Wildlife")
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUTS = ROOT / "data" / "model-outputs" / "rf-cnn-test-outputs.csv"
DEFAULT_MANIFEST = ROOT / "data" / "rf-split-manifest.csv"
DEFAULT_INTEGRITY = ROOT / "results" / "rf-intrusion" / "rf_integrity_checks.json"
DEFAULT_RESULT = ROOT / "results" / "rf-intrusion" / "rf_v5_test_duplicate_sensitivity.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def duplicated_in(split: str, groups: list[dict]) -> dict[str, set[str]]:
    """Files of `split` that share bytes with another split, and those in any duplicate group."""
    cross, any_group = set(), set()
    for group in groups:
        mine = {f["filename"] for f in group["files"] if f["assignment_split"] == split}
        others = [f for f in group["files"] if f["assignment_split"] != split]
        any_group |= mine
        if mine and others:
            cross |= mine
    return {"copy_outside_split": cross, "any_duplicate_group": any_group}


def metrics(rows: list[tuple[str, str]]) -> dict:
    index = {name: i for i, name in enumerate(CLASSES)}
    matrix = [[0] * len(CLASSES) for _ in CLASSES]
    for true, predicted in rows:
        matrix[index[true]][index[predicted]] += 1
    per_class, f1_scores = {}, []
    for i, name in enumerate(CLASSES):
        tp = matrix[i][i]
        support = sum(matrix[i])
        predicted = sum(row[i] for row in matrix)
        precision = tp / predicted if predicted else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_scores.append(f1)
        per_class[name] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
    machine, benign = index["Machine"], index["Benign"]
    return {
        "images": len(rows),
        "accuracy": sum(matrix[i][i] for i in range(len(CLASSES))) / len(rows),
        "macro_f1": sum(f1_scores) / len(f1_scores),
        "machine_recall": per_class["Machine"]["recall"],
        "machine_precision": per_class["Machine"]["precision"],
        "benign_recall": per_class["Benign"]["recall"],
        "benign_to_machine": matrix[benign][machine],
        "machine_to_benign": matrix[machine][benign],
        "per_class": per_class,
        "confusion_matrix": {"labels": list(CLASSES), "rows_true_columns_predicted": matrix},
    }


def run(outputs: Path, manifest: Path, integrity: Path) -> dict:
    truth = {row["filename"]: row["class"] for row in read_csv(manifest) if row["split"] == "test"}
    handoff = read_csv(outputs)
    source_ids = [row["source_observation_id"] for row in handoff]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("handoff source_observation_id values must be unique")
    if set(source_ids) != set(truth) or any(row["split"] != "test" for row in handoff):
        raise ValueError("the handoff must hold exactly the test split of the manifest")
    pairs = {row["source_observation_id"]: (truth[row["source_observation_id"]], row["predicted_label"]) for row in handoff}
    checks = json.loads(Path(integrity).read_text(encoding="utf-8"))
    groups = checks["groups"]
    test_sets = duplicated_in("test", groups)
    validation_sets = duplicated_in("validation", groups)
    mixed_label_test = sorted(
        f["filename"] for g in groups if not g["same_class"] for f in g["files"] if f["assignment_split"] == "test"
    )

    def subset(excluded: set[str]) -> dict:
        return metrics([pair for name, pair in pairs.items() if name not in excluded])

    cross = test_sets["copy_outside_split"]
    return {
        "purpose": "Sensitivity of the selected RF v5 test result to exact cross-split duplicate images.",
        "inputs": {
            "handoff": "data/model-outputs/rf-cnn-test-outputs.csv",
            "true_classes": "data/rf-split-manifest.csv",
            "duplicate_groups": "results/rf-intrusion/rf_integrity_checks.json",
        },
        "model_version": handoff[0]["model_version"],
        "not_retrained": True,
        "threshold_not_refit": True,
        "test_duplicates": {
            "copy_outside_test": len(cross),
            "in_any_duplicate_group": len(test_sets["any_duplicate_group"]),
            "in_mixed_label_groups": len(mixed_label_test),
            "copy_outside_test_by_class": dict(Counter(truth[name] for name in cross)),
            "copy_outside_test_correct": sum(pairs[n][0] == pairs[n][1] for n in cross),
        },
        "validation_duplicates": {
            "copy_outside_validation": len(validation_sets["copy_outside_split"]),
            "copy_outside_validation_by_class": dict(Counter(
                f["class_label"] for g in groups for f in g["files"]
                if f["assignment_split"] == "validation" and f["filename"] in validation_sets["copy_outside_split"]
            )),
        },
        "all_test_images": subset(set()),
        "excluding_copy_outside_test": subset(cross),
        "excluding_any_duplicate_group": subset(test_sets["any_duplicate_group"]),
        "excluded_files": sorted(cross),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--outputs", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--integrity", type=Path, default=DEFAULT_INTEGRITY)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    result = run(args.outputs, args.manifest, args.integrity)
    args.result.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key in ("all_test_images", "excluding_copy_outside_test"):
        m = result[key]
        print(f"{key}: {m['images']} images, Machine recall {m['machine_recall']:.4f}, "
              f"Benign->Machine {m['benign_to_machine']}, Machine->Benign {m['machine_to_benign']}, "
              f"macro F1 {m['macro_f1']:.4f}")
    print(f"wrote {args.result}")


if __name__ == "__main__":
    main()
