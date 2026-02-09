"""
Contract test for conversation history retrieval (T040).

This test verifies that the ChatService.get_conversation_history method:
- Retrieves all messages for a given conversation_id in chronological order
- Returns messages with role, content, and created_at fields
- Returns empty list for conversations with no messages
- Enforces user ownership (returns 404 if conversation doesn't belong to user)
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_get_conversation_history_returns_messages(db_session: AsyncSession):
    """Test that get_conversation_history retrieves messages in chronological order."""
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Create conversation
    conversation_result = await chat_service.create_conversation(user_id=user_id)
    conversation_id = UUID(conversation_result["conversation_id"])

    # Add messages
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content="Hello, I need help with tasks"
    )
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content="I can help you manage your tasks"
    )

    # Act
    history = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id
    )

    # Assert
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello, I need help with tasks"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "I can help you manage your tasks"


@pytest.mark.asyncio
async def test_get_conversation_history_chronological_order(db_session: AsyncSession):
    """Test that messages are returned in chronological order (created_at ASC)."""
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    conversation_result = await chat_service.create_conversation(user_id=user_id)
    conversation_id = UUID(conversation_result["conversation_id"])

    # Add messages out of order (they should be sorted by created_at)
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content="First message"
    )
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content="Second message"
    )
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content="Third message"
    )

    # Act
    history = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id
    )

    # Assert - verify chronological order
    assert len(history) == 3
    assert history[0]["content"] == "First message"
    assert history[1]["content"] == "Second message"
    assert history[2]["content"] == "Third message"

    # Verify timestamps are in ascending order
    for i in range(len(history) - 1):
        assert history[i]["created_at"] <= history[i + 1]["created_at"]


@pytest.mark.asyncio
async def test_get_conversation_history_empty_conversation(db_session: AsyncSession):
    """Test that get_conversation_history returns empty list for new conversation."""
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    conversation_result = await chat_service.create_conversation(user_id=user_id)
    conversation_id = UUID(conversation_result["conversation_id"])

    # Act
    history = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id
    )

    # Assert
    assert history == []


@pytest.mark.asyncio
async def test_get_conversation_history_unauthorized_access(db_session: AsyncSession):
    """Test that get_conversation_history returns None for conversations owned by different user."""
    # Arrange
    user_id_1 = uuid4()
    user_id_2 = uuid4()
    chat_service = ChatService(db_session)

    # Create conversation for user_1
    conversation_result = await chat_service.create_conversation(user_id=user_id_1)
    conversation_id = UUID(conversation_result["conversation_id"])

    # Add a message
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content="Private message"
    )

    # Act - try to access with user_id_2
    history = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id_2
    )

    # Assert - should return None (conversation not found for this user)
    assert history is None


@pytest.mark.asyncio
async def test_get_conversation_history_nonexistent_conversation(db_session: AsyncSession):
    """Test that get_conversation_history returns None for non-existent conversation."""
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)
    fake_conversation_id = uuid4()

    # Act
    history = await chat_service.get_conversation_history(
        conversation_id=fake_conversation_id,
        user_id=user_id
    )

    # Assert
    assert history is None
