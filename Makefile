.PHONY: test mock audit

test:
	python -m pytest -q

mock:
	python scripts/run_experiment.py --config configs/experiments/EXP-001.yaml --mode mock

audit:
	python scripts/scientific_audit.py --config configs/experiments/EXP-001.yaml
