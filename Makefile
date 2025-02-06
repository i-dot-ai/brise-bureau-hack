-include .env
export


install:
	poetry install --with fastapi --no-root

pre-commit-install:
	pre-commit install


test:
	
	cd backend && poetry install --with dev,fastapi --no-root && poetry run python -m pytest --cov=tests -v --cov-report=term-missing --cov-fail-under=0
	cd frontend && poetry install --with dev,streamlit --no-root && poetry run python -m pytest --cov=tests -v --cov-report=term-missing --cov-fail-under=0


run_frontend:
	poetry run python frontend/app/run.py

run_backend:
	poetry run python backend/main.py

run:
	docker compose up -d --wait

stop:
	docker compose down


.PHONY: lint
lint:  ## Check code formatting & linting
	poetry run ruff format . --check
	poetry run ruff check .

.PHONY: format
format:  ## Format and fix code
	poetry run ruff format .
	poetry run ruff check . --fix

.PHONY: safe
safe:  ##
	poetry run bandit -ll -r ./backend
	poetry run bandit -ll -r ./frontend

