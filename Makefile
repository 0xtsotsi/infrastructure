.PHONY: healthcheck test lint

healthcheck:
	@cd scripts/healthcheck && python3 checker.py

test:
	python3 -m pytest tests/ -v

lint:
	python3 -m ruff check scripts/ tests/ || true
