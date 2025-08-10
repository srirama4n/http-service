# Installation Guide

This guide covers how to install HTTP Service and its dependencies.

## 📦 Basic Installation

### From PyPI

```bash
pip install http-service
```

### From Source

```bash
git clone https://github.com/srirama4n/http-service.git
cd http-service
pip install -e .
```

## 🔧 Development Installation

For development and contributing to HTTP Service:

```bash
# Clone the repository
git clone https://github.com/srirama4n/http-service.git
cd http-service

# Install with development dependencies
pip install -e .[dev]

# Or install with all dependencies
pip install -e .[all]
```

## 📋 Dependency Groups

HTTP Service provides several optional dependency groups:

### Core Dependencies (Always Installed)

- `httpx>=0.25.0,<1.0.0` - HTTP client library
- `python-dotenv>=1.0.0,<2.0.0` - Environment variable management
- `certifi>=2023.0.0` - SSL/TLS certificate handling
- `urllib3>=2.0.0,<3.0.0` - HTTP utilities

### Development Dependencies (`[dev]`)

```bash
pip install http-service[dev]
```

Includes:
- **Testing**: pytest, pytest-asyncio, pytest-cov, pytest-mock, pytest-xdist
- **Code Quality**: black, isort, flake8, mypy, pre-commit
- **Security**: bandit, safety, pip-audit
- **Documentation**: sphinx, sphinx-rtd-theme, myst-parser

### Testing Dependencies (`[test]`)

```bash
pip install http-service[test]
```

Includes:
- pytest and related testing tools
- HTTP mocking libraries (responses, aioresponses)
- Performance testing tools

### Documentation Dependencies (`[docs]`)

```bash
pip install http-service[docs]
```

Includes:
- Sphinx documentation generator
- Theme and extensions

### Security Dependencies (`[security]`)

```bash
pip install http-service[security]
```

Includes:
- bandit - Security analysis
- safety - Vulnerability checking
- pip-audit - Dependency auditing

### Performance Dependencies (`[performance]`)

```bash
pip install http-service[performance]
```

Includes:
- pytest-benchmark - Performance testing
- memory-profiler - Memory usage analysis
- psutil - System monitoring

### All Dependencies (`[all]`)

```bash
pip install http-service[all]
```

Includes all optional dependencies from all groups.

## 🐍 Python Version Requirements

- **Minimum**: Python 3.8
- **Recommended**: Python 3.9+
- **Latest**: Python 3.12

## 🔒 Security Considerations

### SSL/TLS Support

HTTP Service includes comprehensive SSL/TLS support:

```bash
# Install with SSL support (included by default)
pip install http-service

# Additional SSL utilities
pip install certifi urllib3
```

### Security Tools

For development environments, install security tools:

```bash
pip install http-service[security]
```

This includes:
- **bandit** - Static security analysis
- **safety** - Check for known vulnerabilities
- **pip-audit** - Audit dependencies

## 🌐 Virtual Environment

We recommend using a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Unix/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Install HTTP Service
pip install http-service[dev]
```

## 🐳 Docker Installation

### Using Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "-m", "http_service.cli"]
```

### Using Docker Compose

```yaml
version: '3.8'
services:
  http-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HTTP_BASE_URL=https://api.example.com
```

## 🔧 Build Tools

### Using Make

```bash
# Install with development dependencies
make install-dev

# Run tests
make test

# Run linting
make lint

# Complete development setup
make dev-setup
```

### Using Build Script

```bash
# Install with all dependencies
python build_script.py install-all

# Run tests with coverage
python build_script.py test-cov

# Run security checks
python build_script.py security
```

## 📦 Package Managers

### Poetry

```bash
# Add to pyproject.toml
[tool.poetry.dependencies]
http-service = "^1.0.0"

# Install
poetry install
```

### Pipenv

```bash
# Install
pipenv install http-service

# Install with dev dependencies
pipenv install http-service[dev]
```

## 🔍 Verification

After installation, verify it works:

```python
# Test basic functionality
from http_service import HttpClient

client = HttpClient(base_url="https://httpbin.org")
response = client.get("/get")
print(f"Status: {response.status_code}")
client.close()
```

## 🚨 Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   ```bash
   pip install certifi --upgrade
   ```

2. **Import Errors**
   ```bash
   # Check installation
   pip list | grep http-service
   
   # Reinstall
   pip uninstall http-service
   pip install http-service
   ```

3. **Permission Errors**
   ```bash
   # Use user installation
   pip install --user http-service
   
   # Or use virtual environment
   python -m venv venv
   source venv/bin/activate
   pip install http-service
   ```

### Getting Help

- **GitHub Issues**: [https://github.com/srirama4n/http-service/issues](https://github.com/srirama4n/http-service/issues)
- **Documentation**: [https://http-service.readthedocs.io/](https://http-service.readthedocs.io/)
- **Examples**: See the [examples](examples.md) section

## 📈 Next Steps

After installation:

1. **Read the [Quick Start Guide](quickstart.md)**
2. **Explore [Examples](examples.md)**
3. **Check the [API Reference](api_reference.md)**
4. **Configure your [Environment](configuration.md)**
