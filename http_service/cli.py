"""
Command Line Interface for the Modular HTTP Client.
"""

import argparse
import json
import sys
from typing import Dict, Any

from .client import HttpClient
from .config import get_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Modular HTTP Client - A comprehensive HTTP client with retry, circuit breaker, and authentication"
    )
    
    parser.add_argument(
        "method",
        choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
        help="HTTP method"
    )
    
    parser.add_argument(
        "url",
        help="Request URL"
    )
    
    parser.add_argument(
        "--base-url",
        help="Base URL for the client"
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for authentication"
    )
    
    parser.add_argument(
        "--token",
        help="Bearer token for authentication"
    )
    
    parser.add_argument(
        "--username",
        help="Username for basic authentication"
    )
    
    parser.add_argument(
        "--password",
        help="Password for basic authentication"
    )
    
    parser.add_argument(
        "--data",
        help="Request data (JSON string)"
    )
    
    parser.add_argument(
        "--headers",
        help="Request headers (JSON string)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds"
    )
    
    parser.add_argument(
        "--circuit-breaker",
        action="store_true",
        help="Enable circuit breaker"
    )
    
    parser.add_argument(
        "--from-env",
        action="store_true",
        help="Load configuration from environment variables"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON response"
    )
    
    args = parser.parse_args()
    
    try:
        # Create client
        if args.from_env:
            config = get_config()
            client = HttpClient(config=config)
        else:
            # Determine auth type
            auth_type = "none"
            if args.api_key:
                auth_type = "api_key"
            elif args.token:
                auth_type = "bearer"
            elif args.username and args.password:
                auth_type = "basic"
            
            client = HttpClient(
                base_url=args.base_url,
                auth_type=auth_type,
                api_key=args.api_key,
                token=args.token,
                username=args.username,
                password=args.password,
                max_retries=args.max_retries,
                read_timeout=args.timeout,
                circuit_breaker_enabled=args.circuit_breaker
            )
        
        # Prepare request data
        kwargs = {}
        
        if args.data:
            try:
                kwargs["json"] = json.loads(args.data)
            except json.JSONDecodeError:
                kwargs["data"] = args.data
        
        if args.headers:
            try:
                kwargs["headers"] = json.loads(args.headers)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in headers", file=sys.stderr)
                sys.exit(1)
        
        # Make request
        method = args.method.lower()
        response = client.request(method, args.url, **kwargs)
        
        # Print response
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        try:
            if args.pretty:
                print(json.dumps(response.json(), indent=2))
            else:
                print(response.text)
        except json.JSONDecodeError:
            print(response.text)
        
        client.close()
        
    except KeyboardInterrupt:
        print("\nRequest cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
