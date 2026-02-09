"""
Unit tests for ChatService (T045).

Tests ChatService business logic with mocked database operations.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.chat_service import ChatService
from src.models.message import MessageRole


@pytest.mark.asyncio
async def test_create_conversation_calls_session_add():
    """Test that create_conversation adds conversation to session."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add = Mock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Create a mock conversation that will be returned
    mock_conversation = Mock()
    mock_conversation.id = uuid4()
    mock_conversation.user_id = uuid4()
    mock_conversation.created_at = datetime.utcnow()

    # Mock refresh to set the conversation attributes
    async def mock_refresh(obj):
        obj.id = mock_conversation.id
        obj.user_id = mock_conversation.user_id
        obj.created_at = mock_conversation.created_at

    mock_session.refresh.side_effect = mock_refresh

    user_id = uuid4()
    chat_service = ChatService(mock_session)

    # Act
    result = await chat_service.create_conversation(user_id=user_id)

    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert result["user_id"] == str(user_id)
    assert "conversation_id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_get_conversation_history_with_valid_conversation():
    """Test get_conversation_history returns messages for valid conversation."""
    # Arrange
    from unittest.mock import MagicMock
    from sqlmodel import select

    mock_session = AsyncMock(spec=AsyncSession)

    conversation_id = uuid4()
    user_id = uuid4()

    # Mock conversation result
    mock_conversation = Mock()
    mock_conversation.id = conversation_id
    mock_conversation.user_id = user_id

    # Mock message results
    mock_msg1 = Mock()
    mock_msg1.id = uuid4()
    mock_msg1.conversation_id = conversation_id
    mock_msg1.role = MessageRole.USER
    mock_msg1.content = "Test message"
    mock_msg1.created_at = datetime.utcnow()

    # Setup mock execute to return conversation first
    mock_result = AsyncMock()
    mock_conversation_result = MagicMock()
    mock_conversation_result.scalar_one_or_none.return_value = mock_conversation

    # Setup message result
    mock_message_result = MagicMock()
    mock_message_result.scalars.return_value.all.return_value = [mock_msg1]

    # Execute returns different results based on call
    call_count = [0]

    async def mock_execute(stmt):
        call_count[0] += 1
        if call_count[0] == 1:  # First call for conversation
            return mock_conversation_result
        else:  # Second call for messages
            return mock_message_result

    mock_session.execute.side_effect = mock_execute

    chat_service = ChatService(mock_session)

    # Act
    result = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id
    )

    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0]["content"] == "Test message"
    assert result[0]["role"] == "user"


@pytest.mark.asyncio
async def test_get_conversation_history_with_invalid_conversation():
    """Test get_conversation_history returns None for non-existent conversation."""
    # Arrange
    from unittest.mock import MagicMock

    mock_session = AsyncMock(spec=AsyncSession)

    conversation_id = uuid4()
    user_id = uuid4()

    # Mock no conversation found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    chat_service = ChatService(mock_session)

    # Act
    result = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id
    )

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_save_message_with_valid_data():
    """Test save_message creates and persists message."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add = Mock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    conversation_id = uuid4()

    # Create a mock message
    mock_message = Mock()
    mock_message.id = uuid4()
    mock_message.conversation_id = conversation_id
    mock_message.role = MessageRole.USER
    mock_message.content = "Test message"
    mock_message.created_at = datetime.utcnow()

    # Mock refresh to set the message attributes
    async def mock_refresh(obj):
        obj.id = mock_message.id
        obj.conversation_id = mock_message.conversation_id
        obj.role = mock_message.role
        obj.content = mock_message.content
        obj.created_at = mock_message.created_at

    mock_session.refresh.side_effect = mock_refresh

    chat_service = ChatService(mock_session)

    # Act
    result = await chat_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content="Test message"
    )

    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert result["conversation_id"] == str(conversation_id)
    assert result["role"] == "user"
    assert result["content"] == "Test message"


@pytest.mark.asyncio
async def test_save_message_with_invalid_role():
    """Test save_message raises ValueError for invalid role."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    chat_service = ChatService(mock_session)
    conversation_id = uuid4()

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid role"):
        await chat_service.save_message(
            conversation_id=conversation_id,
            role="invalid_role",
            content="Test message"
        )


@pytest.mark.asyncio
async def test_save_message_with_empty_content():
    """Test save_message raises ValueError for empty content."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    chat_service = ChatService(mock_session)
    conversation_id = uuid4()

    # Act & Assert
    with pytest.raises(ValueError, match="cannot be empty"):
        await chat_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content=""
        )

    with pytest.raises(ValueError, match="cannot be empty"):
        await chat_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content="   "
        )


@pytest.mark.asyncio
async def test_save_message_strips_whitespace():
    """Test save_message strips leading/trailing whitespace from content."""
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add = Mock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    conversation_id = uuid4()

    # Mock message
    mock_message = Mock()
    mock_message.id = uuid4()
    mock_message.conversation_id = conversation_id
    mock_message.role = MessageRole.USER
    mock_message.content = "Test message"  # After stripping
    mock_message.created_at = datetime.utcnow()

    async def mock_refresh(obj):
        obj.content = mock_message.content

    mock_session.refresh.side_effect = mock_refresh

    chat_service = ChatService(mock_session)

    # Act
    result = await chat_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content="  Test message  "
    )

    # Assert
    assert result["content"] == "Test message"
