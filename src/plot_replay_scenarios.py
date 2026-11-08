"""Create a presentation figure from the simulated replay scenario JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle


SENSORS = ("rf", "radar", "thermal", "acoustic")
COLORS = {
    "available": "#5B9BD5",
    "missing": "#BFBFBF",
    "delayed": "#FFC000",
    "low_quality": "#ED7D31",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/real-output-replay/real-output-replay.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/real-output-replay/scenario-evidence-status-matrix.png"
        ),
    )
    args = parser.parse_args()

    replay = json.loads(args.input.read_text(encoding="utf-8"))
    scenarios = replay["scenarios"]

    figure, axis = plt.subplots(figsize=(11, 7))
    axis.set_xlim(0, len(SENSORS) + 1.9)
    axis.set_ylim(-0.8, len(scenarios))
    axis.axis("off")

    for column, sensor in enumerate(SENSORS, start=1):
        axis.text(
            column + 0.5,
            len(scenarios) - 0.25,
            sensor.upper(),
            ha="center",
            va="center",
            weight="bold",
        )

    for row, item in enumerate(scenarios):
        y = len(scenarios) - row - 1
        axis.text(
            0.0,
            y + 0.5,
            item["scenario"].replace("_", " "),
            ha="left",
            va="center",
            fontsize=9,
        )

        states = {
            evidence["sensor_type"]: evidence["status"]
            for evidence in item["record"]["evidence"]
        }
        for column, sensor in enumerate(SENSORS, start=1):
            state = states[sensor]
            axis.add_patch(
                Rectangle(
                    (column, y),
                    1,
                    1,
                    facecolor=COLORS[state],
                    edgecolor="white",
                    linewidth=2,
                )
            )
            axis.text(
                column + 0.5,
                y + 0.5,
                state.replace("_", "\n"),
                ha="center",
                va="center",
                fontsize=8,
            )

    legend = [
        Patch(facecolor=color, label=status.replace("_", " ").title())
        for status, color in COLORS.items()
    ]
    axis.legend(
        handles=legend,
        loc="lower center",
        bbox_to_anchor=(0.62, -0.12),
        ncol=4,
        frameon=False,
    )
    axis.set_title(
        "Simulated replay scenario evidence states\n"
        "All scenarios require human review; this is not measured sensor fusion.",
        weight="bold",
        pad=18,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(args.output, dpi=200, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()