# Makefile for HTTP Service
# Provides convenient commands for building, testing, and development

.PHONY: help clean build install test lint docs security dev-setup all

# Default target
help:
	@echo "HTTP Service - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install        - Install package in development mode"
	@echo "  install-dev    - Install with development dependencies"
	@echo "  install-test   - Install with testing dependencies"
	@echo "  install-all    - Install with all dependencies"
	@echo ""
	@echo "Building:"
	@echo "  build          - Build package (wheel and sdist)"
	@echo "  wheel          - Build wheel distribution"
	@echo "  sdist          - Build source distribution"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-cov       - Run tests with coverage"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-async     - Run async tests only"
	@echo "  test-perf      - Run performance tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run all linting checks"
	@echo "  format         - Format code with black and isort"
	@echo "  type-check     - Run type checking"
	@echo "  security       - Run security checks"
	@echo ""
	@echo "Documentation:"
	@echo "  docs           - Build documentation"
	@echo ""
	@echo "Development:"
	@echo "  clean          - Clean build artifacts"
	@echo "  dev-setup      - Complete development setup"
	@echo "  all            - Run clean, build, test, lint"
	@echo ""

# Installation commands
install:
	python -m pip install -e .

install-dev:
	python -m pip install -e .[dev]

install-test:
	python -m pip install -e .[test]

install-all:
	python -m pip install -e .[all]

# Building commands
build:
	python -m build

wheel:
	python -m build --wheel

sdist:
	python -m build --sdist

# Testing commands
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=http_service --cov-report=html --cov-report=term-missing

test-unit:
	python -m pytest tests/ -m unit -v

test-integration:
	python -m pytest tests/ -m integration -v

test-async:
	python -m pytest tests/ -m asyncio -v

test-perf:
	python -m pytest tests/ -m performance -v

# Code quality commands
lint:
	@echo "Running linting checks..."
	black --check --diff http_service/ tests/
	isort --check-only --diff http_service/ tests/
	flake8 http_service/ tests/
	mypy http_service/

format:
	@echo "Formatting code..."
	black http_service/ tests/
	isort http_service/ tests/

type-check:
	mypy http_service/

security:
	@echo "Running security checks..."
	bandit -r http_service/
	safety check
	pip-audit

# Documentation
docs:
	sphinx-build -b html docs/ docs/_build/html

# Development commands
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .tox/

dev-setup: clean install-all test lint security
	@echo "Development environment setup complete!"

all: clean build test lint
	@echo "Complete build process finished successfully!"

# Quick commands for common tasks
quick-test:
	python -m pytest tests/ -x

quick-lint:
	black --check http_service/ tests/
	flake8 http_service/ tests/

# Docker commands (if needed)
docker-build:
	docker build -t http-service .

docker-run:
	docker run -it http-service

# Release commands
release-check: clean build test lint security
	@echo "Release checks passed!"

release: release-check
	@echo "Creating release..."
	git tag -a v$(shell python -c "import http_service; print(http_service.__version__)") -m "Release v$(shell python -c "import http_service; print(http_service.__version__)")"
	git push --tags

# Development workflow
dev: install-dev
	@echo "Development environment ready!"

watch-test:
	@echo "Watching for changes and running tests..."
	watchmedo auto-restart --patterns="*.py" --recursive -- python -m pytest tests/ -v

# Environment setup
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

venv-dev: venv
	@echo "Installing development dependencies in virtual environment..."
	venv/bin/pip install -e .[dev]

# Utility commands
check-deps:
	pip list --outdated

update-deps:
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

freeze:
	pip freeze > requirements-frozen.txt

# Help for specific commands
help-install:
	@echo "Installation Commands:"
	@echo "  make install        - Install package in development mode"
	@echo "  make install-dev    - Install with development dependencies"
	@echo "  make install-test   - Install with testing dependencies"
	@echo "  make install-all    - Install with all dependencies"

help-test:
	@echo "Testing Commands:"
	@echo "  make test           - Run all tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-async     - Run async tests only"
	@echo "  make test-perf      - Run performance tests"
	@echo "  make quick-test     - Run tests and stop on first failure"

help-lint:
	@echo "Linting Commands:"
	@echo "  make lint           - Run all linting checks"
	@echo "  make format         - Format code with black and isort"
	@echo "  make type-check     - Run type checking"
	@echo "  make security       - Run security checks"
	@echo "  make quick-lint     - Run basic linting checks"
