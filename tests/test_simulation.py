from recommender_objective_lab import SimulationConfig, run_simulation


def test_simulation_is_deterministic_for_same_seed():
    config = SimulationConfig(seed=7, n_users=40, n_sessions=3, steps_per_session=2)
    assert run_simulation(config) == run_simulation(config)


def test_metrics_are_in_valid_ranges():
    config = SimulationConfig(seed=1, n_users=50, n_sessions=3, steps_per_session=2)
    metrics = run_simulation(config)
    for key in [
        "CTR",
        "satisfaction",
        "mean_return_probability",
        "diversity",
        "fatigue",
        "preference_drift",
        "survival_to_last_session",
    ]:
        assert 0.0 <= metrics[key] <= 1.0, (key, metrics[key])
    assert 1.0 <= metrics["mean_sessions"] <= config.n_sessions


def test_alpha_endpoints_run():
    base = SimulationConfig(seed=3, n_users=50, n_sessions=3, steps_per_session=2)
    engagement = run_simulation(base.with_updates(alpha=0.0))
    value = run_simulation(base.with_updates(alpha=1.0))
    assert engagement["CTR"] != value["CTR"]
