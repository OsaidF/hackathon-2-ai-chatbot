"""
Message model for Todo AI Chatbot.

Represents a single communication in a conversation.
Stores both user messages and assistant responses for conversation history.
"""

from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message entity representing a single communication.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Which conversation this message belongs to
        role: Who sent this message (user or assistant)
        content: The message content
        created_at: When message was created

    Purpose:
        Stores full conversation history for context retrieval.
        Both user messages and assistant responses are persisted.

    State Transitions:
        None - messages are immutable once created

    Operations:
        Create: New message added to conversation (user or assistant role)
        Read: Retrieved as part of conversation history
        Delete: Cascade deleted when conversation deleted

    Validation Rules:
        - conversation_id must reference existing conversation
        - role must be either "user" or "assistant"
        - content cannot be empty or whitespace-only
        - content maximum length: 10,000 characters

    Constitution Compliance:
        - Conversation Continuity: All messages persisted, retrievable across restarts
        - Stateless: No in-memory message storage
    """

    __tablename__ = "todo_messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )

    conversation_id: UUID = Field(
        foreign_key="todo_conversations.id",
        index=True,
        description="Which conversation this message belongs to"
    )

    role: str = Field(
        max_length=20,
        description="Message sender role (user or assistant)"
    )

    content: str = Field(
        max_length=10000,
        description="The message content"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="When message was created"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "223e4567-e89b-12d3-a456-426614174001",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2025-01-24T10:30:00Z"
            }
        }


class MessagePublic(SQLModel):
    """Public message information."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime


class MessageCreate(SQLModel):
    """Schema for creating a new message."""

    conversation_id: UUID
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=10000)


class MessageList(SQLModel):
    """Schema for listing messages in a conversation."""

    messages: list[MessagePublic]
    count: int
