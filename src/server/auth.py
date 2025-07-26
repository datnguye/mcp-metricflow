"""Authentication module for MetricFlow MCP server."""

import re
import secrets
from collections import defaultdict
from time import time
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from utils.logger import logger

# Security scheme for Bearer token authentication
security = HTTPBearer(auto_error=False)

# Rate limiting for failed authentication attempts
request_counts = defaultdict(list)
MAX_REQUESTS = 5
TIME_WINDOW = 300  # 5 minutes


class AuthenticationError(Exception):
    """Custom authentication error."""

    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> None:
        """Initialize authentication error.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format and strength.

    Args:
        api_key: The API key to validate

    Returns:
        True if the API key meets security requirements
    """
    if not api_key:
        return False

    # Minimum length check
    if len(api_key) < 32:
        return False

    # Check for acceptable characters (alphanumeric, underscore, hyphen)
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", api_key))


def validate_auth_config(config: Any) -> None:
    """Validate authentication configuration.

    Args:
        config: Configuration object

    Raises:
        ValueError: If authentication configuration is invalid
    """
    if config.require_auth:
        if not config.api_key:
            raise ValueError("API key is required when authentication is enabled")

        if not validate_api_key_format(config.api_key):
            raise ValueError(
                "API key does not meet security requirements: "
                "must be at least 32 characters and contain only alphanumeric characters, underscores, or hyphens"
            )

        logger.info("✓ Authentication configuration validated")


def check_rate_limit(request: Request) -> None:
    """Check rate limiting for failed authentication attempts.

    Args:
        request: FastAPI request object

    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_ip = request.client.host if request.client else "unknown"
    current_time = time()

    # Clean old entries
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] if current_time - req_time < TIME_WINDOW
    ]

    if len(request_counts[client_ip]) >= MAX_REQUESTS:
        logger.warning(
            "Rate limit exceeded for authentication attempts",
            extra={"client_ip": client_ip, "attempts": len(request_counts[client_ip]), "time_window": TIME_WINDOW},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed authentication attempts. Try again later.",
            headers={"Retry-After": str(TIME_WINDOW)},
        )


def record_failed_attempt(request: Request) -> None:
    """Record a failed authentication attempt for rate limiting.

    Args:
        request: FastAPI request object
    """
    client_ip = request.client.host if request.client else "unknown"
    request_counts[client_ip].append(time())


def verify_api_key(
    request: Request, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> bool:
    """Verify API key authentication.

    Args:
        request: FastAPI request object containing app state
        credentials: HTTP authorization credentials

    Returns:
        True if authentication is successful

    Raises:
        HTTPException: If authentication fails
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    endpoint = str(request.url)

    try:
        # Get config from app state
        config = getattr(request.app.state, "config", None)
        if not config:
            raise AuthenticationError("Server configuration not available", status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Skip authentication if not required
        if not config.require_auth:
            logger.debug("Authentication not required, skipping API key validation")
            return True

        # Check rate limiting before processing
        check_rate_limit(request)

        # Check if API key is configured
        if not config.api_key:
            logger.error("Authentication required but no API key configured")
            raise AuthenticationError(
                "Server authentication not properly configured", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Check if credentials are provided
        if not credentials:
            record_failed_attempt(request)
            logger.warning(
                "Authentication failed: No credentials provided",
                extra={
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "endpoint": endpoint,
                    "reason": "missing_credentials",
                },
            )
            raise AuthenticationError("API key required")

        # Validate the API key using constant-time comparison
        provided_key = credentials.credentials
        if not secrets.compare_digest(provided_key, config.api_key):
            record_failed_attempt(request)
            logger.warning(
                "Authentication failed: Invalid API key provided",
                extra={
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "endpoint": endpoint,
                    "reason": "invalid_api_key",
                },
            )
            raise AuthenticationError("Invalid API key")

        logger.debug("API key authentication successful", extra={"client_ip": client_ip, "endpoint": endpoint})
        return True

    except AuthenticationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={
                "WWW-Authenticate": "Bearer",
                "Cache-Control": "no-store",
                "Pragma": "no-cache",
            },
        ) from None


# Type alias for authenticated dependency
Authenticated = Annotated[bool, Depends(verify_api_key)]
