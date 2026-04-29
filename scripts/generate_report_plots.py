"""Generate report-ready figures from local pipeline JSON reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np


COLORS = {
    "ink": "#1d2623",
    "muted": "#60706a",
    "line": "#ded4c2",
    "panel": "#fffaf0",
    "accent": "#b9472f",
    "accent_dark": "#7f2f22",
    "green": "#246a52",
    "sand": "#efe5d3",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def prepare_figure(width: float = 8.0, height: float = 5.0):
    fig, ax = plt.subplots(figsize=(width, height), dpi=180)
    fig.patch.set_facecolor(COLORS["panel"])
    ax.set_facecolor(COLORS["panel"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["line"])
    ax.spines["bottom"].set_color(COLORS["line"])
    ax.tick_params(colors=COLORS["ink"])
    ax.grid(axis="y", color=COLORS["line"], linewidth=0.8, alpha=0.75)
    ax.set_axisbelow(True)
    return fig, ax


def save_figure(fig, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def add_value_labels(ax, bars, fmt="{:.3f}", padding=0.012) -> None:
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + padding,
            fmt.format(height),
            va="bottom",
            ha="center",
            fontsize=8,
            color=COLORS["ink"],
        )


def add_horizontal_value_labels(ax, bars, fmt="{:.0f}", padding=0.3) -> None:
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + padding,
            bar.get_y() + bar.get_height() / 2,
            fmt.format(width),
            va="center",
            ha="left",
            fontsize=8,
            color=COLORS["ink"],
        )


def plot_model_metrics(evaluation: dict, output_dir: Path) -> None:
    comparison = evaluation["model_comparison"]
    models = ["Baseline", "Proposed hybrid"]
    metrics = ["accuracy", "macro_f1"]
    labels = ["Accuracy", "Macro F1"]
    values = np.array([
        [comparison["baseline"][metric] for metric in metrics],
        [comparison["proposed"][metric] for metric in metrics],
    ])

    fig, ax = prepare_figure(7.0, 4.5)
    x = np.arange(len(labels))
    width = 0.34
    baseline_bars = ax.bar(
        x - width / 2,
        values[0],
        width,
        label=models[0],
        color=COLORS["ink"],
    )
    proposed_bars = ax.bar(
        x + width / 2,
        values[1],
        width,
        label=models[1],
        color=COLORS["accent"],
    )

    ax.set_title("Classification Metrics on Real Dataset", color=COLORS["ink"], pad=16)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 0.75)
    ax.set_ylabel("Score")
    ax.legend(frameon=False, loc="upper right")
    add_value_labels(ax, baseline_bars, fmt="{:.4f}", padding=0.01)
    add_value_labels(ax, proposed_bars, fmt="{:.4f}", padding=0.01)
    save_figure(fig, output_dir / "model_metrics.png")


def plot_category_f1(evaluation: dict, output_dir: Path) -> None:
    comparison = evaluation["model_comparison"]
    baseline = comparison["baseline"]["per_class_f1"]
    proposed = comparison["proposed"]["per_class_f1"]
    categories = sorted(proposed, key=proposed.get)
    y = np.arange(len(categories))
    height = 0.38

    fig, ax = prepare_figure(9.0, 8.5)
    ax.barh(
        y - height / 2,
        [baseline[category] for category in categories],
        height,
        label="Baseline",
        color=COLORS["ink"],
    )
    ax.barh(
        y + height / 2,
        [proposed[category] for category in categories],
        height,
        label="Proposed hybrid",
        color=COLORS["accent"],
    )

    wrapped_labels = ["\n".join(wrap(category.replace("-", " "), 18)) for category in categories]
    ax.set_title("Per-Category F1 Scores", color=COLORS["ink"], pad=16)
    ax.set_yticks(y, wrapped_labels, fontsize=8)
    ax.set_xlim(0, 0.9)
    ax.set_xlabel("F1 score")
    ax.legend(frameon=False, loc="lower right")
    save_figure(fig, output_dir / "category_f1_scores.png")


def plot_validation_metrics(validation: dict, output_dir: Path) -> None:
    metrics = validation["extraction_validation"]
    names = ["Text similarity", "Skill overlap", "Extraction accuracy"]
    values = [
        metrics["text_similarity_mean"],
        metrics["skill_overlap_mean"],
        metrics["extraction_accuracy"],
    ]
    errors = [
        metrics["text_similarity_std"],
        metrics["skill_overlap_std"],
        0,
    ]

    fig, ax = prepare_figure(7.0, 4.5)
    x = np.arange(len(names))
    bars = ax.bar(
        x,
        values,
        yerr=errors,
        capsize=5,
        color=[COLORS["green"], COLORS["accent"], COLORS["ink"]],
        error_kw={"ecolor": COLORS["muted"], "linewidth": 1.2},
    )

    ax.set_title("CSV/PDF Extraction Validation", color=COLORS["ink"], pad=16)
    ax.set_xticks(x, names)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score")
    ax.text(
        0.98,
        0.08,
        f"Samples compared: {metrics['total_samples']}",
        transform=ax.transAxes,
        ha="right",
        color=COLORS["muted"],
        fontsize=9,
    )
    add_value_labels(ax, bars, fmt="{:.4f}", padding=0.015)
    save_figure(fig, output_dir / "validation_metrics.png")


def plot_cluster_sizes(cluster_report: dict, output_dir: Path) -> None:
    cluster_sizes = {
        int(cluster_id): size
        for cluster_id, size in cluster_report["cluster_sizes"].items()
    }
    clusters = sorted(cluster_sizes)
    sizes = [cluster_sizes[cluster_id] for cluster_id in clusters]
    labels = [f"C{cluster_id}" for cluster_id in clusters]

    fig, ax = prepare_figure(8.0, 4.8)
    bars = ax.bar(labels, sizes, color=COLORS["accent"], edgecolor=COLORS["accent_dark"])
    ax.set_title("PDF Cluster Size Distribution", color=COLORS["ink"], pad=16)
    ax.set_ylabel("Resume count (log scale)")
    ax.set_yscale("log")
    ax.grid(axis="y", which="both", color=COLORS["line"], alpha=0.7)
    ax.text(
        0.98,
        0.92,
        f"Silhouette: {cluster_report['silhouette_score']:.4f}",
        transform=ax.transAxes,
        ha="right",
        color=COLORS["muted"],
        fontsize=9,
    )
    for bar, size in zip(bars, sizes):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            size * 1.12,
            str(size),
            ha="center",
            va="bottom",
            fontsize=8,
            color=COLORS["ink"],
        )
    save_figure(fig, output_dir / "cluster_size_distribution.png")


def plot_association_summary(output_dir: Path) -> None:
    names = ["Frequent itemsets", "Association rules"]
    values = [21, 0]

    fig, ax = prepare_figure(6.8, 3.8)
    bars = ax.barh(names, values, color=[COLORS["ink"], COLORS["accent"]])
    ax.set_title("Association Mining Summary", color=COLORS["ink"], pad=16)
    ax.set_xlabel("Count")
    ax.set_xlim(0, 24)
    add_horizontal_value_labels(ax, bars, fmt="{:.0f}", padding=0.3)
    ax.text(
        0.98,
        0.12,
        "No rules met min_confidence=0.5",
        transform=ax.transAxes,
        ha="right",
        color=COLORS["muted"],
        fontsize=9,
    )
    save_figure(fig, output_dir / "association_summary.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reports-dir",
        default="output/reports",
        help="Directory containing generated JSON reports",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/figures",
        help="Directory for generated PNG figures",
    )
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    output_dir = Path(args.output_dir)

    evaluation = load_json(reports_dir / "evaluation_report.json")
    validation = load_json(reports_dir / "validation_report.json")
    cluster_report = load_json(reports_dir / "cluster_report.json")

    plot_model_metrics(evaluation, output_dir)
    plot_category_f1(evaluation, output_dir)
    plot_validation_metrics(validation, output_dir)
    plot_cluster_sizes(cluster_report, output_dir)
    plot_association_summary(output_dir)

    for path in sorted(output_dir.glob("*.png")):
        print(path)


if __name__ == "__main__":
    main()
