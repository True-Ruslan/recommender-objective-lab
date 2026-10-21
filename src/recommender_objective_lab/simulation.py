from __future__ import annotations

from dataclasses import dataclass, replace
import numpy as np


@dataclass(frozen=True)
class SimulationConfig:
    seed: int = 0
    n_users: int = 400
    n_sessions: int = 12
    steps_per_session: int = 5
    n_categories: int = 8
    n_items: int = 1200
    candidate_k: int = 20

    # Objective mix: 0 = engagement-first, 1 = value-aware.
    alpha: float = 0.0

    # Environment dynamics.
    reinforcement: float = 0.04
    fatigue_gain: float = 0.22
    fatigue_decay: float = 0.86
    actual_ideal_alignment: float = 0.70

    use_preference_drift: bool = True
    use_fatigue: bool = True
    use_novelty: bool = True

    def with_updates(self, **kwargs: object) -> "SimulationConfig":
        return replace(self, **kwargs)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def _entropy_rows(counts: np.ndarray) -> np.ndarray:
    sums = counts.sum(axis=1, keepdims=True)
    p = np.divide(
        counts,
        sums,
        out=np.zeros_like(counts, dtype=float),
        where=sums > 0,
    )
    h = -(np.where(p > 0, p * np.log(np.clip(p, 1e-12, None)), 0)).sum(axis=1)
    return h / np.log(counts.shape[1])


def run_simulation(config: SimulationConfig) -> dict[str, float]:
    """Run one deterministic synthetic simulation.

    Interpretation boundary
    -----------------------
    This is a mechanism-demonstration environment, not a calibrated model of
    YouTube, TikTok, X, Pinterest, or any other real platform.

    Assumptions are explicit:
    - immediate clicks are driven by current preferences and item stimulus;
    - latent satisfaction is related to ideal preferences and item quality;
    - repeated exposure may create category-specific fatigue;
    - consumed items may slightly shift current preferences;
    - return probability depends on satisfaction, dwell, and fatigue.

    The experiment asks whether different objective functions can generate
    different trajectories *under those assumptions*.
    """
    c = config
    if not 0.0 <= c.alpha <= 1.0:
        raise ValueError("alpha must be between 0 and 1")
    if not 0.0 <= c.actual_ideal_alignment <= 1.0:
        raise ValueError("actual_ideal_alignment must be between 0 and 1")

    rng = np.random.default_rng(c.seed)

    # Catalog. Quality and stimulation are independent by construction so the
    # environment does not assume that engaging content is low quality.
    categories = rng.integers(0, c.n_categories, c.n_items)
    quality = rng.beta(2.2, 2.2, c.n_items)
    stimulus = rng.beta(2.0, 2.0, c.n_items)

    # Users have reflective/ideal preferences and noisier immediate preferences.
    ideal = rng.dirichlet(np.ones(c.n_categories) * 0.8, c.n_users)
    impulse = rng.dirichlet(np.ones(c.n_categories) * 0.8, c.n_users)
    actual = (
        c.actual_ideal_alignment * ideal
        + (1.0 - c.actual_ideal_alignment) * impulse
    )
    actual /= actual.sum(axis=1, keepdims=True)

    fatigue = np.zeros((c.n_users, c.n_categories))
    seen = np.zeros((c.n_users, c.n_categories), dtype=int)
    active = np.ones(c.n_users, dtype=bool)
    session_counts = np.zeros(c.n_users, dtype=int)

    total_impressions = 0
    total_clicks = 0
    total_dwell = 0.0
    satisfaction_sum = 0.0
    satisfaction_n = 0

    all_return_p: list[float] = []
    all_diversity: list[float] = []
    all_fatigue: list[float] = []
    all_drift: list[float] = []

    for session in range(c.n_sessions):
        active_idx = np.flatnonzero(active)
        if len(active_idx) == 0:
            break
        session_counts[active_idx] += 1

        dwell = np.zeros(c.n_users)
        satisfaction_total = np.zeros(c.n_users)
        clicked_count = np.zeros(c.n_users)

        for _ in range(c.steps_per_session):
            active_idx = np.flatnonzero(active)
            if len(active_idx) == 0:
                break

            candidates = rng.integers(
                0, c.n_items, size=(len(active_idx), c.candidate_k)
            )
            candidate_categories = categories[candidates]

            current_match = np.take_along_axis(
                actual[active_idx][:, None, :],
                candidate_categories[:, :, None],
                axis=2,
            )[:, :, 0]
            ideal_match = np.take_along_axis(
                ideal[active_idx][:, None, :],
                candidate_categories[:, :, None],
                axis=2,
            )[:, :, 0]

            if c.use_fatigue:
                local_fatigue = np.take_along_axis(
                    fatigue[active_idx][:, None, :],
                    candidate_categories[:, :, None],
                    axis=2,
                )[:, :, 0]
            else:
                local_fatigue = np.zeros_like(current_match)

            p_click = _sigmoid(
                -2.2
                + 5.2 * current_match
                + 2.2 * stimulus[candidates]
                - 1.1 * local_fatigue
            )
            predicted_dwell = np.clip(
                0.15
                + 0.9 * current_match
                + 0.7 * stimulus[candidates]
                - 0.25 * local_fatigue,
                0,
                1.7,
            )
            latent_satisfaction = np.clip(
                0.15
                + 1.7 * ideal_match
                + 0.65 * quality[candidates]
                - 0.45 * local_fatigue,
                0,
                1,
            )

            if c.use_novelty:
                seen_for_candidates = np.take_along_axis(
                    seen[active_idx][:, None, :],
                    candidate_categories[:, :, None],
                    axis=2,
                )[:, :, 0]
                novelty = np.exp(-0.35 * seen_for_candidates)
            else:
                novelty = np.zeros_like(current_match)

            engagement_score = 0.58 * p_click + 0.42 * (predicted_dwell / 1.7)

            if c.use_novelty:
                value_score = (
                    0.38 * p_click
                    + 0.47 * latent_satisfaction
                    + 0.15 * novelty
                )
            else:
                value_score = 0.45 * p_click + 0.55 * latent_satisfaction

            score = (1.0 - c.alpha) * engagement_score + c.alpha * value_score
            selected_j = np.argmax(score, axis=1)
            rows = np.arange(len(active_idx))
            selected_item = candidates[rows, selected_j]
            selected_cat = candidate_categories[rows, selected_j]
            selected_p_click = p_click[rows, selected_j]

            clicked = rng.random(len(active_idx)) < selected_p_click
            total_impressions += len(active_idx)

            # Exposure-related fatigue decays with time/interactions.
            fatigue[active_idx] *= c.fatigue_decay

            if clicked.any():
                click_rows = rows[clicked]
                users = active_idx[clicked]
                items = selected_item[clicked]
                cats = selected_cat[clicked]

                realized_dwell = np.clip(
                    predicted_dwell[click_rows, selected_j[clicked]]
                    + rng.normal(0, 0.12, clicked.sum()),
                    0,
                    1.7,
                )
                realized_satisfaction = np.clip(
                    latent_satisfaction[click_rows, selected_j[clicked]]
                    + rng.normal(0, 0.08, clicked.sum()),
                    0,
                    1,
                )

                dwell[users] += realized_dwell
                satisfaction_total[users] += realized_satisfaction
                clicked_count[users] += 1

                total_clicks += int(clicked.sum())
                total_dwell += float(realized_dwell.sum())
                satisfaction_sum += float(realized_satisfaction.sum())
                satisfaction_n += len(realized_satisfaction)

                seen[users, cats] += 1

                if c.use_fatigue:
                    fatigue[users, cats] += c.fatigue_gain * (0.5 + stimulus[items])

                if c.use_preference_drift:
                    learning_rate = c.reinforcement * (0.5 + stimulus[items])
                    actual[users] *= 1.0 - learning_rate[:, None]
                    actual[users, cats] += learning_rate
                    actual[users] /= actual[users].sum(axis=1, keepdims=True)

        active_idx = np.flatnonzero(active)
        avg_satisfaction = np.divide(
            satisfaction_total[active_idx],
            clicked_count[active_idx],
            out=np.full(len(active_idx), 0.45),
            where=clicked_count[active_idx] > 0,
        )
        avg_dwell = np.divide(
            dwell[active_idx],
            clicked_count[active_idx],
            out=np.zeros(len(active_idx)),
            where=clicked_count[active_idx] > 0,
        )
        avg_fatigue = fatigue[active_idx].mean(axis=1)

        # Synthetic retention/return model: this is an assumption, not an
        # empirical estimate of any platform's user-return function.
        p_return = _sigmoid(
            2.1
            + 2.1 * (avg_satisfaction - 0.5)
            + 0.35 * (avg_dwell - 0.5)
            - 2.3 * avg_fatigue
        )

        all_return_p.extend(p_return.tolist())
        all_diversity.extend(_entropy_rows(seen[active_idx]).tolist())
        all_fatigue.extend(avg_fatigue.tolist())
        all_drift.extend(
            (np.abs(actual[active_idx] - ideal[active_idx]).sum(axis=1) / 2).tolist()
        )

        if session < c.n_sessions - 1:
            returned = rng.random(len(active_idx)) < p_return
            active[active_idx[~returned]] = False

    return {
        "CTR": total_clicks / total_impressions,
        "dwell_per_impression": total_dwell / total_impressions,
        "satisfaction": satisfaction_sum / max(satisfaction_n, 1),
        "mean_return_probability": float(np.mean(all_return_p)),
        "diversity": float(np.mean(all_diversity)),
        "fatigue": float(np.mean(all_fatigue)),
        "preference_drift": float(np.mean(all_drift)),
        "survival_to_last_session": float((session_counts == c.n_sessions).mean()),
        "mean_sessions": float(session_counts.mean()),
    }
