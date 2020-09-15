test:
	python -m pytest --cov=pss1830exec --cov-report term-missing --pylint --pylint-error-types=EF

lint:
	pylint pss1830exec/ tests/

checklist: lint test

.PHONY: test lint checklist