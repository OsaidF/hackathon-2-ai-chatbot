"""
Conversation model for Todo AI Chatbot.

Represents a series of message exchanges between a user and the AI assistant.
Enables conversation continuity across requests via conversation_id.
"""

from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a message exchange series.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Owner of this conversation (foreign key to User)
        created_at: When conversation was created

    Purpose:
        Enables conversation continuity across server restarts.
        Each request includes conversation_id to retrieve history.
        New conversations auto-created when conversation_id not provided.

    State Transitions:
        None - conversation is a passive container for messages

    Operations:
        Create: Auto-created when conversation_id not provided in chat request
        Read: Retrieved by conversation_id and user_id (must match)
        Delete: Cascade deletes all associated messages

    Validation Rules:
        - user_id must be valid UUID and reference existing user
        - Only owner (user_id match) can access conversation

    Constitution Compliance:
        - Stateless: Conversation metadata persisted to database
        - Database as Single Source of Truth: No in-memory storage
    """

    __tablename__ = "todo_conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique conversation identifier"
    )

    user_id: UUID = Field(
        foreign_key="todo_users.id",
        index=True,
        description="Owner of this conversation (references User.id)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When conversation was created"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "created_at": "2025-01-24T10:30:00Z"
            }
        }


class ConversationPublic(SQLModel):
    """Public conversation information."""

    id: UUID
    user_id: UUID
    created_at: datetime


class ConversationCreate(SQLModel):
    """Schema for creating a new conversation."""

    user_id: UUID
