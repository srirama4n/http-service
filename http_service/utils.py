"""
Utility functions for HTTP client operations.
Contains helper functions for URL building, header management, and response processing.
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
import httpx

logger = logging.getLogger(__name__)


def build_url(base_url: str, path: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Build a complete URL from base URL, path, and query parameters.
    
    Args:
        base_url: Base URL (e.g., 'https://api.example.com')
        path: Path to append (e.g., '/users')
        params: Query parameters to add
    
    Returns:
        Complete URL with query parameters
    """
    if not base_url.endswith('/') and not path.startswith('/'):
        path = '/' + path
    
    url = urljoin(base_url, path)
    
    if params:
        # Parse existing URL to preserve structure
        parsed = urlparse(url)
        existing_params = parse_qs(parsed.query)
        
        # Update with new parameters
        for key, value in params.items():
            if isinstance(value, (list, tuple)):
                existing_params[key] = [str(v) for v in value]
            else:
                existing_params[key] = [str(value)]
        
        # Rebuild URL with parameters
        new_query = urlencode(existing_params, doseq=True)
        url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
    return url


def sanitize_headers(headers: Dict[str, str], sensitive_keys: Optional[list] = None) -> Dict[str, str]:
    """
    Sanitize headers by masking sensitive information.
    
    Args:
        headers: Headers dictionary
        sensitive_keys: List of header keys to mask
    
    Returns:
        Sanitized headers dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = ['authorization', 'x-api-key', 'cookie', 'set-cookie']
    
    sanitized = {}
    for key, value in headers.items():
        if key.lower() in [k.lower() for k in sensitive_keys]:
            sanitized[key] = '***MASKED***'
        else:
            sanitized[key] = value
    
    return sanitized


def format_request_log(method: str, url: str, headers: Optional[Dict[str, str]] = None, 
                      data: Optional[Any] = None) -> str:
    """
    Format request information for logging.
    
    Args:
        method: HTTP method
        url: Request URL
        headers: Request headers
        data: Request data
    
    Returns:
        Formatted log string
    """
    log_parts = [f"{method.upper()} {url}"]
    
    if headers:
        sanitized_headers = sanitize_headers(headers)
        log_parts.append(f"Headers: {sanitized_headers}")
    
    if data:
        if isinstance(data, dict):
            log_parts.append(f"Data: {json.dumps(data, default=str)}")
        else:
            log_parts.append(f"Data: {str(data)}")
    
    return " | ".join(log_parts)


def format_response_log(response: httpx.Response, include_body: bool = False) -> str:
    """
    Format response information for logging.
    
    Args:
        response: HTTP response object
        include_body: Whether to include response body in log
    
    Returns:
        Formatted log string
    """
    log_parts = [
        f"Status: {response.status_code}",
        f"Reason: {response.reason_phrase}",
        f"Headers: {sanitize_headers(dict(response.headers))}"
    ]
    
    if include_body and response.content:
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                body = response.json()
                log_parts.append(f"Body: {json.dumps(body, default=str)}")
            else:
                log_parts.append(f"Body: {response.text[:500]}...")
        except Exception as e:
            log_parts.append(f"Body: [Error parsing body: {e}]")
    
    return " | ".join(log_parts)


def is_retryable_status_code(status_code: int, retry_codes: Optional[list] = None) -> bool:
    """
    Check if a status code should trigger a retry.
    
    Args:
        status_code: HTTP status code
        retry_codes: List of status codes to retry on
    
    Returns:
        True if status code should trigger retry
    """
    if retry_codes is None:
        retry_codes = [429, 500, 502, 503, 504]
    
    return status_code in retry_codes


def is_retryable_exception(exception: Exception, retry_exceptions: Optional[list] = None) -> bool:
    """
    Check if an exception should trigger a retry.
    
    Args:
        exception: Exception to check
        retry_exceptions: List of exception types to retry on
    
    Returns:
        True if exception should trigger retry
    """
    if retry_exceptions is None:
        retry_exceptions = [
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
            httpx.RemoteProtocolError,
            httpx.ConnectError,
            httpx.ReadError,
            httpx.WriteError
        ]
    
    return any(isinstance(exception, exc_type) for exc_type in retry_exceptions)


def parse_json_response(response: httpx.Response) -> Any:
    """
    Parse JSON response with error handling.
    
    Args:
        response: HTTP response object
    
    Returns:
        Parsed JSON data
    
    Raises:
        ValueError: If response is not valid JSON
    """
    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response content: {response.text}")
        raise ValueError(f"Invalid JSON response: {e}")


def validate_response(response: httpx.Response, expected_status_codes: Optional[list] = None) -> bool:
    """
    Validate HTTP response status code.
    
    Args:
        response: HTTP response object
        expected_status_codes: List of expected status codes
    
    Returns:
        True if response status is expected
    
    Raises:
        httpx.HTTPStatusError: If status code is not expected
    """
    if expected_status_codes is None:
        expected_status_codes = [200, 201, 202, 204]
    
    if response.status_code not in expected_status_codes:
        raise httpx.HTTPStatusError(
            f"Unexpected status code {response.status_code}",
            request=response.request,
            response=response
        )
    
    return True


def merge_headers(default_headers: Dict[str, str], 
                 custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Merge default headers with custom headers.
    
    Args:
        default_headers: Default headers dictionary
        custom_headers: Custom headers to merge
    
    Returns:
        Merged headers dictionary
    """
    if custom_headers is None:
        return default_headers.copy()
    
    merged = default_headers.copy()
    merged.update(custom_headers)
    return merged


def create_auth_header(auth_type: str, **kwargs) -> Dict[str, str]:
    """
    Create authentication header based on type.
    
    Args:
        auth_type: Type of authentication ('bearer', 'api_key', 'basic')
        **kwargs: Authentication parameters
    
    Returns:
        Headers dictionary with authentication
    """
    headers = {}
    
    if auth_type == 'bearer' and kwargs.get('token'):
        headers['Authorization'] = f"Bearer {kwargs['token']}"
    
    elif auth_type == 'api_key' and kwargs.get('api_key'):
        header_name = kwargs.get('api_key_header', 'X-API-Key')
        headers[header_name] = kwargs['api_key']
    
    elif auth_type == 'basic' and kwargs.get('username') and kwargs.get('password'):
        import base64
        credentials = f"{kwargs['username']}:{kwargs['password']}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers['Authorization'] = f"Basic {encoded}"
    
    return headers


def extract_rate_limit_info(response: httpx.Response) -> Dict[str, Any]:
    """
    Extract rate limiting information from response headers.
    
    Args:
        response: HTTP response object
    
    Returns:
        Dictionary with rate limit information
    """
    headers = response.headers
    rate_limit_info = {}
    
    # Common rate limit headers
    rate_limit_headers = {
        'X-RateLimit-Limit': 'limit',
        'X-RateLimit-Remaining': 'remaining',
        'X-RateLimit-Reset': 'reset',
        'X-RateLimit-Used': 'used',
        'Retry-After': 'retry_after'
    }
    
    for header_name, key in rate_limit_headers.items():
        if header_name in headers:
            try:
                rate_limit_info[key] = int(headers[header_name])
            except ValueError:
                rate_limit_info[key] = headers[header_name]
    
    return rate_limit_info


def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, 
                          backoff_factor: float = 2.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay in seconds
    
    Returns:
        Calculated delay in seconds
    """
    delay = base_delay * (backoff_factor ** attempt)
    return min(delay, max_delay)


def is_url_absolute(url: str) -> bool:
    """
    Check if URL is absolute.
    
    Args:
        url: URL to check
    
    Returns:
        True if URL is absolute
    """
    return url.startswith(('http://', 'https://'))


def normalize_url(url: str) -> str:
    """
    Normalize URL by removing trailing slash.
    
    Args:
        url: URL to normalize
    
    Returns:
        Normalized URL
    """
    return url.rstrip('/')


def get_content_type(response: httpx.Response) -> str:
    """
    Get content type from response headers.
    
    Args:
        response: HTTP response object
    
    Returns:
        Content type string
    """
    return response.headers.get('content-type', '').split(';')[0].strip()
