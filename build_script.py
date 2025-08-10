#!/usr/bin/env python3
"""
Build script for the HTTP Service package.
Provides comprehensive build, test, and development commands.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and handle errors."""
    print(f"Running: {command}")
    if description:
        print(f"Description: {description}")
    
    # Use subprocess.run with shell=True for complex commands
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
    
    return result


def clean_build_artifacts():
    """Clean build artifacts and temporary files."""
    print("Cleaning build artifacts...")
    
    # Directories to remove
    dirs_to_remove = [
        "build", "dist", "__pycache__", ".pytest_cache", 
        ".coverage", "htmlcov", ".mypy_cache", ".tox",
        "*.egg-info", "*.egg"
    ]
    
    # Files to remove
    files_to_remove = [
        "*.pyc", "*.pyo", "*.pyd", ".coverage", "coverage.xml",
        "*.so", "*.dll", "*.dylib"
    ]
    
    for pattern in dirs_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                print(f"Removed directory: {path}")
            else:
                path.unlink(missing_ok=True)
                print(f"Removed file: {path}")
    
    for pattern in files_to_remove:
        for path in Path(".").rglob(pattern):
            path.unlink(missing_ok=True)
            print(f"Removed file: {path}")


def build_package():
    """Build the package."""
    print("Building package...")
    # Use the build module directly
    run_command("python -m build", "Build source distribution and wheel")


def build_wheel():
    """Build wheel distribution."""
    print("Building wheel...")
    run_command("python -m build --wheel", "Build wheel distribution only")


def build_sdist():
    """Build source distribution."""
    print("Building source distribution...")
    run_command("python -m build --sdist", "Build source distribution only")


def install_package():
    """Install package in development mode."""
    print("Installing package in development mode...")
    run_command("pip install -e .", "Install package in editable mode")


def install_dev_dependencies():
    """Install development dependencies."""
    print("Installing development dependencies...")
    run_command("pip install -e .[dev]", "Install package with development dependencies")


def install_test_dependencies():
    """Install testing dependencies."""
    print("Installing testing dependencies...")
    run_command("pip install -e .[test]", "Install package with testing dependencies")


def install_all_dependencies():
    """Install all dependencies."""
    print("Installing all dependencies...")
    run_command("pip install -e .[all]", "Install package with all dependencies")


def run_tests():
    """Run tests."""
    print("Running tests...")
    run_command("python -m pytest tests/ -v", "Run all tests with verbose output")


def run_tests_with_coverage():
    """Run tests with coverage."""
    print("Running tests with coverage...")
    run_command("python -m pytest tests/ --cov=http_service --cov-report=html --cov-report=term-missing", 
                "Run tests with coverage reporting")


def run_linting():
    """Run linting checks."""
    print("Running linting...")
    
    # Run black
    run_command("black --check --diff http_service/ tests/", "Check code formatting with black")
    
    # Run isort
    run_command("isort --check-only --diff http_service/ tests/", "Check import sorting with isort")
    
    # Run flake8
    run_command("flake8 http_service/ tests/", "Run flake8 linting")
    
    # Run mypy
    run_command("mypy http_service/", "Run type checking with mypy")


def run_type_checking():
    """Run type checking."""
    print("Running type checking...")
    run_command("mypy http_service/", "Run type checking with mypy")


def run_security_checks():
    """Run security checks."""
    print("Running security checks...")
    
    # Run bandit
    run_command("bandit -r http_service/", "Run security analysis with bandit")
    
    # Run safety
    run_command("safety check", "Check for known security vulnerabilities")
    
    # Run pip-audit
    run_command("pip-audit", "Audit dependencies for security issues")


def run_performance_tests():
    """Run performance tests."""
    print("Running performance tests...")
    run_command("python -m pytest tests/ -m performance", "Run performance tests")


def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    run_command("python -m pytest tests/ -m integration", "Run integration tests")


def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    run_command("python -m pytest tests/ -m unit", "Run unit tests")


def run_async_tests():
    """Run async tests."""
    print("Running async tests...")
    run_command("python -m pytest tests/ -m asyncio", "Run async tests")


def build_docs():
    """Build documentation."""
    print("Building documentation...")
    run_command("sphinx-build -b html docs/ docs/_build/html", "Build HTML documentation")


def create_package_structure():
    """Create package structure for distribution."""
    print("Creating package structure...")
    
    # Create modular_http_client directory
    package_dir = Path("modular_http_client")
    package_dir.mkdir(exist_ok=True)
    
    # Copy files to package directory
    files_to_copy = [
        "http_service/",
        "tests/",
        "README.md",
        "LICENSE",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-test.txt",
        "requirements-docs.txt",
        "pyproject.toml",
        "setup.py",
        "MANIFEST.in",
        "Makefile",
        "build_script.py",
        "example_usage.py",
        "env_example.env"
    ]
    
    for file_name in files_to_copy:
        source = Path(file_name)
        if source.exists():
            if source.is_dir():
                if source.name == "http_service":
                    # Copy http_service to modular_http_client/http_service
                    dest = package_dir / "http_service"
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
                else:
                    # Copy other directories as-is
                    dest = package_dir / source.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
            else:
                # Copy files
                shutil.copy2(source, package_dir)
            print(f"Moved: {file_name} -> modular_http_client/{file_name}")
    
    print("Package structure created in modular_http_client/")


def show_help():
    """Show help information."""
    print("Usage: python build_script.py <command>")
    print("Commands:")
    print("  clean          - Clean build artifacts")
    print("  build          - Build package")
    print("  wheel          - Build wheel distribution")
    print("  sdist          - Build source distribution")
    print("  install        - Install in development mode")
    print("  install-dev    - Install with dev dependencies")
    print("  install-test   - Install with test dependencies")
    print("  install-all    - Install with all dependencies")
    print("  test           - Run tests")
    print("  test-cov       - Run tests with coverage")
    print("  test-perf      - Run performance tests")
    print("  test-integration - Run integration tests")
    print("  test-unit      - Run unit tests")
    print("  test-async     - Run async tests")
    print("  lint           - Run linting")
    print("  type-check     - Run type checking")
    print("  security       - Run security checks")
    print("  docs           - Build documentation")
    print("  structure      - Create package structure")
    print("  all            - Run clean, build, test, lint")
    print("  dev-setup      - Complete development setup")
    print("  help           - Show this help message")


def run_all():
    """Run clean, build, test, and lint."""
    print("Running complete build process...")
    clean_build_artifacts()
    build_package()
    run_tests()
    run_linting()
    print("Complete build process finished successfully!")


def dev_setup():
    """Complete development setup."""
    print("Setting up development environment...")
    clean_build_artifacts()
    install_all_dependencies()
    run_tests()
    run_linting()
    run_security_checks()
    print("Development environment setup complete!")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        "clean": clean_build_artifacts,
        "build": build_package,
        "wheel": build_wheel,
        "sdist": build_sdist,
        "install": install_package,
        "install-dev": install_dev_dependencies,
        "install-test": install_test_dependencies,
        "install-all": install_all_dependencies,
        "test": run_tests,
        "test-cov": run_tests_with_coverage,
        "test-perf": run_performance_tests,
        "test-integration": run_integration_tests,
        "test-unit": run_unit_tests,
        "test-async": run_async_tests,
        "lint": run_linting,
        "type-check": run_type_checking,
        "security": run_security_checks,
        "docs": build_docs,
        "structure": create_package_structure,
        "all": run_all,
        "dev-setup": dev_setup,
        "help": show_help,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
