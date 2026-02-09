"""
Integration test for multi-user task isolation (T051).

This test verifies that:
- Multiple users can create tasks simultaneously without cross-user visibility
- Each user only sees their own tasks
- No data leakage between users
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.task_service import TaskService


@pytest.mark.asyncio
async def test_concurrent_task_operations_no_visibility(db_session: AsyncSession):
    """
    Test that two users creating tasks simultaneously don't see each other's tasks.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates tasks
    task1 = await task_service.create_task(
        user_id=user1_id,
        title="User 1 - Task A"
    )
    task2 = await task_service.create_task(
        user_id=user1_id,
        title="User 1 - Task B"
    )

    # User 2 creates tasks
    task3 = await task_service.create_task(
        user_id=user2_id,
        title="User 2 - Task X"
    )
    task4 = await task_service.create_task(
        user_id=user2_id,
        title="User 2 - Task Y"
    )

    # Act - User 1 retrieves their tasks
    user1_tasks = await task_service.list_tasks(user_id=user1_id)

    # Act - User 2 retrieves their tasks
    user2_tasks = await task_service.list_tasks(user_id=user2_id)

    # Assert - User 1 only sees their own tasks
    assert len(user1_tasks) == 2
    assert all(task["user_id"] == str(user1_id) for task in user1_tasks)
    task_titles_1 = [task["title"] for task in user1_tasks]
    assert "User 1 - Task A" in task_titles_1
    assert "User 1 - Task B" in task_titles_1
    assert "User 2 - Task X" not in task_titles_1
    assert "User 2 - Task Y" not in task_titles_1

    # Assert - User 2 only sees their own tasks
    assert len(user2_tasks) == 2
    assert all(task["user_id"] == str(user2_id) for task in user2_tasks)
    task_titles_2 = [task["title"] for task in user2_tasks]
    assert "User 2 - Task X" in task_titles_2
    assert "User 2 - Task Y" in task_titles_2
    assert "User 1 - Task A" not in task_titles_2
    assert "User 1 - Task B" not in task_titles_2


@pytest.mark.asyncio
async def test_task_operations_isolated_by_user(db_session: AsyncSession):
    """
    Test that all task operations (create, list, complete, delete, update) are isolated by user.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates a task
    task1 = await task_service.create_task(
        user_id=user1_id,
        title="User 1's private task"
    )
    task1_id = task1["task_id"]

    # User 2 creates a task with the same title
    task2 = await task_service.create_task(
        user_id=user2_id,
        title="User 1's private task"  # Same title, different user
    )
    task2_id = task2["task_id"]

    # Act & Assert - User 2 cannot complete User 1's task
    result = await task_service.complete_task(
        task_id=task1_id,
        user_id=user2_id  # User 2 trying to complete User 1's task
    )
    assert result is None  # Should return None (operation rejected)

    # Verify User 1's task is still not completed
    user1_tasks = await task_service.list_tasks(user_id=user1_id)
    user1_task = [t for t in user1_tasks if t["task_id"] == task1_id][0]
    assert user1_task["completed"] is False

    # Act & Assert - User 1 can complete their own task
    result = await task_service.complete_task(
        task_id=task1_id,
        user_id=user1_id
    )
    assert result is not None
    assert result["completed"] is True

    # Act & Assert - User 2 cannot delete User 1's task
    result = await task_service.delete_task(
        task_id=task1_id,
        user_id=user2_id  # Wrong user
    )
    assert result is None

    # Verify User 1's task still exists
    user1_tasks = await task_service.list_tasks(user_id=user1_id)
    assert any(t["task_id"] == task1_id for t in user1_tasks)

    # Act & Assert - User 2 can delete their own task
    result = await task_service.delete_task(
        task_id=task2_id,
        user_id=user2_id
    )
    assert result is not None

    # Verify User 2's task is deleted
    user2_tasks = await task_service.list_tasks(user_id=user2_id)
    assert not any(t["task_id"] == task2_id for t in user2_tasks)


@pytest.mark.asyncio
async def test_conversation_isolation_by_user(db_session: AsyncSession):
    """
    Test that conversations are isolated by user.
    """
    # Arrange
    from src.services.chat_service import ChatService

    user1_id = uuid4()
    user2_id = uuid4()
    chat_service = ChatService(db_session)

    # User 1 creates a conversation
    conv1 = await chat_service.create_conversation(user_id=user1_id)
    conv1_id = conv1["conversation_id"]

    await chat_service.save_message(
        conversation_id=conv1_id,
        role="user",
        content="User 1's private message"
    )

    # User 2 creates a conversation
    conv2 = await chat_service.create_conversation(user_id=user2_id)
    conv2_id = conv2["conversation_id"]

    await chat_service.save_message(
        conversation_id=conv2_id,
        role="user",
        content="User 2's private message"
    )

    # Act - User 1 retrieves their conversation history
    from uuid import UUID
    history1 = await chat_service.get_conversation_history(
        conversation_id=UUID(conv1_id),
        user_id=user1_id
    )

    # Act - User 2 tries to retrieve User 1's conversation
    history2 = await chat_service.get_conversation_history(
        conversation_id=UUID(conv1_id),
        user_id=user2_id
    )

    # Assert - User 1 can see their conversation
    assert history1 is not None
    assert len(history1) == 1
    assert history1[0]["content"] == "User 1's private message"

    # Assert - User 2 cannot see User 1's conversation
    assert history2 is None


@pytest.mark.asyncio
async def test_multiple_users_same_task_titles(db_session: AsyncSession):
    """
    Test that multiple users can have tasks with the same title without interference.
    """
    # Arrange
    user_ids = [uuid4() for _ in range(5)]
    task_service = TaskService(db_session)

    task_title = "Buy groceries"

    # All users create tasks with the same title
    task_ids = []
    for user_id in user_ids:
        task = await task_service.create_task(
            user_id=user_id,
            title=task_title
        )
        task_ids.append(task["task_id"])

    # Act - Each user retrieves their tasks
    all_tasks = []
    for user_id in user_ids:
        tasks = await task_service.list_tasks(user_id=user_id)
        all_tasks.append(tasks)

    # Assert - Each user should have exactly 1 task
    for i, tasks in enumerate(all_tasks):
        assert len(tasks) == 1
        assert tasks[0]["user_id"] == str(user_ids[i])
        assert tasks[0]["title"] == task_title
        assert tasks[0]["task_id"] == task_ids[i]

    # Assert - All task IDs are different
    assert len(set(task_ids)) == 5


@pytest.mark.asyncio
async def test_task_count_isolated_by_user(db_session: AsyncSession):
    """
    Test that task counts are accurate and isolated per user.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()
    task_service = TaskService(db_session)

    # User 1 creates 3 tasks
    for i in range(3):
        await task_service.create_task(
            user_id=user1_id,
            title=f"User 1 - Task {i+1}"
        )

    # User 2 creates 5 tasks
    for i in range(5):
        await task_service.create_task(
            user_id=user2_id,
            title=f"User 2 - Task {i+1}"
        )

    # Act - Retrieve tasks for both users
    user1_tasks = await task_service.list_tasks(user_id=user1_id)
    user2_tasks = await task_service.list_tasks(user_id=user2_id)

    # Assert - Verify counts
    assert len(user1_tasks) == 3
    assert len(user2_tasks) == 5

    # Assert - Verify no cross-contamination
    assert all(task["user_id"] == str(user1_id) for task in user1_tasks)
    assert all(task["user_id"] == str(user2_id) for task in user2_tasks)
