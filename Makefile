# Makefile for Modular HTTP Client

.PHONY: help clean build install test lint type-check coverage docs dev-install package-structure all

# Default target
help:
	@echo "Available commands:"
	@echo "  help           - Show this help message"
	@echo "  clean          - Clean build artifacts"
	@echo "  build          - Build package"
	@echo "  install        - Install package in development mode"
	@echo "  dev-install    - Install with development dependencies"
	@echo "  test           - Run tests"
	@echo "  lint           - Run code linting"
	@echo "  type-check     - Run type checking"
	@echo "  coverage       - Run tests with coverage"
	@echo "  docs           - Build documentation"
	@echo "  package-structure - Create package directory structure"
	@echo "  all            - Run clean, build, test, lint"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Build package
build:
	@echo "Building package..."
	python -m build

# Build wheel only
wheel:
	@echo "Building wheel..."
	python -m build --wheel

# Build source distribution only
sdist:
	@echo "Building source distribution..."
	python -m build --sdist

# Install in development mode
install:
	@echo "Installing package in development mode..."
	pip install -e .

# Install with development dependencies
dev-install:
	@echo "Installing with development dependencies..."
	pip install -e .[dev]

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v

# Run tests with coverage
coverage:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=http_service --cov-report=html --cov-report=term

# Run linting
lint:
	@echo "Running code linting..."
	black .
	isort .
	flake8 .

# Run type checking
type-check:
	@echo "Running type checking..."
	mypy .

# Build documentation
docs:
	@echo "Building documentation..."
	cd docs && make html

# Create package structure
package-structure:
	@echo "Creating package structure..."
	mkdir -p modular_http_client
	@if [ ! -f modular_http_client/__init__.py ]; then \
		echo '"""Modular HTTP Client Package."""' > modular_http_client/__init__.py; \
		echo '' >> modular_http_client/__init__.py; \
		echo '__version__ = "1.0.0"' >> modular_http_client/__init__.py; \
	fi
	@for file in http_client.py config.py models.py decorators.py utils.py circuit_breaker.py; do \
		if [ -f $$file ]; then \
			mv $$file modular_http_client/; \
			echo "Moved: $$file -> modular_http_client/$$file"; \
		fi; \
	done

# Run all checks
all: clean build test lint

# Development workflow
dev: dev-install test lint type-check

# Quick test
quick-test:
	@echo "Running quick tests..."
	python -m pytest tests/ -x -v

# Format code
format:
	@echo "Formatting code..."
	black .
	isort .

# Check code quality
check: lint type-check test

# Install dependencies
deps:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Install all dependencies
deps-all:
	@echo "Installing all dependencies..."
	pip install -r requirements.txt
	pip install -e .[dev,docs]

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  # On Unix/macOS"
	@echo "  venv\\Scripts\\activate     # On Windows"

# Publish to PyPI (dry run)
publish-test:
	@echo "Publishing to TestPyPI (dry run)..."
	python -m twine upload --repository testpypi dist/*

# Publish to PyPI
publish:
	@echo "Publishing to PyPI..."
	python -m twine upload dist/*

# Show package info
info:
	@echo "Package information:"
	@python -c "import setuptools; print(setuptools.find_packages())"

# Show installed packages
list-packages:
	@echo "Installed packages:"
	@pip list

# Run example
example:
	@echo "Running example..."
	python example_usage.py
