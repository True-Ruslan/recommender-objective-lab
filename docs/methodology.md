# Methodology

## Research question

Can two recommendation policies operating in the same synthetic environment
produce different short- and long-horizon outcomes when they optimize different
objective functions?

The experiment deliberately tests a **mechanism**, not a real-world platform.

## User model

Each user has two category distributions:

- `actual`: immediate/current preference, used in click propensity;
- `ideal`: reflective preference, used as one ingredient in latent satisfaction.

The distinction is a modeling choice inspired by work on actual versus ideal
preferences. It is not claimed to be a complete theory of human preference.

## Item model

Each item has:

- category;
- quality;
- stimulus.

Quality and stimulus are independently sampled. This prevents the experiment
from baking in the assumption that more stimulating content is lower quality.

## Behavioral equations

Immediate click probability depends on current category match, stimulus, and
(optional) fatigue. Dwell time follows similar short-horizon signals.

Latent satisfaction depends on ideal category match, item quality, and fatigue.
It is not directly observed by a production recommender in this simulation; it
is used to construct and evaluate the value-aware policy.

## Policies

Engagement-first:

```python
engagement_score = 0.58 * p_click + 0.42 * normalized_dwell
```

Value-aware:

```python
value_score = (
    0.38 * p_click
    + 0.47 * latent_satisfaction
    + 0.15 * novelty
)
```

The objective sweep interpolates between them:

```python
score = (1 - alpha) * engagement_score + alpha * value_score
```

No claim is made that these coefficients are optimal for a real service.

## Dynamic mechanisms

The baseline environment includes two delayed mechanism:

1. preference drift: consumed content slightly shifts current preferences;
2. fatigue: repeated exposure to a category creates a decaying cost.

Ablations remove these mechanisms one at a time.

## Return model

Synthetic return probability increases with session satisfaction and dwell, and
decreases with accumulated fatigue. This function is an explicit assumption.
The resulting retention values are **illustrative**, not estimates of real-user
retention.

## Robustness protocol

Article preset:

- 20 random seeds;
- 400 users per seed;
- up to 12 sessions per user;
- 5 recommendation opportunities per session;
- 8 categories;
- 1,200 items;
- 20 candidates per recommendation.

One-factor-at-a-time sensitivity ranges:

- reinforcement: 0.00, 0.02, 0.04, 0.08;
- fatigue gain: 0.00, 0.10, 0.22, 0.35;
- actual/ideal alignment: 0.50, 0.70, 0.90, 1.00.

Ablations:

- no preference drift;
- no fatigue;
- no novelty term;
- actual preferences equal ideal preferences.

## What the simulation can support

It can show that, under explicit assumptions, optimizing different proxy
objectives can produce systematically different trajectories and trade-offs.

## What the simulation cannot support

It cannot establish that any named platform manipulates users, that engagement
optimization is inherently harmful, that fatigue takes this exact functional
form in real systems, or that the value-aware objective is ethically optimal.
