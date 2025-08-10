"""
Example usage of the modular HTTP client.
Demonstrates various ways to create and use the client with different configurations.
"""

import asyncio
import json
import time
from http_service import (
    HttpClient, RetryConfig, TimeoutConfig, AuthConfig, CircuitBreakerConfig,
    CircuitBreakerOpenError
)
from http_service.config import get_config, get_config_for_service


def example_basic_usage():
    """Example of basic client usage."""
    print("=== Basic Usage Example ===")
    
    # Create a simple client
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Make a GET request
    response = client.get("/posts/1")
    print(f"Status: {response.status_code}")
    print(f"Data: {response.json()}")
    
    # Make a POST request
    data = {"title": "Test Post", "body": "This is a test", "userId": 1}
    response = client.post("/posts", json=data)
    print(f"POST Status: {response.status_code}")
    print(f"Created: {response.json()}")
    
    client.close_sync()


def example_api_key_client():
    """Example of API key authentication."""
    print("\n=== API Key Authentication Example ===")
    
    # Create client with API key
    client = HttpClient.create_api_client(
        base_url="https://api.example.com",
        api_key="your-api-key-here",
        api_key_header="X-API-Key"
    )
    
    # Make authenticated request
    response = client.get("/protected-endpoint")
    print(f"Authenticated request status: {response.status_code}")
    
    client.close_sync()


def example_bearer_token_client():
    """Example of bearer token authentication."""
    print("\n=== Bearer Token Authentication Example ===")
    
    # Create client with bearer token
    client = HttpClient.create_bearer_token_client(
        base_url="https://api.example.com",
        token="your-bearer-token-here"
    )
    
    # Make authenticated request
    response = client.get("/user/profile")
    print(f"Bearer auth request status: {response.status_code}")
    
    client.close_sync()


def example_basic_auth_client():
    """Example of basic authentication."""
    print("\n=== Basic Authentication Example ===")
    
    # Create client with basic auth
    client = HttpClient.create_basic_auth_client(
        base_url="https://api.example.com",
        username="your-username",
        password="your-password"
    )
    
    # Make authenticated request
    response = client.get("/secure-endpoint")
    print(f"Basic auth request status: {response.status_code}")
    
    client.close_sync()


def example_retry_client():
    """Example of client with aggressive retry configuration."""
    print("\n=== Retry Configuration Example ===")
    
    # Create client with retry configuration
    client = HttpClient.create_retry_client(
        base_url="https://api.example.com",
        max_retries=5,
        retry_delay=2.0
    )
    
    # This will retry on failures
    try:
        response = client.get("/unreliable-endpoint")
        print(f"Retry client request status: {response.status_code}")
    except Exception as e:
        print(f"Request failed after retries: {e}")
    
    client.close_sync()


def example_fast_client():
    """Example of client optimized for speed."""
    print("\n=== Fast Client Example ===")
    
    # Create fast client with short timeouts
    client = HttpClient(
        base_url="https://api.example.com",
        connect_timeout=2.0,
        read_timeout=5.0
    )
    
    # Make fast request
    response = client.get("/fast-endpoint")
    print(f"Fast client request status: {response.status_code}")
    
    client.close_sync()


def example_circuit_breaker_client():
    """Example of circuit breaker functionality."""
    print("\n=== Circuit Breaker Example ===")
    
    # Create client with circuit breaker protection
    client = HttpClient.create_circuit_breaker_client(
        base_url="https://httpstat.us",
        failure_threshold=3,
        recovery_timeout=10.0
    )
    
    # Make requests to a failing endpoint
    for i in range(5):
        try:
            response = client.get("/500")
            print(f"Request {i+1}: Status {response.status_code}")
        except CircuitBreakerOpenError as e:
            print(f"Request {i+1}: Circuit breaker OPEN - {e}")
            break
        except Exception as e:
            print(f"Request {i+1}: Error - {type(e).__name__}: {e}")
    
    # Check circuit breaker stats
    stats = client.get_circuit_breaker_stats()
    if stats:
        print(f"Circuit breaker stats: {stats}")
    
    # Wait for recovery timeout
    print("Waiting for circuit breaker to attempt recovery...")
    time.sleep(11)
    
    # Try again (should be in half-open state)
    try:
        response = client.get("/200")
        print(f"Recovery attempt: Status {response.status_code}")
    except Exception as e:
        print(f"Recovery attempt failed: {e}")
    
    client.close_sync()


def example_custom_circuit_breaker_config():
    """Example of custom circuit breaker configuration."""
    print("\n=== Custom Circuit Breaker Configuration Example ===")
    
    # Create custom circuit breaker configuration
    circuit_breaker_config = CircuitBreakerConfig(
        enabled=True,
        failure_threshold=2,
        recovery_timeout=5.0,
        failure_status_codes=[500, 502, 503, 504],
        success_threshold=1
    )
    
    # Create client with custom circuit breaker
    client = HttpClient(
        base_url="https://httpstat.us",
        circuit_breaker_config=circuit_breaker_config
    )
    
    # Test circuit breaker behavior
    for i in range(4):
        try:
            response = client.get("/500")
            print(f"Request {i+1}: Status {response.status_code}")
        except CircuitBreakerOpenError as e:
            print(f"Request {i+1}: Circuit breaker OPEN - {e}")
            break
        except Exception as e:
            print(f"Request {i+1}: Error - {type(e).__name__}: {e}")
    
    # Check circuit breaker state
    print(f"Circuit breaker open: {client.is_circuit_breaker_open()}")
    print(f"Circuit breaker closed: {client.is_circuit_breaker_closed()}")
    print(f"Circuit breaker half-open: {client.is_circuit_breaker_half_open()}")
    
    client.close_sync()


def example_custom_configuration():
    """Example of custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Create custom retry configuration
    retry_config = RetryConfig(
        max_retries=3,
        retry_delay=1.0,
        backoff_factor=1.5,
        retry_on_status_codes=[429, 500, 502, 503, 504]
    )
    
    # Create custom timeout configuration
    timeout_config = TimeoutConfig(
        connect_timeout=5.0,
        read_timeout=15.0,
        write_timeout=15.0,
        pool_timeout=5.0
    )
    
    # Create custom auth configuration
    auth_config = AuthConfig(
        auth_type="api_key",
        api_key="your-custom-api-key",
        api_key_header="X-Custom-API-Key"
    )
    
    # Create custom circuit breaker configuration
    circuit_breaker_config = CircuitBreakerConfig(
        enabled=True,
        failure_threshold=3,
        recovery_timeout=30.0
    )
    
    # Create client with custom configuration
    client = HttpClient(
        base_url="https://api.example.com",
        retry_config=retry_config,
        timeout_config=timeout_config,
        auth_config=auth_config,
        circuit_breaker_config=circuit_breaker_config,
        headers={"X-Custom-Header": "custom-value"},
        rate_limit_requests_per_second=5.0
    )
    
    # Make request with custom configuration
    response = client.get("/custom-endpoint")
    print(f"Custom config request status: {response.status_code}")
    
    client.close_sync()


def example_certificate_configuration():
    """Example of certificate configuration."""
    print("\n=== Certificate Configuration Example ===")
    
    # Client with CA certificate verification
    ca_client = HttpClient(
        base_url="https://api.example.com",
        ca_cert_file="/path/to/ca-cert.pem",
        check_hostname=True
    )
    
    # Client with mutual TLS (client certificates)
    mtls_client = HttpClient(
        base_url="https://secure-api.example.com",
        client_cert_file="/path/to/client-cert.pem",
        client_key_file="/path/to/client-key.pem",
        ssl_version="TLSv1_2"
    )
    
    # Client with custom SSL configuration
    ssl_client = HttpClient(
        base_url="https://api.example.com",
        ssl_version="TLSv1_2",
        ciphers="ECDHE-RSA-AES256-GCM-SHA384",
        check_hostname=False,
        cert_reqs="CERT_OPTIONAL"
    )
    
    # Client with certificate data (not files)
    data_client = HttpClient(
        base_url="https://api.example.com",
        ca_cert_data="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
        client_cert_data="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
        client_key_data="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
    )
    
    # Client with SSL verification disabled
    no_verify_client = HttpClient(
        base_url="https://api.example.com",
        verify_ssl=False  # Disables SSL certificate verification
    )
    
    # Client with SSL verification enabled (default)
    verify_client = HttpClient(
        base_url="https://api.example.com",
        verify_ssl=True  # Enables SSL certificate verification
    )
    
    print("Certificate configurations created successfully")
    
    # Clean up
    ca_client.close_sync()
    mtls_client.close_sync()
    ssl_client.close_sync()
    data_client.close_sync()
    no_verify_client.close_sync()
    verify_client.close_sync()


def example_environment_configuration():
    """Example of using environment-based configuration."""
    print("\n=== Environment Configuration Example ===")
    
    # Create client from environment variables
    # Make sure to set up your .env file first
    try:
        client = HttpClient.create_client_from_env()
        print("Client created from environment variables")
        
        # Make request
        response = client.get("/env-configured-endpoint")
        print(f"Environment config request status: {response.status_code}")
        
        client.close_sync()
    except Exception as e:
        print(f"Environment configuration failed: {e}")
        print("Make sure to set up your .env file with proper values")


def example_service_specific_configuration():
    """Example of service-specific configuration."""
    print("\n=== Service-Specific Configuration Example ===")
    
    # Create client for specific service
    # This will look for USER_* environment variables
    try:
        user_client = HttpClient.create_client_for_service("user")
        print("User service client created")
        
        # Make request to user service
        response = user_client.get("/users/profile")
        print(f"User service request status: {response.status_code}")
        
        user_client.close_sync()
    except Exception as e:
        print(f"Service-specific configuration failed: {e}")
        print("Make sure to set up USER_* environment variables")


async def example_async_usage():
    """Example of async client usage."""
    print("\n=== Async Usage Example ===")
    
    # Create async client
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Make async requests
    async with client:
        # Single request
        response = await client.aget("/posts/1")
        print(f"Async GET status: {response.status_code}")
        
        # Multiple concurrent requests
        tasks = [
            client.aget(f"/posts/{i}") for i in range(1, 6)
        ]
        responses = await asyncio.gather(*tasks)
        
        print(f"Made {len(responses)} concurrent requests")
        for i, response in enumerate(responses, 1):
            print(f"Post {i} status: {response.status_code}")


def example_rate_limiting():
    """Example of rate limiting functionality."""
    print("\n=== Rate Limiting Example ===")
    
    # Create client with rate limiting
    client = HttpClient(
        base_url="https://jsonplaceholder.typicode.com",
        rate_limit_requests_per_second=2.0  # 2 requests per second
    )
    
    # Make multiple requests (will be rate limited)
    for i in range(5):
        response = client.get(f"/posts/{i+1}")
        print(f"Request {i+1} status: {response.status_code}")
    
    client.close_sync()


def example_response_processing():
    """Example of response processing utilities."""
    print("\n=== Response Processing Example ===")
    
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Make request and process response
    response = client.get("/posts/1")
    
    # Extract rate limit info (if available)
    rate_limit_info = client.get_rate_limit_info(response)
    if rate_limit_info:
        print(f"Rate limit info: {rate_limit_info}")
    
    # Process JSON response
    try:
        data = response.json()
        print(f"Response data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
    
    client.close_sync()


def example_error_handling():
    """Example of error handling."""
    print("\n=== Error Handling Example ===")
    
    client = HttpClient(
        base_url="https://httpstat.us",
        retry_config=RetryConfig(max_retries=2)
    )
    
    # Test different error scenarios
    test_cases = [
        ("/200", "Success"),
        ("/404", "Not Found"),
        ("/500", "Server Error"),
        ("/timeout", "Timeout")
    ]
    
    for endpoint, description in test_cases:
        try:
            response = client.get(endpoint)
            print(f"{description}: {response.status_code}")
        except Exception as e:
            print(f"{description}: Error - {type(e).__name__}: {e}")
    
    client.close_sync()


def example_circuit_breaker_management():
    """Example of circuit breaker management."""
    print("\n=== Circuit Breaker Management Example ===")
    
    # Create client with circuit breaker
    client = HttpClient.create_circuit_breaker_client(
        base_url="https://httpstat.us",
        failure_threshold=2,
        recovery_timeout=5.0
    )
    
    # Check initial state
    print(f"Initial state - Open: {client.is_circuit_breaker_open()}")
    
    # Force open circuit breaker
    client.force_open_circuit_breaker()
    print(f"After force open - Open: {client.is_circuit_breaker_open()}")
    
    # Try to make request (should be rejected)
    try:
        response = client.get("/200")
        print(f"Request succeeded: {response.status_code}")
    except CircuitBreakerOpenError as e:
        print(f"Request rejected: {e}")
    
    # Reset circuit breaker
    client.reset_circuit_breaker()
    print(f"After reset - Open: {client.is_circuit_breaker_open()}")
    
    # Now request should work
    try:
        response = client.get("/200")
        print(f"Request after reset: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Get statistics
    stats = client.get_circuit_breaker_stats()
    if stats:
        print(f"Circuit breaker statistics: {json.dumps(stats, indent=2)}")
    
    client.close_sync()


def main():
    """Run all examples."""
    print("HTTP Client Examples")
    print("=" * 50)
    
    # Run synchronous examples
    example_basic_usage()
    example_api_key_client()
    example_bearer_token_client()
    example_basic_auth_client()
    example_retry_client()
    example_fast_client()
    example_circuit_breaker_client()
    example_custom_circuit_breaker_config()
    example_custom_configuration()
    example_certificate_configuration()
    example_environment_configuration()
    example_service_specific_configuration()
    example_rate_limiting()
    example_response_processing()
    example_error_handling()
    example_circuit_breaker_management()
    
    # Run async example
    asyncio.run(example_async_usage())
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    main()
