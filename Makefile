.PHONY: install test quick reproduce clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

quick:
	python -m recommender_objective_lab --preset quick --out results/quick

reproduce:
	python -m recommender_objective_lab --preset article --out results/article

clean:
	rm -rf results/quick results/article .pytest_cache
