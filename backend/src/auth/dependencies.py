"""
Authentication dependencies for Todo AI Chatbot (T049).

This module provides FastAPI dependencies for extracting user information
from JWT tokens using proper JWT validation.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
import os

from src.services.jwt_service import jwt_service


# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UUID:
    """
    Extract and validate user_id from JWT token.

    Args:
        credentials: HTTP Bearer token credentials from Authorization header

    Returns:
        UUID: User ID extracted from JWT token

    Raises:
        HTTPException 401: If token is invalid, missing, or expired
    """
    # Check for development mode bypass
    if os.getenv("ENVIRONMENT") == "development" and os.getenv("SKIP_AUTH") == "true":
        # For testing only: return dev user ID
        return UUID("550e8400-e29b-41d4-a716-446655440000")

    # Validate credentials are present
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract and validate token
    user_id = jwt_service.get_user_id_from_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UUID]:
    """
    Optionally extract user_id from JWT token.

    Unlike get_current_user, this does not raise an exception if token is missing.
    Returns None instead, allowing anonymous access.

    Args:
        credentials: HTTP Bearer token credentials from Authorization header

    Returns:
        Optional[UUID]: User ID if token provided and valid, None otherwise

    Use Case:
        Endpoints that want to provide personalized experience when authenticated
        but still allow anonymous access.
    """
    # Check for development mode bypass
    if os.getenv("ENVIRONMENT") == "development" and os.getenv("SKIP_AUTH") == "true":
        # For testing only: return dev user ID
        return UUID("550e8400-e29b-41d4-a716-446655440000")

    # If no credentials provided, return None
    if credentials is None:
        return None

    # Extract and validate token
    user_id = jwt_service.get_user_id_from_token(credentials.credentials)

    # Return user_id if valid, None otherwise
    return user_id
