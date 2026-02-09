"""
SQLModel models for Todo AI Chatbot.

This module imports and registers all database models with SQLAlchemy metadata.
Importing this package ensures all models are available for ORM operations.
"""

from src.models.user import User, UserPublic, UserCreate, UserUpdate
from src.models.conversation import (
    Conversation,
    ConversationPublic,
    ConversationCreate,
)
from src.models.message import (
    Message,
    MessageRole,
    MessagePublic,
    MessageCreate,
    MessageList,
)
from src.models.task import (
    Task,
    TaskPublic,
    TaskCreate,
    TaskUpdate,
    TaskList,
)


__all__ = [
    # User models
    "User",
    "UserPublic",
    "UserCreate",
    "UserUpdate",
    # Conversation models
    "Conversation",
    "ConversationPublic",
    "ConversationCreate",
    # Message models
    "Message",
    "MessageRole",
    "MessagePublic",
    "MessageCreate",
    "MessageList",
    # Task models
    "Task",
    "TaskPublic",
    "TaskCreate",
    "TaskUpdate",
    "TaskList",
]
