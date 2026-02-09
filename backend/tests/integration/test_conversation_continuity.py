"""
Integration test for conversation persistence across server restart (T041).

This test verifies that:
- Conversations persist in the database across application restarts
- Message history is preserved and retrievable after reconnection
- User can continue conversation where they left off using conversation_id
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_conversation_persistence_across_sessions(db_session: AsyncSession):
    """
    Test that conversation persists across different database sessions.
    This simulates a server restart scenario.
    """
    # Arrange - First session (before restart)
    user_id = uuid4()
    conversation_id = None

    # Simulate first session
    async with db_session.begin():
        chat_service = ChatService(db_session)

        # Create conversation and add messages
        result = await chat_service.create_conversation(user_id=user_id)
        conversation_id = result["conversation_id"]

        await chat_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content="Add a task: Buy groceries"
        )
        await chat_service.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content="I've added the task 'Buy groceries' to your list"
        )

    # Act - Second session (after restart simulation)
    # Reconnect to the database and retrieve conversation
    async with db_session.begin():
        chat_service_reconnected = ChatService(db_session)

        # Retrieve conversation history using the same conversation_id
        history = await chat_service_reconnected.get_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id
        )

    # Assert - verify conversation was preserved
        assert history is not None
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Add a task: Buy groceries"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "I've added the task 'Buy groceries' to your list"


@pytest.mark.asyncio
async def test_conversation_continuation_after_reconnection(db_session: AsyncSession):
    """
    Test that user can continue conversation after reconnection by providing conversation_id.
    """
    # Arrange - First session
    user_id = uuid4()
    conversation_id = None

    async with db_session.begin():
        chat_service = ChatService(db_session)

        result = await chat_service.create_conversation(user_id=user_id)
        conversation_id = result["conversation_id"]

        await chat_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content="What tasks do I have?"
        )
        await chat_service.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content="You have 3 tasks: Buy groceries, Clean room, Call mom"
        )

    # Act - Second session: Continue conversation
    async with db_session.begin():
        chat_service_reconnected = ChatService(db_session)

        # Add new message to existing conversation
        await chat_service_reconnected.save_message(
            conversation_id=conversation_id,
            role="user",
            content="Mark 'Buy groceries' as complete"
        )
        await chat_service_reconnected.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content="I've marked 'Buy groceries' as complete"
        )

        # Get full history
        history = await chat_service_reconnected.get_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id
        )

    # Assert - verify full conversation history including continuation
        assert history is not None
        assert len(history) == 4
        assert history[0]["content"] == "What tasks do I have?"
        assert history[1]["content"] == "You have 3 tasks: Buy groceries, Clean room, Call mom"
        assert history[2]["content"] == "Mark 'Buy groceries' as complete"
        assert history[3]["content"] == "I've marked 'Buy groceries' as complete"


@pytest.mark.asyncio
async def test_conversation_metadata_preservation(db_session: AsyncSession):
    """
    Test that conversation metadata (created_at) is preserved across sessions.
    """
    # Arrange - First session
    from datetime import datetime

    user_id = uuid4()
    original_created_at = None

    async with db_session.begin():
        chat_service = ChatService(db_session)

        result = await chat_service.create_conversation(user_id=user_id)
        conversation_id = result["conversation_id"]
        original_created_at = result["created_at"]

    # Act - Second session: Retrieve conversation
    async with db_session.begin():
        from sqlmodel import select
        from src.models.conversation import Conversation

        chat_service_reconnected = ChatService(db_session)

        # Get conversation from database directly
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        db_result = await db_session.execute(stmt)
        conversation = db_result.scalar_one()

    # Assert - verify metadata preserved
        assert conversation is not None
        assert conversation.id == conversation_id
        assert conversation.user_id == user_id
        assert conversation.created_at == original_created_at
