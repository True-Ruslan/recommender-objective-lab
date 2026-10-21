from __future__ import annotations

import argparse
import os
from pathlib import Path

from .experiments import run_all_experiments
from .plotting import make_figures


PRESETS = {
    "quick": {"seeds": 3, "users": 100, "n_sessions": 6, "steps_per_session": 4},
    "article": {"seeds": 20, "users": 400, "n_sessions": 12, "steps_per_session": 5},
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reproduce synthetic recommender-objective experiments."
    )
    parser.add_argument(
        "--preset", choices=PRESETS, default="article",
        help="quick = smoke run; article = reference configuration",
    )
    parser.add_argument(
        "--out", type=Path, default=Path("results/run"),
        help="Output directory for CSV tables and figures",
    )
    parser.add_argument("--seeds", type=int, default=None)
    parser.add_argument("--users", type=int, default=None)
    parser.add_argument(
        "--jobs", type=int, default=max(1, min(4, (os.cpu_count() or 2) - 1)),
        help="Parallel worker processes (default: up to 4)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = dict(PRESETS[args.preset])
    if args.seeds is not None:
        settings["seeds"] = args.seeds
    if args.users is not None:
        settings["users"] = args.users

    tables_dir = args.out / "tables"
    figures_dir = args.out / "figures"

    run_all_experiments(tables_dir, jobs=args.jobs, **settings)
    figures = make_figures(tables_dir, figures_dir)

    print(f"Preset: {args.preset}")
    print(f"Workers: {args.jobs}")
    print(f"Results: {args.out.resolve()}")
    print(f"Figures: {len(figures)}")
    print("Key table: article_baseline_table.csv")
