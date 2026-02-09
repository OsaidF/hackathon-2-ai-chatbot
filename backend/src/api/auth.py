"""
Authentication endpoints for Todo AI Chatbot.

Provides login and signup endpoints with JWT token generation.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from src.db.session import get_session
from src.models.user import User
from src.services.jwt_service import jwt_service

# Router
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Security scheme
security = HTTPBearer()


# Request/Response Models
class SignupRequest(BaseModel):
    """Signup request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (8-100 characters)")


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (bearer)")
    user_id: str = Field(..., description="User ID")


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Register a new user.

    Args:
        request: Signup request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token and user ID

    Raises:
        HTTPException 409: If user already exists
    """
    # Check if user already exists
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Create new user
    user = User(
        id=uuid4(),
        email=request.email,
        hashed_password=jwt_service.get_password_hash(request.password)
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Generate JWT token
    access_token = jwt_service.create_access_token(
        data={"sub": str(user.id)}
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id)
    )


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Login existing user.

    Args:
        request: Login request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token and user ID

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not jwt_service.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = jwt_service.create_access_token(
        data={"sub": str(user.id)}
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id)
    )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
):
    """
    Get current user information.

    Args:
        credentials: Bearer token credentials
        session: Database session

    Returns:
        User information

    Raises:
        HTTPException 401: If token is invalid
    """
    # Extract user ID from token
    user_id = jwt_service.get_user_id_from_token(credentials.credentials)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Get user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return {
        "user_id": str(user.id),
        "email": user.email,
        "created_at": user.created_at
    }
