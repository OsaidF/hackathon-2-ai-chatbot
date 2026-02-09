"""
User model for Todo AI Chatbot.

Represents a user authenticated via Better Auth.
Tasks and conversations are isolated by user_id for multi-tenancy.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    """
    User entity representing a person using the system.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique)
        created_at: Account creation timestamp

    Notes:
        - Managed by Better Auth authentication system
        - Never directly accessed by MCP tools (only referenced via user_id)
        - Cascade deletes: When user deleted, all conversations and tasks are deleted
    """

    __tablename__ = "todo_users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique user identifier"
    )

    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (must be unique)"
    )

    hashed_password: str = Field(
        max_length=255,
        description="Hashed password (bcrypt)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2025-01-24T10:30:00Z"
            }
        }


class UserPublic(SQLModel):
    """Public user information (without sensitive data)."""

    id: UUID
    email: str
    created_at: datetime


class UserCreate(SQLModel):
    """Schema for creating a new user."""

    email: str


class UserUpdate(SQLModel):
    """Schema for updating user information."""

    email: Optional[str] = None
