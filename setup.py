"""
Setup configuration for the HTTP Client package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="http-service",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive, robust HTTP client service built with HTTPX",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/modular-http-client",
    packages=find_packages(include=['http_service', 'http_service.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: HTTP Clients",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "pytest-xdist>=3.0.0,<4.0.0",
            "black>=23.0.0,<24.0.0",
            "isort>=5.12.0,<6.0.0",
            "flake8>=6.0.0,<7.0.0",
            "mypy>=1.0.0,<2.0.0",
            "pre-commit>=3.0.0,<4.0.0",
            "bandit>=1.7.0,<2.0.0",
            "safety>=2.0.0,<3.0.0",
        ],
        "test": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "pytest-xdist>=3.0.0,<4.0.0",
            "responses>=0.23.0,<1.0.0",
            "aioresponses>=0.7.0,<1.0.0",
        ],
        "lint": [
            "black>=23.0.0,<24.0.0",
            "isort>=5.12.0,<6.0.0",
            "flake8>=6.0.0,<7.0.0",
            "mypy>=1.0.0,<2.0.0",
            "bandit>=1.7.0,<2.0.0",
            "safety>=2.0.0,<3.0.0",
        ],
        "security": [
            "bandit>=1.7.0,<2.0.0",
            "safety>=2.0.0,<3.0.0",
            "pip-audit>=2.4.0,<3.0.0",
        ],
        "performance": [
            "pytest-benchmark>=4.0.0,<5.0.0",
            "memory-profiler>=0.60.0,<1.0.0",
            "psutil>=5.9.0,<6.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0,<7.0.0",
            "sphinx-rtd-theme>=1.2.0,<2.0.0",
            "myst-parser>=1.0.0,<2.0.0",
            "sphinx-autodoc-typehints>=1.23.0,<2.0.0",
        ],
        "all": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "pytest-xdist>=3.0.0,<4.0.0",
            "responses>=0.23.0,<1.0.0",
            "aioresponses>=0.7.0,<1.0.0",
            "black>=23.0.0,<24.0.0",
            "isort>=5.12.0,<6.0.0",
            "flake8>=6.0.0,<7.0.0",
            "mypy>=1.0.0,<2.0.0",
            "pre-commit>=3.0.0,<4.0.0",
            "bandit>=1.7.0,<2.0.0",
            "safety>=2.0.0,<3.0.0",
            "pip-audit>=2.4.0,<3.0.0",
            "sphinx>=6.0.0,<7.0.0",
            "sphinx-rtd-theme>=1.2.0,<2.0.0",
            "myst-parser>=1.0.0,<2.0.0",
            "sphinx-autodoc-typehints>=1.23.0,<2.0.0",
            "pytest-benchmark>=4.0.0,<5.0.0",
            "memory-profiler>=0.60.0,<1.0.0",
            "psutil>=5.9.0,<6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "http-service=http_service.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "http_service": ["*.env", "*.txt", "*.md"],
    },
    keywords="http client httpx retry circuit-breaker rate-limiting authentication ssl tls",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/modular-http-client/issues",
        "Source": "https://github.com/yourusername/modular-http-client",
        "Documentation": "https://modular-http-client.readthedocs.io/",
        "Changelog": "https://github.com/yourusername/modular-http-client/blob/master/CHANGELOG.md",
    },
)
