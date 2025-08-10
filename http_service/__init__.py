"""
HTTP Service Package

A comprehensive, robust HTTP client service built with HTTPX featuring:
- Retry logic with exponential backoff
- Circuit breaker pattern
- Rate limiting
- Authentication (API Key, Bearer Token, Basic Auth)
- Connection pooling
- Comprehensive logging
- Environment-based configuration
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core imports
from .client import HttpClient
from .config import HTTPClientConfig, get_config, get_config_for_service
from .models import (
    RetryConfig, TimeoutConfig, AuthConfig, CircuitBreakerConfig,
    ConnectionPoolConfig, RateLimitConfig, LoggingConfig, HTTPClientSettings,
    CircuitBreakerState
)
from .circuit_breaker import (
    CircuitBreaker, CircuitBreakerOpenError,
    should_trigger_circuit_breaker
)

# Utility imports
from .utils import (
    build_url, sanitize_headers, format_request_log, format_response_log,
    is_retryable_status_code, is_retryable_exception, merge_headers,
    create_auth_header, extract_rate_limit_info, calculate_backoff_delay,
    is_url_absolute, normalize_url, get_content_type, parse_json_response,
    validate_response
)

# Decorator imports
from .decorators import (
    retry, async_retry, rate_limit, async_rate_limit,
    log_request_response, async_log_request_response
)

__all__ = [
    # Core classes
    "HttpClient",
    "HTTPClientConfig",
    "RetryConfig",
    "TimeoutConfig", 
    "AuthConfig",
    "CircuitBreakerConfig",
    "ConnectionPoolConfig",
    "RateLimitConfig",
    "LoggingConfig",
    "HTTPClientSettings",
    "CircuitBreakerState",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    
    # Functions
    "get_config",
    "get_config_for_service",
    "should_trigger_circuit_breaker",
    "build_url",
    "sanitize_headers",
    "format_request_log",
    "format_response_log",
    "is_retryable_status_code",
    "is_retryable_exception",
    "merge_headers",
    "create_auth_header",
    "extract_rate_limit_info",
    "calculate_backoff_delay",
    "is_url_absolute",
    "normalize_url",
    "get_content_type",
    "parse_json_response",
    "validate_response",
    
    # Decorators
    "retry",
    "async_retry",
    "rate_limit",
    "async_rate_limit",
    "log_request_response",
    "async_log_request_response",
]
