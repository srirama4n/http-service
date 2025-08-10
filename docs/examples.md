# Examples

Practical examples and use cases for HTTP Service.

## 🔧 Basic Examples

### Simple HTTP Client

```python
from http_service import HttpClient

# Create a basic client
client = HttpClient(base_url="https://jsonplaceholder.typicode.com")

# GET request
response = client.get("/posts/1")
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")

# POST request
data = {"title": "New Post", "body": "Content", "userId": 1}
response = client.post("/posts", json=data)
print(f"Created: {response.json()}")

# PUT request
update_data = {"title": "Updated Post", "body": "Updated content"}
response = client.put("/posts/1", json=update_data)
print(f"Updated: {response.json()}")

# DELETE request
response = client.delete("/posts/1")
print(f"Deleted: {response.status_code}")

client.close()
```

### With Query Parameters

```python
from http_service import HttpClient

client = HttpClient(base_url="https://api.example.com")

# GET with query parameters
params = {"page": 1, "limit": 10, "sort": "name"}
response = client.get("/users", params=params)
users = response.json()

# POST with form data
form_data = {"name": "John Doe", "email": "john@example.com"}
response = client.post("/users", data=form_data)

client.close()
```

## 🔐 Authentication Examples

### API Key Authentication

```python
from http_service import HttpClient

# Method 1: Using factory method
client = HttpClient.create_api_client(
    base_url="https://api.example.com",
    api_key="your-api-key-here",
    api_key_header="X-API-Key"
)

# Method 2: Using constructor
client = HttpClient(
    base_url="https://api.example.com",
    auth_type="api_key",
    api_key="your-api-key-here",
    api_key_header="X-API-Key"
)

response = client.get("/protected-endpoint")
client.close()
```

### Bearer Token Authentication

```python
from http_service import HttpClient

# Method 1: Using factory method
client = HttpClient.create_bearer_token_client(
    base_url="https://api.example.com",
    token="your-bearer-token-here"
)

# Method 2: Using constructor
client = HttpClient(
    base_url="https://api.example.com",
    auth_type="bearer",
    token="your-bearer-token-here"
)

response = client.get("/user/profile")
client.close()
```

### Basic Authentication

```python
from http_service import HttpClient

# Method 1: Using factory method
client = HttpClient.create_basic_auth_client(
    base_url="https://api.example.com",
    username="your-username",
    password="your-password"
)

# Method 2: Using constructor
client = HttpClient(
    base_url="https://api.example.com",
    auth_type="basic",
    username="your-username",
    password="your-password"
)

response = client.get("/secure-endpoint")
client.close()
```

## 🔄 Retry Examples

### Basic Retry

```python
from http_service import HttpClient

# Client with retry configuration
client = HttpClient(
    base_url="https://api.example.com",
    max_retries=3,
    retry_delay=1.0,
    retry_backoff_factor=2.0
)

# This will retry on connection errors and timeouts
response = client.get("/unreliable-endpoint")
client.close()
```

### Retry on Specific Status Codes

```python
from http_service import HttpClient

client = HttpClient(
    base_url="https://api.example.com",
    max_retries=5,
    retry_on_status_codes=[429, 500, 502, 503, 504]
)

# Will retry on rate limiting (429) and server errors (5xx)
response = client.get("/endpoint")
client.close()
```

### Using Retry Decorator

```python
from http_service import retry

@retry(max_retries=3, retry_delay=1.0)
def make_request():
    client = HttpClient(base_url="https://api.example.com")
    response = client.get("/endpoint")
    client.close()
    return response

response = make_request()
```

## ⚡ Circuit Breaker Examples

### Basic Circuit Breaker

```python
from http_service import HttpClient

client = HttpClient(
    base_url="https://api.example.com",
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=3,
    circuit_breaker_recovery_timeout=30.0
)

# Circuit breaker will open after 3 failures
for i in range(5):
    try:
        response = client.get("/unreliable-endpoint")
        print(f"Request {i+1}: Success")
    except Exception as e:
        print(f"Request {i+1}: Failed - {e}")

client.close()
```

### Circuit Breaker Management

```python
from http_service import HttpClient
from http_service.circuit_breaker import CircuitBreakerOpenError

client = HttpClient(
    base_url="https://api.example.com",
    circuit_breaker_enabled=True
)

# Check circuit breaker state
print(f"Open: {client.is_circuit_breaker_open()}")
print(f"Closed: {client.is_circuit_breaker_closed()}")
print(f"Half-open: {client.is_circuit_breaker_half_open()}")

# Force open circuit breaker
client.force_open_circuit_breaker()

try:
    response = client.get("/endpoint")
except CircuitBreakerOpenError as e:
    print(f"Circuit breaker open: {e}")

# Reset circuit breaker
client.reset_circuit_breaker()

# Get statistics
stats = client.get_circuit_breaker_stats()
print(f"Stats: {stats}")

client.close()
```

## 🚦 Rate Limiting Examples

### Basic Rate Limiting

```python
from http_service import HttpClient
import time

client = HttpClient(
    base_url="https://api.example.com",
    rate_limit_requests_per_second=2.0  # 2 requests per second
)

# Requests will be automatically throttled
for i in range(5):
    start_time = time.time()
    response = client.get(f"/posts/{i}")
    end_time = time.time()
    print(f"Request {i+1}: {response.status_code} (took {end_time - start_time:.2f}s)")

client.close()
```

### Using Rate Limit Decorator

```python
from http_service import rate_limit
import time

@rate_limit(requests_per_second=1.0)  # 1 request per second
def make_request():
    client = HttpClient(base_url="https://api.example.com")
    response = client.get("/endpoint")
    client.close()
    return response

for i in range(3):
    start_time = time.time()
    response = make_request()
    end_time = time.time()
    print(f"Request {i+1}: took {end_time - start_time:.2f}s")
```

## 🔄 Async Examples

### Basic Async Usage

```python
import asyncio
from http_service import HttpClient

async def main():
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Single async request
    response = await client.aget("/posts/1")
    print(f"Status: {response.status_code}")
    print(f"Data: {response.json()}")
    
    await client.aclose()

asyncio.run(main())
```

### Concurrent Requests

```python
import asyncio
from http_service import HttpClient

async def main():
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Multiple concurrent requests
    tasks = [
        client.aget(f"/posts/{i}") 
        for i in range(1, 6)
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses, 1):
        print(f"Post {i}: {response.status_code}")
    
    await client.aclose()

asyncio.run(main())
```

### Async with Rate Limiting

```python
import asyncio
from http_service import HttpClient

async def main():
    client = HttpClient(
        base_url="https://api.example.com",
        rate_limit_requests_per_second=2.0
    )
    
    # Concurrent requests with rate limiting
    tasks = [
        client.aget(f"/endpoint/{i}") 
        for i in range(5)
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses, 1):
        print(f"Request {i}: {response.status_code}")
    
    await client.aclose()

asyncio.run(main())
```

## ⚙️ Configuration Examples

### Environment Configuration

Create a `.env` file:

```env
# Basic configuration
HTTP_BASE_URL=https://api.example.com
HTTP_TIMEOUT=30.0
HTTP_MAX_RETRIES=3

# Authentication
HTTP_AUTH_TYPE=bearer
HTTP_BEARER_TOKEN=your-token-here

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

# Create client for user service (looks for USER_* variables)
user_client = HttpClient.create_client_for_service("user")

# Create client for order service (looks for ORDER_* variables)
order_client = HttpClient.create_client_for_service("order")

# Use the clients
user_response = user_client.get("/users/profile")
order_response = order_client.get("/orders/123")

user_client.close()
order_client.close()
```

## 🔒 SSL/TLS Examples

### Custom SSL Configuration

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

### Disable SSL Verification (Not Recommended)

```python
from http_service import HttpClient

client = HttpClient(
    base_url="https://api.example.com",
    verify_ssl=False  # Disables SSL verification
)

response = client.get("/endpoint")
client.close()
```

## 📊 Response Processing Examples

### Rate Limit Information

```python
from http_service import HttpClient

client = HttpClient(base_url="https://api.example.com")

response = client.get("/endpoint")

# Extract rate limit information
rate_limit_info = client.get_rate_limit_info(response)
if rate_limit_info:
    print(f"Rate limit: {rate_limit_info}")
    print(f"Remaining: {rate_limit_info.get('remaining')}")
    print(f"Reset time: {rate_limit_info.get('reset')}")

client.close()
```

### Content Type Handling

```python
from http_service import HttpClient

client = HttpClient(base_url="https://api.example.com")

response = client.get("/endpoint")

# Get content type
content_type = client.get_content_type(response)
print(f"Content-Type: {content_type}")

# Process based on content type
if content_type == "application/json":
    data = response.json()
    print(f"JSON data: {data}")
elif content_type.startswith("text/"):
    text = response.text
    print(f"Text data: {text}")

client.close()
```

## 🧪 Testing Examples

### Basic Test

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

### Test with Mocking

```python
import pytest
from unittest.mock import Mock, patch
from http_service import HttpClient

def test_with_mock():
    with patch('httpx.Client') as mock_client:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_client.return_value.request.return_value = mock_response
        
        # Test
        client = HttpClient(base_url="https://api.example.com")
        response = client.get("/endpoint")
        
        assert response.status_code == 200
        assert response.json()["message"] == "success"
        client.close()
```

## 🛠️ CLI Examples

### Basic CLI Usage

```bash
# GET request
http-service get https://jsonplaceholder.typicode.com/posts/1

# POST request with JSON data
http-service post https://jsonplaceholder.typicode.com/posts \
  --json '{"title": "Test Post", "body": "Content", "userId": 1}'

# PUT request
http-service put https://jsonplaceholder.typicode.com/posts/1 \
  --json '{"title": "Updated Post", "body": "Updated content"}'

# DELETE request
http-service delete https://jsonplaceholder.typicode.com/posts/1
```

### CLI with Authentication

```bash
# With API key
http-service get https://api.example.com/protected \
  --api-key your-api-key-here

# With Bearer token
http-service get https://api.example.com/protected \
  --bearer-token your-token-here

# With Basic auth
http-service get https://api.example.com/secure \
  --username your-username \
  --password your-password
```

### CLI with Headers and Data

```bash
# With custom headers
http-service get https://api.example.com/endpoint \
  --headers '{"X-Custom-Header": "value", "Accept": "application/json"}'

# POST with form data
http-service post https://api.example.com/users \
  --data 'name=John Doe&email=john@example.com'

# POST with JSON data
http-service post https://api.example.com/users \
  --json '{"name": "John Doe", "email": "john@example.com"}'
```

## 🏗️ Real-World Application Example

### User Service Client

```python
from http_service import HttpClient
from typing import Dict, List, Optional

class UserService:
    def __init__(self, base_url: str, api_key: str):
        self.client = HttpClient.create_api_client(
            base_url=base_url,
            api_key=api_key,
            api_key_header="X-API-Key"
        )
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        try:
            response = self.client.get(f"/users/{user_id}")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error getting user {user_id}: {e}")
            return None
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Create a new user."""
        try:
            response = self.client.post("/users", json=user_data)
            return response.json() if response.status_code == 201 else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user(self, user_id: int, user_data: Dict) -> Optional[Dict]:
        """Update user."""
        try:
            response = self.client.put(f"/users/{user_id}", json=user_data)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        try:
            response = self.client.delete(f"/users/{user_id}")
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting user {user_id}: {e}")
            return False
    
    def list_users(self, page: int = 1, limit: int = 10) -> List[Dict]:
        """List users with pagination."""
        try:
            params = {"page": page, "limit": limit}
            response = self.client.get("/users", params=params)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error listing users: {e}")
            return []
    
    def close(self):
        """Close the client."""
        self.client.close()

# Usage
user_service = UserService(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

# Get user
user = user_service.get_user(1)
print(f"User: {user}")

# Create user
new_user = user_service.create_user({
    "name": "John Doe",
    "email": "john@example.com"
})
print(f"Created: {new_user}")

# List users
users = user_service.list_users(page=1, limit=5)
print(f"Users: {users}")

user_service.close()
```

### Order Service with Circuit Breaker

```python
from http_service import HttpClient
from http_service.circuit_breaker import CircuitBreakerOpenError

class OrderService:
    def __init__(self, base_url: str, token: str):
        self.client = HttpClient.create_bearer_token_client(
            base_url=base_url,
            token=token
        )
        # Enable circuit breaker for fault tolerance
        self.client.circuit_breaker_enabled = True
        self.client.circuit_breaker_failure_threshold = 3
        self.client.circuit_breaker_recovery_timeout = 30.0
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order by ID with circuit breaker protection."""
        try:
            response = self.client.get(f"/orders/{order_id}")
            return response.json() if response.status_code == 200 else None
        except CircuitBreakerOpenError:
            print(f"Circuit breaker open for order {order_id}")
            return None
        except Exception as e:
            print(f"Error getting order {order_id}: {e}")
            return None
    
    def create_order(self, order_data: Dict) -> Optional[Dict]:
        """Create a new order."""
        try:
            response = self.client.post("/orders", json=order_data)
            return response.json() if response.status_code == 201 else None
        except CircuitBreakerOpenError:
            print("Circuit breaker open for order creation")
            return None
        except Exception as e:
            print(f"Error creating order: {e}")
            return None
    
    def get_circuit_breaker_stats(self) -> Dict:
        """Get circuit breaker statistics."""
        return self.client.get_circuit_breaker_stats() or {}
    
    def close(self):
        """Close the client."""
        self.client.close()

# Usage
order_service = OrderService(
    base_url="https://api.example.com",
    token="your-bearer-token"
)

# Get order with circuit breaker protection
order = order_service.get_order("12345")
if order:
    print(f"Order: {order}")

# Check circuit breaker stats
stats = order_service.get_circuit_breaker_stats()
print(f"Circuit breaker stats: {stats}")

order_service.close()
```

## 📈 Performance Examples

### Benchmarking

```python
import time
from http_service import HttpClient

def benchmark_requests():
    client = HttpClient(base_url="https://httpbin.org")
    
    # Benchmark GET requests
    start_time = time.time()
    for i in range(10):
        response = client.get("/get")
        print(f"Request {i+1}: {response.status_code}")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / 10
    
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per request: {avg_time:.2f}s")
    print(f"Requests per second: {10/total_time:.2f}")
    
    client.close()

benchmark_requests()
```

### Memory Usage Monitoring

```python
import psutil
import os
from http_service import HttpClient

def monitor_memory_usage():
    process = psutil.Process(os.getpid())
    
    # Memory before
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Memory before: {memory_before:.2f} MB")
    
    # Create client and make requests
    client = HttpClient(base_url="https://httpbin.org")
    for i in range(100):
        response = client.get("/get")
    
    # Memory after
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Memory after: {memory_after:.2f} MB")
    print(f"Memory increase: {memory_after - memory_before:.2f} MB")
    
    client.close()

monitor_memory_usage()
```

These examples demonstrate the versatility and power of HTTP Service for various use cases. Each example can be adapted and extended based on your specific requirements.
