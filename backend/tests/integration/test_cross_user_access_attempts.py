"""
Integration test for cross-user access prevention (T052).

This test verifies that:
- Unauthorized access attempts are prevented (404 or None when user_id mismatch)
- Users cannot access, modify, or delete resources owned by other users
- All operations properly validate user ownership
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.task_service import TaskService


@pytest.mark.asyncio
async def test_get_task_wrong_user_returns_none(db_session: AsyncSession):
    """
    Test that getting a task owned by another user returns None.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates a task
    task = await task_service.create_task(
        user_id=user1_id,
        title="User 1's task"
    )
    task_id = task["task_id"]

    # Act - User 2 tries to get User 1's task
    result = await task_service.get_task(
        task_id=task_id,
        user_id=user2_id  # Wrong user
    )

    # Assert - Should return None (access denied)
    assert result is None


@pytest.mark.asyncio
async def test_complete_task_wrong_user_returns_none(db_session: AsyncSession):
    """
    Test that completing a task owned by another user returns None.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates a task
    task = await task_service.create_task(
        user_id=user1_id,
        title="User 1's task"
    )
    task_id = task["task_id"]

    # Act - User 2 tries to complete User 1's task
    result = await task_service.complete_task(
        task_id=task_id,
        user_id=user2_id  # Wrong user
    )

    # Assert - Should return None (operation rejected)
    assert result is None

    # Verify task is still not completed
    user1_tasks = await task_service.list_tasks(user_id=user1_id)
    task_data = next(t for t in user1_tasks if t["task_id"] == task_id)
    assert task_data["completed"] is False


@pytest.mark.asyncio
async def test_delete_task_wrong_user_returns_none(db_session: AsyncSession):
    """
    Test that deleting a task owned by another user returns None.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates a task
    task = await task_service.create_task(
        user_id=user1_id,
        title="User 1's task"
    )
    task_id = task["task_id"]

    # Act - User 2 tries to delete User 1's task
    result = await task_service.delete_task(
        task_id=task_id,
        user_id=user2_id  # Wrong user
    )

    # Assert - Should return None (operation rejected)
    assert result is None

    # Verify task still exists
    user1_tasks = await task_service.list_tasks(user_id=user1_id)
    assert any(t["task_id"] == task_id for t in user1_tasks)


@pytest.mark.asyncio
async def test_update_task_wrong_user_returns_none(db_session: AsyncSession):
    """
    Test that updating a task owned by another user returns None.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates a task
    task = await task_service.create_task(
        user_id=user1_id,
        title="Original title"
    )
    task_id = task["task_id"]

    # Act - User 2 tries to update User 1's task
    result = await task_service.update_task(
        task_id=task_id,
        user_id=user2_id,  # Wrong user
        title="Modified title"
    )

    # Assert - Should return None (operation rejected)
    assert result is None

    # Verify task was not modified
    user1_tasks = await task_service.list_tasks(user_id=user1_id)
    task_data = next(t for t in user1_tasks if t["task_id"] == task_id)
    assert task_data["title"] == "Original title"


@pytest.mark.asyncio
async def test_list_tasks_only_returns_own_tasks(db_session: AsyncSession):
    """
    Test that list_tasks only returns tasks owned by the requesting user.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates 2 tasks
    await task_service.create_task(user_id=user1_id, title="User 1 - Task A")
    await task_service.create_task(user_id=user1_id, title="User 1 - Task B")

    # User 2 creates 3 tasks
    await task_service.create_task(user_id=user2_id, title="User 2 - Task X")
    await task_service.create_task(user_id=user2_id, title="User 2 - Task Y")
    await task_service.create_task(user_id=user2_id, title="User 2 - Task Z")

    # Act - User 1 lists tasks
    user1_tasks = await task_service.list_tasks(user_id=user1_id)

    # Act - User 2 lists tasks
    user2_tasks = await task_service.list_tasks(user_id=user2_id)

    # Assert - User 1 only sees their tasks
    assert len(user1_tasks) == 2
    assert all(task["user_id"] == str(user1_id) for task in user1_tasks)

    # Assert - User 2 only sees their tasks
    assert len(user2_tasks) == 3
    assert all(task["user_id"] == str(user2_id) for task in user2_tasks)


@pytest.mark.asyncio
async def test_conversation_access_denied_for_wrong_user(db_session: AsyncSession):
    """
    Test that conversation history is denied for users who don't own it.
    """
    # Arrange
    from src.services.chat_service import ChatService
    from uuid import UUID

    user1_id = uuid4()
    user2_id = uuid4()
    chat_service = ChatService(db_session)

    # User 1 creates a conversation
    conv = await chat_service.create_conversation(user_id=user1_id)
    conv_id = UUID(conv["conversation_id"])

    await chat_service.save_message(
        conversation_id=conv_id,
        role="user",
        content="Private message"
    )

    # Act - User 2 tries to access User 1's conversation
    result = await chat_service.get_conversation_history(
        conversation_id=conv_id,
        user_id=user2_id  # Wrong user
    )

    # Assert - Should return None (access denied)
    assert result is None


@pytest.mark.asyncio
async def test_cascade_operations_respect_user_ownership(db_session: AsyncSession):
    """
    Test that even with cascade relationships, user ownership is respected.
    """
    # Arrange
    from src.services.chat_service import ChatService
    from uuid import UUID

    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)
    chat_service = ChatService(db_session)

    # User 1 creates a conversation and adds messages
    conv = await chat_service.create_conversation(user_id=user1_id)
    conv_id = UUID(conv["conversation_id"])

    await chat_service.save_message(
        conversation_id=conv_id,
        role="user",
        content="User 1's message"
    )

    # User 1 creates a task
    task = await task_service.create_task(
        user_id=user1_id,
        title="User 1's task"
    )

    # Act - User 2 tries to list everything
    user2_tasks = await task_service.list_tasks(user_id=user2_id)
    user2_conv = await chat_service.get_conversation_history(
        conversation_id=conv_id,
        user_id=user2_id
    )

    # Assert - User 2 should see nothing
    assert len(user2_tasks) == 0
    assert user2_conv is None


@pytest.mark.asyncio
async def test_batch_operations_isolated_by_user(db_session: AsyncSession):
    """
    Test that batch operations respect user isolation.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates multiple tasks
    task_ids_1 = []
    for i in range(3):
        task = await task_service.create_task(
            user_id=user1_id,
            title=f"User 1 - Task {i+1}"
        )
        task_ids_1.append(task["task_id"])

    # User 2 creates multiple tasks
    task_ids_2 = []
    for i in range(2):
        task = await task_service.create_task(
            user_id=user2_id,
            title=f"User 2 - Task {i+1}"
        )
        task_ids_2.append(task["task_id"])

    # Act - User 2 tries to complete all User 1's tasks
    for task_id in task_ids_1:
        result = await task_service.complete_task(
            task_id=task_id,
            user_id=user2_id  # Wrong user
        )
        assert result is None  # All should fail

    # Assert - User 1's tasks should remain uncompleted
    user1_tasks = await task_service.list_tasks(user_id=user1_id)
    for task in user1_tasks:
        assert task["completed"] is False

    # Act - User 1 can complete their own tasks
    for task_id in task_ids_1:
        result = await task_service.complete_task(
            task_id=task_id,
            user_id=user1_id  # Correct user
        )
        assert result is not None  # All should succeed


@pytest.mark.asyncio
async def test_no_data_leakage_in_error_messages(db_session: AsyncSession):
    """
    Test that error messages don't leak information about other users' resources.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates a task
    task = await task_service.create_task(
        user_id=user1_id,
        title="User 1's secret task"
    )
    task_id = task["task_id"]

    # Act - User 2 tries various operations
    get_result = await task_service.get_task(task_id=task_id, user_id=user2_id)
    complete_result = await task_service.complete_task(task_id=task_id, user_id=user2_id)
    delete_result = await task_service.delete_task(task_id=task_id, user_id=user2_id)

    # Assert - All operations should return None (no error messages, no data leakage)
    assert get_result is None
    assert complete_result is None
    assert delete_result is None

    # No exception should be raised, and no task data should be exposed
