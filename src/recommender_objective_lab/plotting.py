from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _ci95(series: pd.Series) -> float:
    if len(series) < 2:
        return float("nan")
    return float(1.96 * series.std(ddof=1) / np.sqrt(len(series)))


def make_figures(results_dir: Path, figures_dir: Path) -> list[Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    alpha = pd.read_csv(results_dir / "alpha_sweep_raw.csv")
    sensitivity = pd.read_csv(results_dir / "sensitivity_delta.csv")
    ablation = pd.read_csv(results_dir / "ablation_delta.csv")

    created: list[Path] = []

    pareto = alpha.groupby("alpha")[["CTR", "satisfaction"]].mean().reset_index()
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(pareto["CTR"], pareto["satisfaction"], marker="o")
    for _, row in pareto.iterrows():
        ax.annotate(
            f"α={row['alpha']:.1f}",
            (row["CTR"], row["satisfaction"]),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_title("Objective trade-off: CTR vs satisfaction")
    ax.set_xlabel("CTR")
    ax.set_ylabel("Satisfaction")
    fig.tight_layout()
    path = figures_dir / "01_pareto_ctr_vs_satisfaction.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    created.append(path)

    trajectory = (
        alpha.groupby("alpha")["mean_sessions"]
        .agg(["mean", _ci95])
        .reset_index()
        .rename(columns={"_ci95": "ci95"})
    )
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.errorbar(
        trajectory["alpha"],
        trajectory["mean"],
        yerr=trajectory["ci95"],
        marker="o",
        capsize=3,
    )
    ax.set_title("Objective mix vs synthetic long-term retention")
    ax.set_xlabel("Value-aware weight α")
    ax.set_ylabel("Mean sessions")
    fig.tight_layout()
    path = figures_dir / "02_alpha_vs_mean_sessions.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    created.append(path)

    for metric, number, label in [
        ("delta_satisfaction", "03", "Δ satisfaction"),
        ("delta_mean_sessions", "04", "Δ mean sessions"),
    ]:
        heat = sensitivity.groupby(["parameter", "value"])[metric].mean().unstack()
        fig, ax = plt.subplots(figsize=(8, 3.8))
        image = ax.imshow(heat.values, aspect="auto")
        ax.set_title(f"Sensitivity: {label} (value − engagement)")
        ax.set_yticks(np.arange(len(heat.index)))
        ax.set_yticklabels(heat.index)
        ax.set_xticks(np.arange(len(heat.columns)))
        ax.set_xticklabels([str(x) for x in heat.columns])
        ax.set_xlabel("Parameter value")
        for i in range(heat.shape[0]):
            for j in range(heat.shape[1]):
                value = heat.iloc[i, j]
                if pd.notna(value):
                    fmt = ".3f" if metric == "delta_satisfaction" else ".2f"
                    ax.text(j, i, format(value, fmt), ha="center", va="center", fontsize=8)
        fig.colorbar(image, ax=ax, label=label)
        fig.tight_layout()
        path = figures_dir / f"{number}_sensitivity_{metric}.png"
        fig.savefig(path, dpi=120)
        plt.close(fig)
        created.append(path)

    for metric, number, title in [
        ("delta_satisfaction", "05", "Ablation study: Δ satisfaction"),
        ("delta_mean_sessions", "06", "Ablation study: Δ mean sessions"),
        ("delta_CTR", "07", "Ablation study: Δ CTR"),
    ]:
        summary = (
            ablation.groupby("ablation")[metric]
            .agg(["mean", _ci95])
            .rename(columns={"_ci95": "ci95"})
            .sort_values("mean")
        )
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.barh(summary.index, summary["mean"], xerr=summary["ci95"], capsize=3)
        ax.axvline(0, linewidth=1)
        ax.set_title(title)
        ax.set_xlabel("Value-aware − engagement")
        fig.tight_layout()
        path = figures_dir / f"{number}_{metric}.png"
        fig.savefig(path, dpi=120)
        plt.close(fig)
        created.append(path)

    return created
