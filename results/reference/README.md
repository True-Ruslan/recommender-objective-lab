# Reference outputs

These files were generated from the verified `article` preset:

```bash
python -m recommender_objective_lab --preset article --out results/article --jobs 4
```

Configuration:

- 20 random seeds
- 400 users per seed
- 12 possible sessions per user
- 5 recommendation opportunities per session
- 8 content categories
- 1,200 synthetic items
- 20 candidates per recommendation

Reference baseline means:

| Metric | Engagement-first | Value-aware |
|---|---:|---:|
| CTR | 0.7023 | 0.6073 |
| Satisfaction | 0.6817 | 0.9078 |
| Mean sessions | 7.5306 | 8.8260 |
| Diversity | 0.3576 | 0.4978 |
| Fatigue | 0.1528 | 0.1293 |
| Preference drift | 0.2537 | 0.1470 |

The output is deterministic per seed but aggregate values may differ if code,
dependency behavior, model equations, or experiment settings are changed.
