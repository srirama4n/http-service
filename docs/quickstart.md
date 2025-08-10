# Quick Start Guide

Get up and running with HTTP Service in minutes!

## 🚀 Basic Usage

### Simple HTTP Request

```python
from http_service import HttpClient

# Create a client
client = HttpClient(base_url="https://jsonplaceholder.typicode.com")

# Make a GET request
response = client.get("/posts/1")
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")

# Make a POST request
data = {"title": "New Post", "body": "Post content", "userId": 1}
response = client.post("/posts", json=data)
print(f"Created: {response.json()}")

# Don't forget to close the client
client.close()
```

### With Authentication

```python
from http_service import HttpClient

# API Key authentication
client = HttpClient.create_api_client(
    base_url="https://api.example.com",
    api_key="your-api-key-here",
    api_key_header="X-API-Key"
)

# Bearer token authentication
client = HttpClient.create_bearer_token_client(
    base_url="https://api.example.com",
    token="your-bearer-token-here"
)

# Basic authentication
client = HttpClient.create_basic_auth_client(
    base_url="https://api.example.com",
    username="your-username",
    password="your-password"
)

response = client.get("/protected-endpoint")
client.close()
```

## ⚡ Advanced Features

### Retry Logic

```python
from http_service import HttpClient

# Client with automatic retry
client = HttpClient.create_retry_client(
    base_url="https://api.example.com",
    max_retries=3,
    retry_delay=1.0
)

# This will automatically retry on failures
response = client.get("/unreliable-endpoint")
client.close()
```

### Circuit Breaker

```python
from http_service import HttpClient

# Client with circuit breaker protection
client = HttpClient(
    base_url="https://api.example.com",
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=3,
    circuit_breaker_recovery_timeout=30.0
)

# Circuit breaker will open after 3 failures
response = client.get("/endpoint")
client.close()
```

### Rate Limiting

```python
from http_service import HttpClient

# Client with rate limiting (2 requests per second)
client = HttpClient(
    base_url="https://api.example.com",
    rate_limit_requests_per_second=2.0
)

# Requests will be automatically throttled
for i in range(5):
    response = client.get(f"/posts/{i}")
    print(f"Request {i}: {response.status_code}")

client.close()
```

## 🔄 Async Usage

```python
import asyncio
from http_service import HttpClient

async def main():
    # Create async client
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Single async request
    response = await client.aget("/posts/1")
    print(f"Status: {response.status_code}")
    
    # Multiple concurrent requests
    tasks = [
        client.aget(f"/posts/{i}") 
        for i in range(1, 6)
    ]
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses, 1):
        print(f"Post {i}: {response.status_code}")
    
    await client.aclose()

# Run async function
asyncio.run(main())
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
# Basic configuration
HTTP_BASE_URL=https://api.example.com
HTTP_TIMEOUT=30.0
HTTP_MAX_RETRIES=3

# Authentication
HTTP_API_KEY=your-api-key-here
HTTP_BEARER_TOKEN=your-token-here
HTTP_USERNAME=your-username
HTTP_PASSWORD=your-password

# Circuit breaker
HTTP_CIRCUIT_BREAKER_ENABLED=true
HTTP_CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
HTTP_CIRCUIT_BREAKER_RECOVERY_TIMEOUT=30.0

# Rate limiting
HTTP_RATE_LIMIT_RPS=2.0
```

Load configuration:

```python
from http_service import HttpClient

# Create client from environment variables
client = HttpClient.create_client_from_env()
response = client.get("/endpoint")
client.close()
```

### Service-Specific Configuration

```python
from http_service import HttpClient

# Create client for specific service (looks for USER_* variables)
user_client = HttpClient.create_client_for_service("user")

# This will look for:
# USER_BASE_URL, USER_API_KEY, USER_TIMEOUT, etc.
response = user_client.get("/users/profile")
user_client.close()
```

## 🛠️ CLI Tool

HTTP Service includes a command-line interface:

```bash
# Basic GET request
http-service get https://jsonplaceholder.typicode.com/posts/1

# POST request with JSON data
http-service post https://jsonplaceholder.typicode.com/posts \
  --json '{"title": "Test", "body": "Content", "userId": 1}'

# With headers
http-service get https://api.example.com/endpoint \
  --headers '{"Authorization": "Bearer token"}'

# With authentication
http-service get https://api.example.com/protected \
  --api-key your-key-here
```

## 📊 Response Processing

```python
from http_service import HttpClient

client = HttpClient(base_url="https://api.example.com")

response = client.get("/endpoint")

# Get rate limit information
rate_limit_info = client.get_rate_limit_info(response)
if rate_limit_info:
    print(f"Rate limit: {rate_limit_info}")

# Process JSON response
try:
    data = response.json()
    print(f"Data: {data}")
except Exception as e:
    print(f"Failed to parse JSON: {e}")

# Get content type
content_type = client.get_content_type(response)
print(f"Content-Type: {content_type}")

client.close()
```

## 🔒 SSL/TLS Configuration

```python
from http_service import HttpClient

# Client with custom SSL configuration
client = HttpClient(
    base_url="https://api.example.com",
    verify_ssl=True,
    ca_cert_file="/path/to/ca-cert.pem",
    client_cert_file="/path/to/client-cert.pem",
    client_key_file="/path/to/client-key.pem"
)

response = client.get("/secure-endpoint")
client.close()
```

## 🧪 Testing

```python
import pytest
from http_service import HttpClient

def test_basic_request():
    client = HttpClient(base_url="https://httpbin.org")
    response = client.get("/get")
    assert response.status_code == 200
    client.close()

@pytest.mark.asyncio
async def test_async_request():
    client = HttpClient(base_url="https://httpbin.org")
    response = await client.aget("/get")
    assert response.status_code == 200
    await client.aclose()
```

## 📈 Performance

```python
from http_service import HttpClient
import time

client = HttpClient(base_url="https://api.example.com")

# Measure request time
start_time = time.time()
response = client.get("/endpoint")
end_time = time.time()

print(f"Request took {end_time - start_time:.2f} seconds")
client.close()
```

## 🔧 Error Handling

```python
from http_service import HttpClient
from http_service.circuit_breaker import CircuitBreakerOpenError

client = HttpClient(
    base_url="https://api.example.com",
    circuit_breaker_enabled=True
)

try:
    response = client.get("/endpoint")
    print(f"Success: {response.status_code}")
except CircuitBreakerOpenError as e:
    print(f"Circuit breaker open: {e}")
except Exception as e:
    print(f"Request failed: {e}")

client.close()
```

## 📚 Next Steps

Now that you're familiar with the basics:

1. **Explore the [User Guide](user_guide.md)** for detailed feature explanations
2. **Check the [API Reference](api_reference.md)** for complete documentation
3. **See [Examples](examples.md)** for more use cases
4. **Learn about [Configuration](configuration.md)** for advanced setup
5. **Understand [Circuit Breaker](circuit_breaker.md)** and [Retry Logic](retry_logic.md)**

## 🆘 Need Help?

- **Examples**: See the [examples](examples.md) section
- **API Reference**: Complete [API documentation](api_reference.md)
- **Issues**: Report problems on [GitHub](https://github.com/srirama4n/http-service/issues)
- **Discussions**: Join the [GitHub Discussions](https://github.com/srirama4n/http-service/discussions)
