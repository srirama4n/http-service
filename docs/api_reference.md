# API Reference

Complete API documentation for HTTP Service.

## HttpClient

The main HTTP client class that provides all HTTP functionality.

### Constructor

```python
HttpClient(
    base_url: str = "",
    timeout: float = 30.0,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_backoff_factor: float = 2.0,
    retry_on_status_codes: List[int] = None,
    circuit_breaker_enabled: bool = True,
    circuit_breaker_failure_threshold: int = 5,
    circuit_breaker_recovery_timeout: float = 60.0,
    circuit_breaker_failure_status_codes: List[int] = None,
    circuit_breaker_success_threshold: int = 2,
    rate_limit_requests_per_second: Optional[float] = None,
    verify_ssl: bool = True,
    ca_cert_file: Optional[str] = None,
    ca_cert_data: Optional[str] = None,
    client_cert_file: Optional[str] = None,
    client_key_file: Optional[str] = None,
    client_cert_data: Optional[str] = None,
    client_key_data: Optional[str] = None,
    check_hostname: bool = True,
    cert_reqs: str = "CERT_REQUIRED",
    ssl_version: Optional[str] = None,
    ciphers: Optional[str] = None,
    cert_verify_mode: Optional[str] = None,
    **kwargs
)
```

### Factory Methods

#### create_api_client

```python
@classmethod
def create_api_client(
    cls,
    base_url: str,
    api_key: str,
    api_key_header: str = "X-API-Key",
    **kwargs
) -> "HttpClient"
```

Creates a client configured with API key authentication.

#### create_bearer_token_client

```python
@classmethod
def create_bearer_token_client(
    cls,
    base_url: str,
    token: str,
    **kwargs
) -> "HttpClient"
```

Creates a client configured with Bearer token authentication.

#### create_basic_auth_client

```python
@classmethod
def create_basic_auth_client(
    cls,
    base_url: str,
    username: str,
    password: str,
    **kwargs
) -> "HttpClient"
```

Creates a client configured with Basic authentication.

#### create_retry_client

```python
@classmethod
def create_retry_client(
    cls,
    base_url: str,
    max_retries: int = 5,
    retry_delay: float = 2.0,
    **kwargs
) -> "HttpClient"
```

Creates a client with aggressive retry configuration.

#### create_fast_client

```python
@classmethod
def create_fast_client(
    cls,
    base_url: str,
    timeout: float = 5.0,
    **kwargs
) -> "HttpClient"
```

Creates a client optimized for speed with short timeouts.

#### create_client_from_env

```python
@classmethod
def create_client_from_env(cls, **kwargs) -> "HttpClient"
```

Creates a client from environment variables.

#### create_client_for_service

```python
@classmethod
def create_client_for_service(
    cls,
    service_name: str,
    **kwargs
) -> "HttpClient"
```

Creates a client for a specific service using service-prefixed environment variables.

### HTTP Methods

#### get

```python
def get(
    self,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes a GET request.

#### post

```python
def post(
    self,
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes a POST request.

#### put

```python
def put(
    self,
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes a PUT request.

#### patch

```python
def patch(
    self,
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes a PATCH request.

#### delete

```python
def delete(
    self,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes a DELETE request.

#### request

```python
def request(
    self,
    method: str,
    url: str,
    **kwargs
) -> httpx.Response
```

Makes a generic HTTP request.

### Async Methods

#### aget

```python
async def aget(
    self,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes an async GET request.

#### apost

```python
async def apost(
    self,
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes an async POST request.

#### aput

```python
async def aput(
    self,
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes an async PUT request.

#### apatch

```python
async def apatch(
    self,
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes an async PATCH request.

#### adelete

```python
async def adelete(
    self,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> httpx.Response
```

Makes an async DELETE request.

#### arequest

```python
async def arequest(
    self,
    method: str,
    url: str,
    **kwargs
) -> httpx.Response
```

Makes an async generic HTTP request.

### Circuit Breaker Methods

#### is_circuit_breaker_open

```python
def is_circuit_breaker_open(self) -> bool
```

Returns True if the circuit breaker is in OPEN state.

#### is_circuit_breaker_closed

```python
def is_circuit_breaker_closed(self) -> bool
```

Returns True if the circuit breaker is in CLOSED state.

#### is_circuit_breaker_half_open

```python
def is_circuit_breaker_half_open(self) -> bool
```

Returns True if the circuit breaker is in HALF_OPEN state.

#### force_open_circuit_breaker

```python
def force_open_circuit_breaker(self) -> None
```

Forces the circuit breaker to OPEN state.

#### reset_circuit_breaker

```python
def reset_circuit_breaker(self) -> None
```

Resets the circuit breaker to CLOSED state.

#### get_circuit_breaker_stats

```python
def get_circuit_breaker_stats(self) -> Optional[Dict[str, Any]]
```

Returns circuit breaker statistics.

### Utility Methods

#### get_rate_limit_info

```python
def get_rate_limit_info(self, response: httpx.Response) -> Optional[Dict[str, Any]]
```

Extracts rate limit information from response headers.

#### get_content_type

```python
def get_content_type(self, response: httpx.Response) -> Optional[str]
```

Gets the content type from response headers.

#### close

```python
def close(self) -> None
```

Closes the HTTP client.

#### aclose

```python
async def aclose(self) -> None
```

Closes the async HTTP client.

## CircuitBreaker

Circuit breaker implementation for fault tolerance.

### Constructor

```python
CircuitBreaker(
    config: CircuitBreakerConfig,
    failure_callback: Optional[Callable] = None,
    success_callback: Optional[Callable] = None
)
```

### Methods

#### call

```python
def call(self, func: Callable, *args, **kwargs) -> Any
```

Executes a function with circuit breaker protection.

#### is_open

```python
def is_open(self) -> bool
```

Returns True if the circuit breaker is open.

#### is_closed

```python
def is_closed(self) -> bool
```

Returns True if the circuit breaker is closed.

#### is_half_open

```python
def is_half_open(self) -> bool
```

Returns True if the circuit breaker is half-open.

#### force_open

```python
def force_open(self) -> None
```

Forces the circuit breaker to open state.

#### reset

```python
def reset(self) -> None
```

Resets the circuit breaker to closed state.

#### get_stats

```python
def get_stats(self) -> Dict[str, Any]
```

Returns circuit breaker statistics.

## Decorators

### retry

```python
def retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retry_on_exceptions: Tuple[Type[Exception], ...] = None,
    retry_on_status_codes: List[int] = None,
    jitter: bool = False
) -> Callable
```

Decorator for automatic retry logic.

### async_retry

```python
def async_retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retry_on_exceptions: Tuple[Type[Exception], ...] = None,
    retry_on_status_codes: List[int] = None,
    jitter: bool = False
) -> Callable
```

Async decorator for automatic retry logic.

### rate_limit

```python
def rate_limit(
    requests_per_second: Optional[float] = None,
    burst_size: int = 1
) -> Callable
```

Decorator for rate limiting.

### async_rate_limit

```python
def async_rate_limit(
    requests_per_second: Optional[float] = None,
    burst_size: int = 1
) -> Callable
```

Async decorator for rate limiting.

### log_request_response

```python
def log_request_response(
    log_request: bool = True,
    log_response: bool = True,
    log_headers: bool = True,
    log_body: bool = True,
    max_body_length: int = 1000
) -> Callable
```

Decorator for request/response logging.

### async_log_request_response

```python
def async_log_request_response(
    log_request: bool = True,
    log_response: bool = True,
    log_headers: bool = True,
    log_body: bool = True,
    max_body_length: int = 1000
) -> Callable
```

Async decorator for request/response logging.

## Configuration Classes

### HTTPClientConfig

```python
@dataclass
class HTTPClientConfig:
    base_url: str = ""
    timeout: float = 30.0
    retry: RetryConfig = field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    certificate: CertificateConfig = field(default_factory=CertificateConfig)
```

### RetryConfig

```python
@dataclass
class RetryConfig:
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 60.0
    retry_on_exceptions: Tuple[Type[Exception], ...] = (httpx.ConnectError, httpx.TimeoutException)
    retry_on_status_codes: List[int] = None
    jitter: bool = False
```

### CircuitBreakerConfig

```python
@dataclass
class CircuitBreakerConfig:
    enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    failure_status_codes: List[int] = None
    success_threshold: int = 2
    failure_callback: Optional[Callable] = None
    success_callback: Optional[Callable] = None
```

### AuthConfig

```python
@dataclass
class AuthConfig:
    auth_type: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
```

### RateLimitConfig

```python
@dataclass
class RateLimitConfig:
    requests_per_second: Optional[float] = None
    burst_size: int = 1
```

### LoggingConfig

```python
@dataclass
class LoggingConfig:
    log_requests: bool = True
    log_responses: bool = True
    log_headers: bool = True
    log_body: bool = True
    max_body_length: int = 1000
```

### CertificateConfig

```python
@dataclass
class CertificateConfig:
    verify_ssl: bool = True
    ca_cert_file: Optional[str] = None
    ca_cert_data: Optional[str] = None
    client_cert_file: Optional[str] = None
    client_key_file: Optional[str] = None
    client_cert_data: Optional[str] = None
    client_key_data: Optional[str] = None
    check_hostname: bool = True
    cert_reqs: str = "CERT_REQUIRED"
    ssl_version: Optional[str] = None
    ciphers: Optional[str] = None
    cert_verify_mode: Optional[str] = None
```

## Utility Functions

### build_url

```python
def build_url(
    base_url: str,
    path: str = "",
    params: Optional[Dict[str, Any]] = None
) -> str
```

Builds a complete URL from base URL, path, and parameters.

### sanitize_headers

```python
def sanitize_headers(
    headers: Dict[str, str],
    sensitive_keys: List[str] = None
) -> Dict[str, str]
```

Sanitizes headers by masking sensitive information.

### format_request_log

```python
def format_request_log(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Any] = None,
    max_body_length: int = 1000
) -> str
```

Formats request information for logging.

### format_response_log

```python
def format_response_log(
    response: httpx.Response,
    max_body_length: int = 1000
) -> str
```

Formats response information for logging.

### create_auth_header

```python
def create_auth_header(auth_config) -> Dict[str, str]
```

Creates authentication headers from configuration.

### calculate_backoff_delay

```python
def calculate_backoff_delay(
    attempt: int,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = False
) -> float
```

Calculates backoff delay for retry logic.

### get_content_type

```python
def get_content_type(response: Union[httpx.Response, Dict[str, str]]) -> Optional[str]
```

Gets content type from response or headers.

### parse_json_response

```python
def parse_json_response(response: httpx.Response) -> Any
```

Parses JSON response with error handling.

## Exceptions

### CircuitBreakerOpenError

```python
class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and request is rejected."""
    pass
```

### ConfigurationError

```python
class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass
```

## Environment Variables

### Basic Configuration

- `HTTP_BASE_URL` - Base URL for all requests
- `HTTP_TIMEOUT` - Request timeout in seconds
- `HTTP_MAX_RETRIES` - Maximum number of retries
- `HTTP_RETRY_DELAY` - Delay between retries
- `HTTP_RETRY_BACKOFF_FACTOR` - Exponential backoff factor

### Authentication

- `HTTP_AUTH_TYPE` - Authentication type (api_key, bearer, basic)
- `HTTP_API_KEY` - API key for authentication
- `HTTP_API_KEY_HEADER` - Header name for API key
- `HTTP_BEARER_TOKEN` - Bearer token for authentication
- `HTTP_USERNAME` - Username for basic authentication
- `HTTP_PASSWORD` - Password for basic authentication

### Circuit Breaker

- `HTTP_CIRCUIT_BREAKER_ENABLED` - Enable/disable circuit breaker
- `HTTP_CIRCUIT_BREAKER_FAILURE_THRESHOLD` - Failure threshold
- `HTTP_CIRCUIT_BREAKER_RECOVERY_TIMEOUT` - Recovery timeout
- `HTTP_CIRCUIT_BREAKER_FAILURE_STATUS_CODES` - Status codes that trigger failures
- `HTTP_CIRCUIT_BREAKER_SUCCESS_THRESHOLD` - Success threshold

### Rate Limiting

- `HTTP_RATE_LIMIT_RPS` - Requests per second limit

### SSL/TLS

- `HTTP_VERIFY_SSL` - Enable/disable SSL verification
- `HTTP_CA_CERT_FILE` - Path to CA certificate file
- `HTTP_CLIENT_CERT_FILE` - Path to client certificate file
- `HTTP_CLIENT_KEY_FILE` - Path to client key file

## CLI Commands

### http-service

```bash
http-service [OPTIONS] COMMAND [ARGS]...
```

#### Commands

- `get URL` - Make a GET request
- `post URL` - Make a POST request
- `put URL` - Make a PUT request
- `patch URL` - Make a PATCH request
- `delete URL` - Make a DELETE request

#### Options

- `--headers TEXT` - Request headers (JSON format)
- `--json TEXT` - JSON data for request body
- `--data TEXT` - Form data for request body
- `--api-key TEXT` - API key for authentication
- `--bearer-token TEXT` - Bearer token for authentication
- `--username TEXT` - Username for basic authentication
- `--password TEXT` - Password for basic authentication
- `--timeout FLOAT` - Request timeout
- `--verify-ssl BOOLEAN` - Verify SSL certificates
- `--help` - Show help message
