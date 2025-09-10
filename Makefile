# Makefile for Superset Guest Token Generator

.PHONY: help install install-dev test test-unit test-integration test-mock test-error test-coverage lint format clean run serve-embed

# Default target
help:
	@echo "Available commands:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-mock      Run mock tests only"
	@echo "  test-error     Run error handling tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  lint           Run code linting"
	@echo "  format         Format code"
	@echo "  clean          Clean up generated files"
	@echo "  run            Run the FastAPI application"
	@echo "  serve-embed    Run the embed server"

# Installation targets
install:
	pip install -r requirements.txt

install-dev: install
	pip install -r test_requirements.txt

# Test targets
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/test_models.py tests/test_config.py tests/test_utils.py -v

test-integration:
	python -m pytest tests/test_api.py -v

test-mock:
	python -m pytest tests/test_mocks.py -v

test-error:
	python -m pytest tests/test_errors.py -v

test-coverage:
	python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing -v

# Code quality targets
lint:
	flake8 . --exclude=venv,__pycache__,.git
	bandit -r . -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true

format:
	autopep8 --in-place --recursive --exclude=venv .
	isort . --skip venv

# Utility targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf bandit-report.json
	rm -rf safety-report.json

# Run targets
run:
	python main.py

serve-embed:
	python serve_embed.py

# Development targets
dev-setup: install-dev
	@echo "Setting up development environment..."
	@echo "Creating .env file from template..."
	@if [ ! -f .env ]; then cp .env.test .env; fi
	@echo "Development environment ready!"

# CI/CD targets
ci-test: install-dev
	python -m pytest tests/ --cov=. --cov-report=xml --cov-report=term-missing -v

ci-lint: install-dev
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Documentation targets
docs:
	@echo "Generating API documentation..."
	@echo "Visit http://localhost:8000/docs when the server is running"

# Docker targets (if needed in the future)
docker-build:
	docker build -t superset-token-generator .

docker-run:
	docker run -p 8000:8000 superset-token-generator

