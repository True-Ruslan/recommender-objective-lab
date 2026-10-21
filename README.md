# Recommender Objective Lab

A small reproducible **synthetic** experiment about objective design in
recommender systems: what changes when a ranker optimizes short-term engagement
versus a broader, value-aware objective?

The project is intended as a research/reproducibility artifact for a technical
article. It is **not** a calibrated model of YouTube, TikTok, X, Pinterest, or
any other real platform.

## Core question

Suppose a recommender can optimize either:

```python
engagement_score = (
    0.58 * p_click
    + 0.42 * normalized_dwell
)
```

or a broader synthetic objective:

```python
value_score = (
    0.38 * p_click
    + 0.47 * latent_satisfaction
    + 0.15 * novelty
)
```

If short-term observable behavior and long-horizon user value are not identical,
do the two objective functions produce different trajectories?

## Reference result

Using the `article` preset (20 seeds × 400 users), the baseline simulation
produces approximately:

| Metric | Engagement-first | Value-aware |
|---|---:|---:|
| CTR | 0.702 | 0.607 |
| Satisfaction | 0.682 | 0.908 |
| Mean sessions | 7.53 | 8.83 |
| Diversity | 0.358 | 0.498 |
| Fatigue | 0.153 | 0.129 |
| Preference drift | 0.254 | 0.147 |

These are **model outputs**, not estimates of real platform metrics.

The important result is the trade-off, not the specific values: the
engagement-first policy does better on the metric it was built to optimize,
while the value-aware policy scores better on the broader synthetic outcome.

## What makes the experiment useful

The repository includes:

- baseline policy comparison;
- 20-seed robustness analysis;
- one-factor-at-a-time sensitivity analysis;
- ablation study;
- continuous objective sweep `alpha ∈ [0, 1]`;
- article-facing CSV tables;
- reproducible figures;
- explicit claim/interpretation boundaries.

A particularly useful ablation is removing fatigue. In the baseline model the
value-aware advantage in satisfaction is large; without fatigue it becomes much
smaller. This suggests that the short-vs-long-term divergence in this environment
is driven strongly by **delayed consumption costs**, not just by preference drift.

## Repository layout

```text
.
├── src/recommender_objective_lab/
│   ├── simulation.py      # synthetic environment and rankers
│   ├── experiments.py     # baseline, robustness, ablations, alpha sweep
│   ├── plotting.py        # article figures
│   └── cli.py             # reproducible CLI
├── tests/
├── docs/
│   ├── methodology.md
│   └── claim-boundaries.md
├── results/reference/     # committed reference outputs
├── REFERENCES.md
├── pyproject.toml
└── Makefile
```

## Installation

Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Or with requirements:

```bash
python -m pip install -r requirements.txt
```

## Reproduce

Fast smoke run:

```bash
python -m recommender_objective_lab --preset quick --out results/quick
```

Article/reference configuration:

```bash
python -m recommender_objective_lab --preset article --out results/article
```

Equivalent Make targets:

```bash
make quick
make reproduce
```

Runs are parallelized across independent configurations by default (up to 4 worker processes); use `--jobs 1` for fully sequential execution.

The `article` preset uses:

- 20 random seeds;
- 400 users per seed;
- 12 possible sessions;
- 5 recommendation opportunities/session;
- 8 content categories;
- 1,200 items;
- 20 candidates per recommendation.

## Test

```bash
python -m pytest -q
```

## Main figures

The reproduction command generates:

1. CTR vs satisfaction objective trade-off;
2. objective mix vs mean sessions;
3. sensitivity heatmaps;
4. ablation deltas for satisfaction, sessions and CTR.

## Interpretation boundary

This project demonstrates a mechanism under explicit assumptions.

It does **not** demonstrate that:

- a named social platform manipulates users;
- engagement optimization is inherently harmful;
- real preference formation follows the equations used here;
- the synthetic satisfaction function is an ethically correct definition of welfare;
- the coefficients used here are production-optimal.

Read [`docs/methodology.md`](docs/methodology.md) for the model assumptions and
[`docs/claim-boundaries.md`](docs/claim-boundaries.md) before making claims from
the results.

## Research context

The experiment is motivated by work on:

- click/engagement proxies versus user value;
- actual versus ideal preferences;
- long-term recommendation objectives;
- sustainable engagement and fatigue;
- reward learning and feedback loops.

Primary references are collected in [`REFERENCES.md`](REFERENCES.md).

## License

MIT.
