# Habr article fact-check

Checked: **2026-10-21**

This file records the evidence boundary for externally sourced claims in
`article/habr-draft.md`.

| Claim in article | Status | Primary / authoritative source | Boundary |
|---|---|---|---|
| Milli et al. frame engagement vs value as a measurement problem | ✅ Verified | https://arxiv.org/abs/2008.12623 | Their target construct is a latent notion of value; this does not define a universal welfare metric. |
| Google LRF takes short-term predictions and optimizes long-term satisfaction | ✅ Verified | https://arxiv.org/abs/2408.06512 and https://recsys.acm.org/recsys24/accepted-contributions/ | The authors report live experiments and describe deployment on YouTube. Do not infer the full YouTube ranking stack works this way. |
| Kleinberg et al. model inconsistent preferences with engagement-only observations | ✅ Verified | https://arxiv.org/abs/2202.11776 | Theoretical model, not a field estimate of real-world harm. |
| Khambatta et al. preregistered experiment has n=6488 | ✅ Verified | https://doi.org/10.1038/s41598-023-34192-x | Main experiment n=6488; primary comparison when actual/ideal recommendations differed uses n=2504. |
| Actual recommendations got more clicks than ideal recommendations | ✅ Verified | Scientific Reports article above | In primary comparison: 52% vs 40%, p<0.001. |
| Ideal recommendations increased “better off” / “time well spent” ratings | ✅ Verified | Scientific Reports article above | Self-reported outcomes in that experiment; not a universal definition of welfare. |
| Saig & Rosenfeld model positive/negative feedback and learn break policies | ✅ Verified | https://proceedings.mlr.press/v202/saig23a.html | Empirical demonstration is on semi-synthetic data, not a production-field experiment. |
| Social-media behavior can exhibit reward-learning dynamics | ✅ Verified | https://doi.org/10.1038/s41467-020-19607-x | 1,046,857 posts / 4,168 users + online experiment n=176. Does not establish recommender-caused preference drift. |
| Stray et al. describe value-oriented modifications of real recommenders | ✅ Verified | https://arxiv.org/abs/2107.10939 | Preprint/workshop-origin paper, not evidence that all platforms optimize these values. |
| Aristotle distinguishes instrumental and final ends | ✅ Verified | https://classics.mit.edu/Aristotle/nicomachaen.1.i.html | Philosophical analogy only. |
| Romans 7 presents a conflict between intended good and actual action | ✅ Verified | https://www.oca.org/readings/daily/2026/06/16/1 | Theological analogy only; not empirical evidence for actual/ideal preference models. |

## Internal experiment values

The values printed in the Habr draft were checked against committed reference CSVs:

- baseline: `results/reference/tables/article_baseline_table.csv`;
- alpha sweep: `results/reference/tables/alpha_sweep_summary.csv`;
- ablations: `results/reference/tables/article_ablation_table.csv`;
- sensitivity: `results/reference/tables/article_sensitivity_table.csv`.

Checked values include:

- CTR: 0.7023 vs 0.6073;
- satisfaction: 0.6817 vs 0.9078;
- mean sessions: 7.5306 vs 8.8260;
- baseline delta satisfaction: +0.2261;
- no-fatigue delta satisfaction: +0.0619;
- baseline delta mean sessions: +1.2954;
- no-fatigue delta mean sessions: +0.2810.

## Claims deliberately not made

The article must not state or imply that:

- YouTube/TikTok/etc. use the equations in this repository;
- engagement optimization is inherently harmful;
- the simulation estimates real platform effect sizes;
- recommender systems have been shown here to rewrite human preferences;
- synthetic satisfaction is a validated welfare measure;
- the value-aware policy is universally superior.
