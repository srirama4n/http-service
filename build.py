#!/usr/bin/env python3
"""
Build script for the HTTP Client package.
Provides additional build tasks and utilities.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, check=True, capture_output=True):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(
        command, shell=True, check=check, capture_output=capture_output, text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed: {path}")


def build_package():
    """Build the package."""
    print("Building package...")
    run_command("python -m build")


def build_wheel():
    """Build wheel distribution."""
    print("Building wheel...")
    run_command("python -m build --wheel")


def build_sdist():
    """Build source distribution."""
    print("Building source distribution...")
    run_command("python -m build --sdist")


def install_package():
    """Install the package in development mode."""
    print("Installing package in development mode...")
    run_command("pip install -e .")


def install_dev_dependencies():
    """Install development dependencies."""
    print("Installing development dependencies...")
    run_command("pip install -e .[dev]")


def run_tests():
    """Run tests."""
    print("Running tests...")
    run_command("python -m pytest tests/")


def run_linting():
    """Run code linting."""
    print("Running linting...")
    run_command("black .")
    run_command("isort .")
    run_command("flake8 .")


def run_type_checking():
    """Run type checking."""
    print("Running type checking...")
    run_command("mypy .")


def run_coverage():
    """Run tests with coverage."""
    print("Running tests with coverage...")
    run_command("python -m pytest tests/ --cov=modular_http_client --cov-report=html")


def create_package_structure():
    """Create the package directory structure."""
    print("Creating package structure...")
    
    # Create package directory
    package_dir = Path("modular_http_client")
    package_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    init_file = package_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Modular HTTP Client Package."""\n\n__version__ = "1.0.0"\n')
    
    # Move source files to package directory
    source_files = [
        "http_client.py",
        "config.py", 
        "models.py",
        "decorators.py",
        "utils.py",
        "circuit_breaker.py"
    ]
    
    for file_name in source_files:
        if Path(file_name).exists():
            shutil.move(file_name, package_dir / file_name)
            print(f"Moved: {file_name} -> modular_http_client/{file_name}")


def main():
    """Main build function."""
    if len(sys.argv) < 2:
        print("Usage: python build.py <command>")
        print("Commands:")
        print("  clean          - Clean build artifacts")
        print("  build          - Build package")
        print("  wheel          - Build wheel distribution")
        print("  sdist          - Build source distribution")
        print("  install        - Install in development mode")
        print("  install-dev    - Install with dev dependencies")
        print("  test           - Run tests")
        print("  lint           - Run linting")
        print("  type-check     - Run type checking")
        print("  coverage       - Run tests with coverage")
        print("  structure      - Create package structure")
        print("  all            - Run clean, build, test, lint")
        return
    
    command = sys.argv[1]
    
    if command == "clean":
        clean_build()
    elif command == "build":
        build_package()
    elif command == "wheel":
        build_wheel()
    elif command == "sdist":
        build_sdist()
    elif command == "install":
        install_package()
    elif command == "install-dev":
        install_dev_dependencies()
    elif command == "test":
        run_tests()
    elif command == "lint":
        run_linting()
    elif command == "type-check":
        run_type_checking()
    elif command == "coverage":
        run_coverage()
    elif command == "structure":
        create_package_structure()
    elif command == "all":
        clean_build()
        build_package()
        run_tests()
        run_linting()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
