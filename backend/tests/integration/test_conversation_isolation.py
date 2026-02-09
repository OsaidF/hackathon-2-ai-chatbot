"""
Integration test for conversation isolation (T042).

This test verifies that:
- Separate conversations don't leak messages between each other
- Each conversation maintains its own independent message history
- User cannot access conversations belonging to another user
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_separate_conversations_no_cross_contamination(db_session: AsyncSession):
    """
    Test that messages from separate conversations don't leak into each other.
    """
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Create two separate conversations
    conv1_result = await chat_service.create_conversation(user_id=user_id)
    conv1_id = conv1_result["conversation_id"]

    conv2_result = await chat_service.create_conversation(user_id=user_id)
    conv2_id = conv2_result["conversation_id"]

    # Add different messages to each conversation
    await chat_service.save_message(
        conversation_id=conv1_id,
        role="user",
        content="Conversation 1: Add task A"
    )
    await chat_service.save_message(
        conversation_id=conv1_id,
        role="assistant",
        content="Conversation 1: Task A added"
    )

    await chat_service.save_message(
        conversation_id=conv2_id,
        role="user",
        content="Conversation 2: Add task B"
    )
    await chat_service.save_message(
        conversation_id=conv2_id,
        role="assistant",
        content="Conversation 2: Task B added"
    )

    # Act - Retrieve both conversation histories
    history1 = await chat_service.get_conversation_history(
        conversation_id=conv1_id,
        user_id=user_id
    )
    history2 = await chat_service.get_conversation_history(
        conversation_id=conv2_id,
        user_id=user_id
    )

    # Assert - verify no cross-contamination
    assert len(history1) == 2
    assert len(history2) == 2

    # Verify conversation 1 only has its own messages
    assert all("Conversation 1" in msg["content"] for msg in history1)
    assert not any("Conversation 2" in msg["content"] for msg in history1)

    # Verify conversation 2 only has its own messages
    assert all("Conversation 2" in msg["content"] for msg in history2)
    assert not any("Conversation 1" in msg["content"] for msg in history2)


@pytest.mark.asyncio
async def test_different_users_conversations_isolated(db_session: AsyncSession):
    """
    Test that conversations for different users are completely isolated.
    """
    # Arrange
    user_id_1 = uuid4()
    user_id_2 = uuid4()
    chat_service = ChatService(db_session)

    # User 1 creates a conversation
    conv1_result = await chat_service.create_conversation(user_id=user_id_1)
    conv1_id = conv1_result["conversation_id"]

    await chat_service.save_message(
        conversation_id=conv1_id,
        role="user",
        content="User 1's private message"
    )

    # User 2 creates a conversation
    conv2_result = await chat_service.create_conversation(user_id=user_id_2)
    conv2_id = conv2_result["conversation_id"]

    await chat_service.save_message(
        conversation_id=conv2_id,
        role="user",
        content="User 2's private message"
    )

    # Act - User 1 tries to access User 2's conversation
    unauthorized_access = await chat_service.get_conversation_history(
        conversation_id=conv2_id,
        user_id=user_id_1
    )

    # Act - User 1 accesses their own conversation
    authorized_access = await chat_service.get_conversation_history(
        conversation_id=conv1_id,
        user_id=user_id_1
    )

    # Assert - User 1 cannot access User 2's conversation
    assert unauthorized_access is None

    # Assert - User 1 can access their own conversation
    assert authorized_access is not None
    assert len(authorized_access) == 1
    assert authorized_access[0]["content"] == "User 1's private message"


@pytest.mark.asyncio
async def test_conversation_count_independence(db_session: AsyncSession):
    """
    Test that message count is independent for each conversation.
    """
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Create three conversations
    conv_ids = []
    for i in range(3):
        result = await chat_service.create_conversation(user_id=user_id)
        conv_id = result["conversation_id"]
        conv_ids.append(conv_id)

    # Add different number of messages to each conversation
    await chat_service.save_message(
        conversation_id=conv_ids[0],
        role="user",
        content="Message 1 for conv 0"
    )

    await chat_service.save_message(
        conversation_id=conv_ids[1],
        role="user",
        content="Message 1 for conv 1"
    )
    await chat_service.save_message(
        conversation_id=conv_ids[1],
        role="assistant",
        content="Message 2 for conv 1"
    )

    await chat_service.save_message(
        conversation_id=conv_ids[2],
        role="user",
        content="Message 1 for conv 2"
    )
    await chat_service.save_message(
        conversation_id=conv_ids[2],
        role="assistant",
        content="Message 2 for conv 2"
    )
    await chat_service.save_message(
        conversation_id=conv_ids[2],
        role="user",
        content="Message 3 for conv 2"
    )

    # Act - Retrieve all conversation histories
    history0 = await chat_service.get_conversation_history(
        conversation_id=conv_ids[0],
        user_id=user_id
    )
    history1 = await chat_service.get_conversation_history(
        conversation_id=conv_ids[1],
        user_id=user_id
    )
    history2 = await chat_service.get_conversation_history(
        conversation_id=conv_ids[2],
        user_id=user_id
    )

    # Assert - verify independent message counts
    assert len(history0) == 1
    assert len(history1) == 2
    assert len(history2) == 3


@pytest.mark.asyncio
async def test_same_user_multiple_conversations(db_session: AsyncSession):
    """
    Test that a single user can have multiple isolated conversations.
    """
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Create multiple conversations for the same user
    work_conv = await chat_service.create_conversation(user_id=user_id)
    personal_conv = await chat_service.create_conversation(user_id=user_id)

    # Add work-related messages
    await chat_service.save_message(
        conversation_id=work_conv["conversation_id"],
        role="user",
        content="Add task: Finish quarterly report"
    )

    # Add personal-related messages
    await chat_service.save_message(
        conversation_id=personal_conv["conversation_id"],
        role="user",
        content="Add task: Buy birthday gift"
    )

    # Act - Retrieve both conversations
    work_history = await chat_service.get_conversation_history(
        conversation_id=work_conv["conversation_id"],
        user_id=user_id
    )
    personal_history = await chat_service.get_conversation_history(
        conversation_id=personal_conv["conversation_id"],
        user_id=user_id
    )

    # Assert - verify conversations are independent
    assert len(work_history) == 1
    assert "quarterly report" in work_history[0]["content"]

    assert len(personal_history) == 1
    assert "birthday gift" in personal_history[0]["content"]
