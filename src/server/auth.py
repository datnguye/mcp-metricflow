"""Authentication module for MetricFlow MCP server."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils.logger import logger

# Security scheme for Bearer token authentication
security = HTTPBearer(auto_error=False)


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
    # Get config from app state
    config = getattr(request.app.state, "config", None)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server configuration not available"
        )

    # Skip authentication if not required
    if not config.require_auth:
        logger.debug("Authentication not required, skipping API key validation")
        return True

    # Check if API key is configured
    if not config.api_key:
        logger.error("Authentication required but no API key configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server authentication not properly configured"
        )

    # Check if credentials are provided
    if not credentials:
        logger.warning("API key authentication failed: No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate the API key
    provided_key = credentials.credentials
    if provided_key != config.api_key:
        logger.warning("API key authentication failed: Invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("API key authentication successful")
    return True


# Type alias for authenticated dependency
Authenticated = Annotated[bool, Depends(verify_api_key)]
