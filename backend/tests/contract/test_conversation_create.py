"""
Contract test for conversation creation (T039).

This test verifies that the ChatService.create_conversation method:
- Creates a new conversation with a unique conversation_id (UUID)
- Associates the conversation with a specific user_id
- Sets the created_at timestamp
- Returns the conversation with all required fields
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_create_conversation_returns_uuid(db_session: AsyncSession):
    """Test that create_conversation returns a valid UUID."""
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Act
    result = await chat_service.create_conversation(user_id=user_id)

    # Assert
    assert "conversation_id" in result
    assert isinstance(UUID(result["conversation_id"]), UUID)
    assert result["user_id"] == str(user_id)
    assert "created_at" in result
    assert isinstance(result["created_at"], datetime)


@pytest.mark.asyncio
async def test_create_conversation_persists_to_database(db_session: AsyncSession):
    """Test that create_conversation persists the conversation to the database."""
    # Arrange
    from sqlmodel import select
    from src.models.conversation import Conversation

    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Act
    result = await chat_service.create_conversation(user_id=user_id)
    conversation_id = UUID(result["conversation_id"])

    # Assert - verify it exists in database
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    db_result = await db_session.execute(stmt)
    conversation = db_result.scalar_one_or_none()

    assert conversation is not None
    assert conversation.id == conversation_id
    assert conversation.user_id == user_id


@pytest.mark.asyncio
async def test_create_conversation_unique_ids(db_session: AsyncSession):
    """Test that each call to create_conversation generates a unique conversation_id."""
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Act
    result1 = await chat_service.create_conversation(user_id=user_id)
    result2 = await chat_service.create_conversation(user_id=user_id)

    # Assert
    assert result1["conversation_id"] != result2["conversation_id"]


@pytest.mark.asyncio
async def test_create_conversation_different_users(db_session: AsyncSession):
    """Test that conversations for different users are isolated."""
    # Arrange
    user_id_1 = uuid4()
    user_id_2 = uuid4()
    chat_service = ChatService(db_session)

    # Act
    result1 = await chat_service.create_conversation(user_id=user_id_1)
    result2 = await chat_service.create_conversation(user_id=user_id_2)

    # Assert
    assert result1["user_id"] == str(user_id_1)
    assert result2["user_id"] == str(user_id_2)
    assert result1["conversation_id"] != result2["conversation_id"]
