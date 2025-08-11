# HTTP Service

A comprehensive, modular HTTP client built with HTTPX that provides advanced features like retry logic, authentication, rate limiting, circuit breaker pattern, and environment-based configuration.

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Environment Configuration**: Load settings from `.env` files and environment variables
- **Multiple Authentication Types**: Basic, Bearer Token, and API Key authentication
- **Retry Logic**: Configurable retry with exponential backoff and jitter
- **Rate Limiting**: Built-in rate limiting support
- **Circuit Breaker Pattern**: Fault tolerance to prevent cascading failures
- **Connection Pooling**: Optimized connection management
- **Async Support**: Full async/await support for concurrent requests
- **Logging**: Comprehensive request/response logging
- **Error Handling**: Robust error handling and validation
- **Service-Specific Configuration**: Support for multiple services with different configs
- **SSL/TLS Support**: Custom certificate configuration and SSL context management

## 📦 Installation

### Standard Installation

```bash
pip install -r requirements.txt
```

### Local Development Installation

For development or using in another local application:

#### Option 1: Install in Development Mode

```bash
# Clone the repository
git clone https://github.com/srirama4n/http-service.git
cd http-service

# Install in development mode (editable)
pip install -e .

# Or install with all dependencies
pip install -e .[dev]
```

#### Option 2: Add to Local Repository

```bash
# In your local application directory
git submodule add https://github.com/srirama4n/http-service.git libs/http-service

# Or clone directly
git clone https://github.com/srirama4n/http-service.git libs/http-service

# Install the local package
pip install -e ./libs/http-service
```

#### Option 3: Direct Import (No Installation)

```bash
# Copy the http_service directory to your project
cp -r /path/to/http-service/http_service /your/project/libs/

# Add to your Python path
export PYTHONPATH="${PYTHONPATH}:/your/project/libs"

# Or add to your project's __init__.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
```

### Using in Another Local Application

#### Method 1: As a Git Submodule

```bash
# In your application directory
git submodule add https://github.com/srirama4n/http-service.git external/http-service

# Update submodule when needed
git submodule update --remote external/http-service

# Install the submodule
pip install -e ./external/http-service
```

#### Method 2: As a Local Package

```bash
# Clone to a local directory
git clone https://github.com/srirama4n/http-service.git ~/local-packages/http-service

# Add to your application's requirements.txt
-e ~/local-packages/http-service

# Install
pip install -r requirements.txt
```

#### Method 3: Direct Import

```python
# In your application code
import sys
import os

# Add the http_service path
http_service_path = "/path/to/http-service"
sys.path.insert(0, http_service_path)

# Now you can import
from http_service import HttpClient
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/srirama4n/http-service.git
cd http-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_http_client.py -v
```


## 🚀 Quick Start

### Basic Usage

```python
from http_service import HttpClient

# Create a simple client
client = HttpClient(base_url="https://api.example.com")

# Make requests
response = client.get("/users/1")
data = response.json()

# Clean up
client.close()
```

### Using Environment Variables

1. Copy `env_example.env` to `.env` and configure your settings:

```bash
cp env_example.env .env
```

2. Edit `.env` with your configuration:

```env
HTTP_BASE_URL=https://api.example.com
HTTP_AUTH_TYPE=api_key
HTTP_API_KEY=your-api-key-here
HTTP_MAX_RETRIES=3
HTTP_RATE_LIMIT_RPS=10.0
HTTP_CIRCUIT_BREAKER_ENABLED=true
```

3. Use the client:

```python
from http_service import HttpClient

# Create client from environment variables
client = HttpClient.create_client_from_env()

# Make requests
response = client.get("/protected-endpoint")
```

## 📁 Module Structure

### Core Package: `http_service`

- **`client.py`**: Main HttpClient class with all HTTP methods
- **`config.py`**: Environment-based configuration management
- **`models.py`**: Data structures for configuration
- **`decorators.py`**: Retry and rate limiting decorators
- **`utils.py`**: Utility functions for URL building, logging, etc.
- **`circuit_breaker.py`**: Circuit breaker pattern implementation
- **`cli.py`**: Command-line interface

### Configuration Modules

- **`RetryConfig`**: Retry logic configuration
- **`TimeoutConfig`**: Timeout settings
- **`AuthConfig`**: Authentication configuration
- **`CircuitBreakerConfig`**: Circuit breaker configuration
- **`HTTPClientConfig`**: Complete client configuration

## 🔐 Authentication Types

### API Key Authentication

```python
from http_service import HttpClient

client = HttpClient.create_api_client(
    base_url="https://api.example.com",
    api_key="your-api-key",
    api_key_header="X-API-Key"
)
```

### Bearer Token Authentication

```python
from http_service import HttpClient

client = HttpClient.create_bearer_token_client(
    base_url="https://api.example.com",
    token="your-bearer-token"
)
```

### Basic Authentication

```python
from http_service import HttpClient

client = HttpClient.create_basic_auth_client(
    base_url="https://api.example.com",
    username="your-username",
    password="your-password"
)
```

## 🔄 Retry Configuration

```python
from http_service import HttpClient

client = HttpClient(
    base_url="https://api.example.com",
    max_retries=5,
    retry_delay=1.0,
    backoff_factor=2.0,
    retry_on_status_codes=[429, 500, 502, 503, 504]
)

# With jitter for better distribution
from http_service.utils import calculate_backoff_delay
delay = calculate_backoff_delay(attempt=2, base_delay=1.0, backoff_factor=2.0, jitter=True)
```

## ⏱️ Rate Limiting

```python
client = HttpClient(
    base_url="https://api.example.com",
    rate_limit_requests_per_second=10.0  # 10 requests per second
)
```

## 🛡️ Circuit Breaker Pattern

The circuit breaker pattern provides fault tolerance by preventing cascading failures. It has three states:

- **CLOSED**: Normal operation, requests are allowed
- **OPEN**: Failing, requests are rejected immediately
- **HALF_OPEN**: Testing if service has recovered

### Basic Circuit Breaker Usage

```python
from http_service import HttpClient

# Create client with circuit breaker protection
client = HttpClient.create_circuit_breaker_client(
    base_url="https://api.example.com",
    failure_threshold=5,      # Number of failures to open circuit
    recovery_timeout=60.0     # Time to wait before trying half-open
)

# Make requests (circuit breaker will protect against failures)
try:
    response = client.get("/endpoint")
except CircuitBreakerOpenError:
    print("Circuit breaker is open, service is failing")
```

### Custom Circuit Breaker Configuration

```python
from http_service import HttpClient

client = HttpClient(
    base_url="https://api.example.com",
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=3,                    # Open after 3 failures
    circuit_breaker_recovery_timeout=30.0,                  # Wait 30 seconds before half-open
    circuit_breaker_failure_status_codes=[500, 502, 503],   # Status codes that count as failures
    circuit_breaker_success_threshold=2                     # Close after 2 successful requests
)
```

### Circuit Breaker Management

```python
# Check circuit breaker state
print(f"Open: {client.is_circuit_breaker_open()}")
print(f"Closed: {client.is_circuit_breaker_closed()}")
print(f"Half-open: {client.is_circuit_breaker_half_open()}")

# Get statistics
stats = client.get_circuit_breaker_stats()
print(f"Stats: {stats}")

# Manual control
client.force_open_circuit_breaker()  # Force open
client.reset_circuit_breaker()       # Reset to closed
```

### Circuit Breaker with Decorators

```python
from http_service.decorators import circuit_breaker_decorator
from http_service.circuit_breaker import CircuitBreakerConfig

config = CircuitBreakerConfig(enabled=True, failure_threshold=3)

@circuit_breaker_decorator(config)
def my_api_call():
    # Your API call here
    pass
```

## ⚡ Async Usage

```python
import asyncio
from http_service import HttpClient

async def main():
    client = HttpClient(base_url="https://api.example.com")
    
    async with client:
        # Single request
        response = await client.aget("/users/1")
        
        # Multiple concurrent requests
        tasks = [
            client.aget(f"/users/{i}") for i in range(1, 6)
        ]
        responses = await asyncio.gather(*tasks)

asyncio.run(main())
```

## 🔧 Service-Specific Configuration

For multiple services, use service-specific environment variables. **Default values are automatically used for any properties not specified in the environment variables**, ensuring your configuration is always complete.

```env
# User service
USER_BASE_URL=https://user-api.example.com
USER_API_KEY=user-api-key
USER_AUTH_TYPE=api_key
USER_VERIFY_SSL=true
USER_ENABLE_LOGGING=true
USER_CONNECT_TIMEOUT=10.0
USER_READ_TIMEOUT=30.0
USER_WRITE_TIMEOUT=30.0
USER_POOL_TIMEOUT=10.0
USER_MAX_CONNECTIONS=10
USER_MAX_KEEPALIVE_CONNECTIONS=5
USER_KEEPALIVE_EXPIRY=30.0
USER_MAX_RETRIES=3
USER_RETRY_DELAY=1.0
USER_BACKOFF_FACTOR=2.0
USER_RETRY_STATUS_CODES=429,500,502,503,504
USER_RATE_LIMIT_RPS=10.0
USER_CIRCUIT_BREAKER_ENABLED=true
USER_CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
USER_CIRCUIT_BREAKER_RECOVERY_TIMEOUT=30.0
USER_CIRCUIT_BREAKER_FAILURE_STATUS_CODES=500,502,503,504
USER_CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2
USER_HEADER_X_CUSTOM=user-custom-value

# Order service
ORDER_BASE_URL=https://order-api.example.com
ORDER_TOKEN=order-bearer-token
ORDER_AUTH_TYPE=bearer
ORDER_MAX_RETRIES=5
ORDER_RETRY_DELAY=2.0
ORDER_CIRCUIT_BREAKER_ENABLED=true
ORDER_CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60.0
ORDER_HEADER_X_ORDER_ID=order-service

# Secure service with certificates
SECURE_BASE_URL=https://secure-api.example.com
SECURE_CA_CERT_FILE=/path/to/ca-cert.pem
SECURE_CLIENT_CERT_FILE=/path/to/client-cert.pem
SECURE_CLIENT_KEY_FILE=/path/to/client-key.pem
SECURE_SSL_VERSION=TLSv1_2
SECURE_CIPHERS=ECDHE-RSA-AES256-GCM-SHA384
SECURE_CHECK_HOSTNAME=true

# Development service with SSL verification disabled
DEV_BASE_URL=https://dev-api.example.com
DEV_VERIFY_SSL=false
DEV_CHECK_HOSTNAME=false
```

```python
from http_service import HttpClient

# Create clients for specific services
user_client = HttpClient.create_client_for_service("user")
order_client = HttpClient.create_client_for_service("order")
```

### Default Value Behavior

When using service-specific configuration, any properties not explicitly set in the environment variables will use the default values from the base configuration:

- **No environment variables**: All defaults are used
- **Partial configuration**: Only specified values override defaults
- **Complete configuration**: All values are explicitly set

**Example**: If you only set `USER_BASE_URL` and `USER_MAX_RETRIES`, all other properties (timeouts, circuit breaker settings, etc.) will use their default values.

### SSL Verification Control

The `verify_ssl` flag provides fine-grained control over SSL certificate verification:

- **`verify_ssl=True` (default)**: Enables SSL certificate verification
  - Uses system CA certificates if no custom certificates provided
  - Uses custom SSL context if certificate configuration is provided
  - Respects `check_hostname` and other certificate settings

- **`verify_ssl=False`**: Completely disables SSL certificate verification
  - Ignores all certificate configuration
  - Useful for development/testing environments
  - **Warning**: Not recommended for production use

**Examples**:
```python
# Development environment - SSL verification disabled
client = HttpClient(base_url="https://dev-api.example.com", verify_ssl=False)

# Production environment - SSL verification enabled with custom certificates
client = HttpClient(
    base_url="https://prod-api.example.com",
    verify_ssl=True,
    ca_cert_file="/path/to/ca-cert.pem"
)
```

## 🔧 Environment Variables

### Base Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_BASE_URL` | Base URL for all requests | None |
| `HTTP_VERIFY_SSL` | Whether to verify SSL certificates | true |
| `HTTP_ENABLE_LOGGING` | Enable request/response logging | true |

### Timeout Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_CONNECT_TIMEOUT` | Connection timeout (seconds) | 10.0 |
| `HTTP_READ_TIMEOUT` | Read timeout (seconds) | 30.0 |
| `HTTP_WRITE_TIMEOUT` | Write timeout (seconds) | 30.0 |
| `HTTP_POOL_TIMEOUT` | Pool timeout (seconds) | 10.0 |

### Connection Pool Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_MAX_CONNECTIONS` | Maximum connections in pool | 10 |
| `HTTP_MAX_KEEPALIVE_CONNECTIONS` | Maximum keepalive connections | 5 |
| `HTTP_KEEPALIVE_EXPIRY` | Keepalive expiry time (seconds) | 30.0 |

### Retry Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_MAX_RETRIES` | Maximum retry attempts | 3 |
| `HTTP_RETRY_DELAY` | Initial retry delay (seconds) | 1.0 |
| `HTTP_BACKOFF_FACTOR` | Exponential backoff multiplier | 2.0 |
| `HTTP_RETRY_STATUS_CODES` | Status codes to retry on | 429,500,502,503,504 |

### Circuit Breaker Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_CIRCUIT_BREAKER_ENABLED` | Enable circuit breaker | false |
| `HTTP_CIRCUIT_BREAKER_FAILURE_THRESHOLD` | Failures to open circuit | 5 |
| `HTTP_CIRCUIT_BREAKER_RECOVERY_TIMEOUT` | Recovery timeout (seconds) | 60.0 |
| `HTTP_CIRCUIT_BREAKER_FAILURE_STATUS_CODES` | Status codes that count as failures | 500,502,503,504 |
| `HTTP_CIRCUIT_BREAKER_SUCCESS_THRESHOLD` | Successes to close circuit | 2 |

### Authentication Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_AUTH_TYPE` | Authentication type (none/basic/bearer/api_key) | none |
| `HTTP_USERNAME` | Username for basic auth | None |
| `HTTP_PASSWORD` | Password for basic auth | None |
| `HTTP_TOKEN` | Bearer token | None |
| `HTTP_API_KEY` | API key | None |
| `HTTP_API_KEY_HEADER` | API key header name | X-API-Key |

### Certificate Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_CA_CERT_FILE` | Path to CA certificate file | None |
| `HTTP_CA_CERT_DATA` | CA certificate data as string | None |
| `HTTP_CLIENT_CERT_FILE` | Path to client certificate file | None |
| `HTTP_CLIENT_KEY_FILE` | Path to client private key file | None |
| `HTTP_CLIENT_CERT_DATA` | Client certificate data as string | None |
| `HTTP_CLIENT_KEY_DATA` | Client private key data as string | None |
| `HTTP_CHECK_HOSTNAME` | Verify hostname in certificate | true |
| `HTTP_CERT_REQS` | Certificate requirements (CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED) | CERT_REQUIRED |
| `HTTP_SSL_VERSION` | SSL/TLS version (TLSv1_2, TLSv1_3) | None |
| `HTTP_CIPHERS` | SSL ciphers to use | None |
| `HTTP_CERT_VERIFY_MODE` | Certificate verification mode | None |

### Rate Limiting

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_RATE_LIMIT_RPS` | Requests per second limit | None |

### Custom Headers

Use `HTTP_HEADER_` prefix for custom headers:

```env
HTTP_HEADER_X_REQUEST_ID=12345
HTTP_HEADER_X_CLIENT_VERSION=1.0.0
```

## 🛠️ Convenience Functions

### Pre-configured Clients

```python
# API Key client
client = HttpClient.create_api_client(base_url, api_key)

# Bearer token client
client = HttpClient.create_bearer_token_client(base_url, token)

# Basic auth client
client = HttpClient.create_basic_auth_client(base_url, username, password)

# Retry-focused client
client = HttpClient.create_retry_client(base_url, max_retries=5)

# Circuit breaker client
client = HttpClient.create_circuit_breaker_client(base_url, failure_threshold=5)
```

### Environment-based Clients

```python
# From general environment variables
client = HttpClient.create_client_from_env()

# From service-specific environment variables
client = HttpClient.create_client_for_service("user")
```

### Certificate Configuration

```python
# Client with CA certificate verification
client = HttpClient(
    base_url="https://api.example.com",
    ca_cert_file="/path/to/ca-cert.pem"
)

# Client with mutual TLS (client certificates)
client = HttpClient(
    base_url="https://secure-api.example.com",
    client_cert_file="/path/to/client-cert.pem",
    client_key_file="/path/to/client-key.pem"
)

# Client with custom SSL configuration
client = HttpClient(
    base_url="https://api.example.com",
    ssl_version="TLSv1_2",
    ciphers="ECDHE-RSA-AES256-GCM-SHA384",
    check_hostname=False
)

# Client with SSL verification disabled
client = HttpClient(
    base_url="https://api.example.com",
    verify_ssl=False  # Disables SSL certificate verification
)

# Client with SSL verification enabled (default)
client = HttpClient(
    base_url="https://api.example.com",
    verify_ssl=True  # Enables SSL certificate verification
)

# From environment variables
# HTTP_CA_CERT_FILE=/path/to/ca-cert.pem
# HTTP_CLIENT_CERT_FILE=/path/to/client-cert.pem
# HTTP_CLIENT_KEY_FILE=/path/to/client-key.pem
# HTTP_VERIFY_SSL=false  # Disable SSL verification
client = HttpClient.create_client_from_env()
```

## 🔧 Advanced Features

### Custom Decorators

```python
from http_service.decorators import retry, rate_limit, log_request_response
from http_service.circuit_breaker import circuit_breaker_decorator

config = CircuitBreakerConfig(enabled=True, failure_threshold=3)

@retry(max_retries=3, retry_delay=1.0)
@rate_limit(requests_per_second=5.0)
@circuit_breaker_decorator(config)
@log_request_response()
def my_api_call():
    # Your API call here
    pass
```

### Utility Functions

```python
from http_service.utils import (
    build_url, sanitize_headers, format_request_log,
    is_retryable_status_code, parse_json_response, get_content_type,
    create_auth_header, calculate_backoff_delay
)

# Build URL with parameters
url = build_url("https://api.example.com", "/users", {"page": 1, "limit": 10})

# Sanitize headers for logging
safe_headers = sanitize_headers(headers)

# Check if status code should trigger retry
should_retry = is_retryable_status_code(500)

# Parse JSON response safely
data = parse_json_response(response)

# Get content type from headers
content_type = get_content_type(headers)

# Create authentication headers
auth_headers = create_auth_header(auth_config)

# Calculate backoff delay with jitter
delay = calculate_backoff_delay(attempt=2, base_delay=1.0, backoff_factor=2.0, jitter=True)
```

## ⚠️ Error Handling

The client provides comprehensive error handling:

```python
try:
    response = client.get("/endpoint")
    data = response.json()
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e.response.status_code}")
except httpx.ConnectTimeout:
    print("Connection timeout")
except httpx.ReadTimeout:
    print("Read timeout")
except CircuitBreakerOpenError as e:
    print(f"Circuit breaker is open: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📝 Logging

The client provides detailed logging:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.DEBUG)

# Client will log:
# - Request details (method, URL, headers)
# - Response details (status, headers)
# - Retry attempts
# - Rate limiting delays
# - Circuit breaker state changes
# - Errors and exceptions
```

## 📚 Examples

This section focuses on two practical circuit breaker examples. For full examples, see `example_usage.py`.

### Circuit Breaker with Custom Exception (Service Config)

```python
import time
from http_service import HttpClient, CircuitBreakerOpenError

# Create a client from service-specific environment variables (e.g., ORDER_*)
client = HttpClient.create_client_for_service("order")

# Define a custom exception that should trip the circuit breaker
class UpstreamServiceError(Exception):
    pass

# Enable and tune the breaker
client.circuit_breaker_enabled = True
client.circuit_breaker_failure_threshold = 2
client.circuit_breaker_recovery_timeout = 3.0
client.circuit_breaker_success_threshold = 1

# Make the breaker treat the custom exception as a failure
client._circuit_breaker.config.expected_exception = UpstreamServiceError

def flaky_operation():
    raise UpstreamServiceError("Upstream dependency failed")

# Two failures will OPEN the breaker
for _ in range(2):
    try:
        client._circuit_breaker.call(flaky_operation)
    except UpstreamServiceError:
        pass

# Breaker should now be open and reject calls
try:
    client._circuit_breaker.call(lambda: "ok")
except CircuitBreakerOpenError:
    print("Breaker open as expected")

# Wait for recovery timeout; first success closes the breaker
time.sleep(client.circuit_breaker_recovery_timeout + 0.1)
result = client._circuit_breaker.call(lambda: "success")
print(result)
client.close()
```

### Circuit Breaker Ignoring Non-critical Exceptions

```python
from http_service import HttpClient

class UpstreamServiceError(Exception):
    pass

class IgnoredError(Exception):
    pass

client = HttpClient(
    base_url="https://example.com",
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=2,
    circuit_breaker_recovery_timeout=2.0,
    circuit_breaker_success_threshold=1,
)

# Configure breaker to only treat UpstreamServiceError as a failure
client._circuit_breaker.config.expected_exception = UpstreamServiceError

# These errors are ignored by the breaker (will not open)
def operation_with_ignored_error():
    raise IgnoredError("Non-fatal, should not trip breaker")

for _ in range(2):
    try:
        client._circuit_breaker.call(operation_with_ignored_error)
    except IgnoredError:
        pass

print("Breaker open?", client.is_circuit_breaker_open())  # Expect False

# Now raise the expected exception to trigger failures
def operation_with_expected_error():
    raise UpstreamServiceError("Should count as failure")

for _ in range(2):
    try:
        client._circuit_breaker.call(operation_with_expected_error)
    except UpstreamServiceError:
        pass

print("Breaker open after expected errors?", client.is_circuit_breaker_open())
client.close()

### Circuit Breaker with Multiple Expected Exceptions

```python
import time
from http_service import HttpClient

class UpstreamServiceError(Exception):
    pass

class DependencyTimeoutError(Exception):
    pass

client = HttpClient(
    base_url="https://example.com",
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=2,
    circuit_breaker_recovery_timeout=2.0,
    circuit_breaker_success_threshold=1,
)

# Treat multiple exceptions as breaker-triggering failures
client._circuit_breaker.config.expected_exception = (
    UpstreamServiceError,
    DependencyTimeoutError,
)

def raise_upstream():
    raise UpstreamServiceError("upstream error")

def raise_timeout():
    raise DependencyTimeoutError("dependency timed out")

try:
    client._circuit_breaker.call(raise_upstream)
except UpstreamServiceError:
    pass

try:
    client._circuit_breaker.call(raise_timeout)
except DependencyTimeoutError:
    pass

print("Breaker open?", client.is_circuit_breaker_open())
time.sleep(client.circuit_breaker_recovery_timeout + 0.1)
print(client._circuit_breaker.call(lambda: "success"))
client.close()
```
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_http_client.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_circuit_breaker.py -v

# Run with coverage
python -m pytest tests/ --cov=http_service --cov-report=html
```

## 🔄 Local Repository Management

### Setting Up a Local Repository

```bash
# Create a local repository for development
mkdir ~/local-repos
cd ~/local-repos

# Clone the repository
git clone https://github.com/srirama4n/http-service.git
cd http-service

# Create a new branch for your changes
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "Add your feature"

# Push to your local repository (if you have one)
git remote add local /path/to/your/local/repo
git push local feature/your-feature-name
```

### Using Local Repository in Applications

#### Method 1: Local Git Repository

```bash
# In your application directory
git remote add http-service ~/local-repos/http-service
git subtree add --prefix=libs/http-service http-service master --squash

# Or use as a submodule
git submodule add ~/local-repos/http-service libs/http-service
```

#### Method 2: Local Package Installation

```bash
# Install from local path
pip install -e ~/local-repos/http-service

# Or add to requirements.txt
echo "-e ~/local-repos/http-service" >> requirements.txt
pip install -r requirements.txt
```

#### Method 3: Symlink for Development

```bash
# Create a symlink for easy development
ln -s ~/local-repos/http-service ~/your-app/libs/http-service

# In your application
import sys
sys.path.append('~/your-app/libs')
from http_service import HttpClient
```

### Managing Local Development

```bash
# Update your local repository
cd ~/local-repos/http-service
git pull origin master

# Update submodules in your application
cd ~/your-app
git submodule update --remote libs/http-service

# Reinstall if needed
pip install -e ~/local-repos/http-service --force-reinstall
```

### Publishing to Local Package Index

```bash
# Build the package
cd ~/local-repos/http-service
python setup.py sdist bdist_wheel

# Install from local package
pip install dist/http_service-*.whl

# Or publish to a local PyPI server
pip install twine
twine upload --repository-url http://localhost:8080 dist/*
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

## 📋 Quick Reference Guide

### 🚀 Getting Started in 5 Minutes

```bash
# 1. Clone the repository
git clone https://github.com/srirama4n/http-service.git
cd http-service

# 2. Install in development mode
pip install -e .

# 3. Run tests to verify installation
python -m pytest tests/ -v

# 4. Start using in your application
```

```python
# 5. Basic usage in your application
from http_service import HttpClient

# Create a client
client = HttpClient(base_url="https://api.example.com")

# Make a request
response = client.get("/users/1")
print(response.json())

# Clean up
client.close()
```

### 🔧 Common Use Cases

#### Quick API Client Setup
```python
# For a simple API
client = HttpClient.create_api_client(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

# For a service with authentication
client = HttpClient.create_bearer_token_client(
    base_url="https://api.example.com",
    token="your-bearer-token"
)
```

#### Environment-Based Configuration
```bash
# Create .env file
echo "HTTP_BASE_URL=https://api.example.com" > .env
echo "HTTP_API_KEY=your-api-key" >> .env
echo "HTTP_AUTH_TYPE=api_key" >> .env
```

```python
# Use in your application
client = HttpClient.create_client_from_env()
```

#### Service-Specific Clients
```bash
# Multiple services in .env
echo "USER_BASE_URL=https://user-api.example.com" >> .env
echo "USER_API_KEY=user-key" >> .env
echo "ORDER_BASE_URL=https://order-api.example.com" >> .env
echo "ORDER_TOKEN=order-token" >> .env
```

```python
# Create service-specific clients
user_client = HttpClient.create_client_for_service("user")
order_client = HttpClient.create_client_for_service("order")
```

### 🛠️ Development Workflow

#### Local Development Setup
```bash
# 1. Set up development environment
git clone https://github.com/srirama4n/http-service.git
cd http-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -e .

# 3. Run tests
python -m pytest tests/ -v

# 4. Make changes and test
# Edit files...
python -m pytest tests/test_your_feature.py -v
```

#### Using in Another Project
```bash
# Method 1: Git submodule
cd your-project
git submodule add https://github.com/srirama4n/http-service.git libs/http-service
pip install -e ./libs/http-service

# Method 2: Direct clone
cd your-project
git clone https://github.com/srirama4n/http-service.git libs/http-service
pip install -e ./libs/http-service

# Method 3: Local development
cd your-project
ln -s ~/path/to/http-service libs/http-service
export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs"
```

### 📦 Package Management

#### Building and Installing
```bash
# Build the package
python setup.py sdist bdist_wheel

# Install from wheel
pip install dist/http_service-*.whl

# Install in development mode
pip install -e .
```

#### Publishing to Local PyPI
```bash
# Set up local PyPI server
pip install pypiserver
pypi-server -p 8080 ~/packages &

# Build and upload
python setup.py sdist bdist_wheel
twine upload --repository-url http://localhost:8080 dist/*

# Install from local PyPI
pip install --index-url http://localhost:8080/simple/ http-service
```

### 🔍 Troubleshooting

#### Common Issues and Solutions

**Import Error: No module named 'http_service'**
```bash
# Solution 1: Install in development mode
pip install -e .

# Solution 2: Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/http-service"

# Solution 3: Use sys.path
import sys
sys.path.append('/path/to/http-service')
```

**Test Failures**
```bash
# Run tests with verbose output
python -m pytest tests/ -v -s

# Run specific test file
python -m pytest tests/test_http_client.py -v

# Run with coverage
python -m pytest tests/ --cov=http_service --cov-report=html
```

**SSL Certificate Issues**
```python
# For development environments
client = HttpClient(
    base_url="https://api.example.com",
    verify_ssl=False  # Disable SSL verification
)

# For production with custom certificates
client = HttpClient(
    base_url="https://api.example.com",
    ca_cert_file="/path/to/ca-cert.pem"
)
```

### 📚 Additional Resources

- **Full Documentation**: See `example_usage.py` for comprehensive examples
- **Test Suite**: Run `python -m pytest tests/ -v` to see all features in action
- **Environment Variables**: Check `env_example.env` for all available options
- **Configuration**: See `http_service/config.py` for configuration options
- **Models**: See `http_service/models.py` for data structures

### 🎯 Best Practices

1. **Use Environment Variables**: Configure your clients using environment variables for flexibility
2. **Service-Specific Configs**: Use service-specific environment variables for multiple services
3. **Error Handling**: Always wrap HTTP calls in try-catch blocks
4. **Resource Management**: Use context managers (`async with client:`) for proper cleanup
5. **Testing**: Run the test suite to verify your setup
6. **Logging**: Enable logging for debugging and monitoring
7. **Circuit Breaker**: Enable circuit breaker for production applications
8. **Rate Limiting**: Use rate limiting to respect API limits

### 🔄 Version Management

```bash
# Check current version
python -c "import http_service; print(http_service.__version__)"

# Update from remote
git pull origin master
pip install -e . --force-reinstall

# Pin to specific version
pip install -e .==1.0.0
```



