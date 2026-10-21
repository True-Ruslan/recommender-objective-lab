from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd

from .simulation import SimulationConfig, run_simulation


METRICS = [
    "CTR",
    "dwell_per_impression",
    "satisfaction",
    "mean_return_probability",
    "diversity",
    "fatigue",
    "preference_drift",
    "survival_to_last_session",
    "mean_sessions",
]


def _ci95(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 2:
        return float("nan")
    return float(1.96 * s.std(ddof=1) / np.sqrt(len(s)))


def _summarize(raw: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    group_arg = group_cols[0] if len(group_cols) == 1 else group_cols
    for keys, group in raw.groupby(group_arg, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row: dict[str, float | str] = dict(zip(group_cols, keys))
        for metric in METRICS:
            row[f"{metric}_mean"] = float(group[metric].mean())
            row[f"{metric}_ci95"] = _ci95(group[metric])
        rows.append(row)
    return pd.DataFrame(rows)


def _paired_delta(raw: pd.DataFrame, index_cols: list[str]) -> pd.DataFrame:
    pivot = raw.pivot_table(index=index_cols, columns="policy", values=METRICS)
    rows = []
    for idx, row in pivot.iterrows():
        if not isinstance(idx, tuple):
            idx = (idx,)
        record = dict(zip(index_cols, idx))
        for metric in METRICS:
            record[f"delta_{metric}"] = (
                row[(metric, "value")] - row[(metric, "engagement")]
            )
        rows.append(record)
    return pd.DataFrame(rows)


def _run_task(task: tuple[dict, SimulationConfig]) -> dict:
    metadata, config = task
    return {**metadata, **run_simulation(config)}


def _execute(tasks: list[tuple[dict, SimulationConfig]], jobs: int) -> list[dict]:
    if jobs <= 1:
        return [_run_task(task) for task in tasks]
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        return list(pool.map(_run_task, tasks, chunksize=max(1, len(tasks) // (jobs * 8))))


def _policy_pair_tasks(base: SimulationConfig, seed: int, **metadata) -> list[tuple[dict, SimulationConfig]]:
    tasks = []
    for alpha, policy in ((0.0, "engagement"), (1.0, "value")):
        meta = {**metadata, "policy": policy, "alpha": alpha, "seed": seed}
        tasks.append((meta, base.with_updates(seed=seed, alpha=alpha)))
    return tasks


def run_all_experiments(
    output_dir: Path,
    *,
    seeds: int = 20,
    users: int = 400,
    n_sessions: int = 12,
    steps_per_session: int = 5,
    jobs: int = 1,
) -> dict[str, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)

    base = SimulationConfig(
        n_users=users,
        n_sessions=n_sessions,
        steps_per_session=steps_per_session,
    )

    # 1. Baseline policy comparison.
    tasks = []
    for seed in range(seeds):
        tasks.extend(_policy_pair_tasks(base, seed))
    baseline = pd.DataFrame(_execute(tasks, jobs))
    baseline_summary = _summarize(baseline, ["policy", "alpha"])

    # 2. One-factor-at-a-time sensitivity analysis.
    specs = {
        "reinforcement": [0.00, 0.02, 0.04, 0.08],
        "fatigue_gain": [0.00, 0.10, 0.22, 0.35],
        "actual_ideal_alignment": [0.50, 0.70, 0.90, 1.00],
    }
    tasks = []
    for parameter, values in specs.items():
        for value in values:
            parameter_base = base.with_updates(**{parameter: value})
            for seed in range(seeds):
                tasks.extend(
                    _policy_pair_tasks(
                        parameter_base,
                        seed,
                        parameter=parameter,
                        value=value,
                    )
                )
    sensitivity = pd.DataFrame(_execute(tasks, jobs))
    sensitivity_delta = _paired_delta(
        sensitivity, ["parameter", "value", "seed"]
    )

    # 3. Ablation study.
    ablations = {
        "baseline": {},
        "no_preference_drift": {"use_preference_drift": False},
        "no_fatigue": {"use_fatigue": False, "fatigue_gain": 0.0},
        "no_novelty": {"use_novelty": False},
        "actual_equals_ideal": {"actual_ideal_alignment": 1.0},
    }
    tasks = []
    for name, changes in ablations.items():
        ablation_base = base.with_updates(**changes)
        for seed in range(seeds):
            tasks.extend(_policy_pair_tasks(ablation_base, seed, ablation=name))
    ablation = pd.DataFrame(_execute(tasks, jobs))
    ablation_delta = _paired_delta(ablation, ["ablation", "seed"])

    # 4. Continuous objective trade-off curve.
    tasks = []
    for alpha in np.round(np.linspace(0, 1, 11), 2):
        for seed in range(seeds):
            tasks.append((
                {"alpha": alpha, "seed": seed},
                base.with_updates(seed=seed, alpha=float(alpha)),
            ))
    alpha_sweep = pd.DataFrame(_execute(tasks, jobs))
    alpha_summary = _summarize(alpha_sweep, ["alpha"])

    outputs = {
        "baseline_raw": baseline,
        "baseline_summary": baseline_summary,
        "sensitivity_raw": sensitivity,
        "sensitivity_delta": sensitivity_delta,
        "ablation_raw": ablation,
        "ablation_delta": ablation_delta,
        "alpha_sweep_raw": alpha_sweep,
        "alpha_sweep_summary": alpha_summary,
    }

    for name, frame in outputs.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)

    baseline_table = baseline.groupby("policy")[METRICS].mean().round(4)
    ablation_table = (
        ablation_delta.groupby("ablation")[[
            "delta_CTR",
            "delta_satisfaction",
            "delta_mean_sessions",
            "delta_diversity",
            "delta_fatigue",
            "delta_preference_drift",
        ]]
        .mean()
        .round(4)
        .reset_index()
    )
    sensitivity_table = (
        sensitivity_delta.groupby(["parameter", "value"])[[
            "delta_CTR",
            "delta_satisfaction",
            "delta_mean_sessions",
        ]]
        .mean()
        .round(4)
        .reset_index()
    )
    baseline_table.to_csv(output_dir / "article_baseline_table.csv")
    ablation_table.to_csv(output_dir / "article_ablation_table.csv", index=False)
    sensitivity_table.to_csv(output_dir / "article_sensitivity_table.csv", index=False)

    return outputs
