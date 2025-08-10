# HTTP Service Documentation

Welcome to the HTTP Service documentation! This comprehensive HTTP client library is built with HTTPX and provides advanced features for robust HTTP communication.

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
api_reference
examples
```

## 🚀 Quick Start

```python
from http_service import HttpClient

# Create a simple client
client = HttpClient(base_url="https://api.example.com")

# Make a request
response = client.get("/users/1")
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")

# Don't forget to close the client
client.close()
```

## 📚 Documentation Sections

### [Installation](installation.md)
Learn how to install HTTP Service and its dependencies.

### [Quick Start Guide](quickstart.md)
Get up and running with HTTP Service in minutes.

### [API Reference](api_reference.md)
Complete API documentation for all classes and functions.

### [Examples](examples.md)
Practical examples and use cases.

## 🎯 Key Features

- **🔄 Automatic Retry Logic** - Configurable retry with exponential backoff
- **⚡ Circuit Breaker Pattern** - Fault tolerance and failure isolation
- **🚦 Rate Limiting** - Control request rates and prevent throttling
- **🔐 Multiple Authentication** - API Key, Bearer Token, Basic Auth
- **🔒 SSL/TLS Support** - Full certificate management and verification
- **⚡ Async Support** - Native async/await support
- **📊 Comprehensive Logging** - Detailed request/response logging
- **⚙️ Environment Configuration** - Easy configuration via environment variables
- **🧪 Extensive Testing** - 179+ tests with comprehensive coverage

## 📦 Installation

```bash
# Basic installation
pip install http-service

# With development dependencies
pip install http-service[dev]

# With all dependencies
pip install http-service[all]
```

## 🔧 Development Setup

```bash
# Clone the repository
git clone https://github.com/srirama4n/http-service.git
cd http-service

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
make lint
```

## 📈 Project Status

- **Version**: 1.0.0
- **Python Support**: 3.8+
- **Test Coverage**: 179 tests ✅
- **Build Status**: ✅ Passing
- **Documentation**: ✅ Complete

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](development.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔗 Links

- **GitHub**: [https://github.com/srirama4n/http-service](https://github.com/srirama4n/http-service)
- **Issues**: [https://github.com/srirama4n/http-service/issues](https://github.com/srirama4n/http-service/issues)
- **PyPI**: [https://pypi.org/project/http-service/](https://pypi.org/project/http-service/)

---

**Need Help?** Check out our [Examples](examples.md) or open an [Issue](https://github.com/srirama4n/http-service/issues) on GitHub.
