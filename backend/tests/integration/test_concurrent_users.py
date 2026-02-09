"""
Integration test for concurrent users (T053).

This test verifies that:
- 10+ simultaneous users can operate without data mixing
- High concurrency doesn't cause race conditions or cross-user data leakage
- System maintains isolation under load
"""

import pytest
import asyncio
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.task_service import TaskService
from src.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_ten_concurrent_users_create_tasks(db_session: AsyncSession):
    """
    Test that 10 concurrent users can create tasks simultaneously without data mixing.
    """
    # Arrange
    num_users = 10
    user_ids = [uuid4() for _ in range(num_users)]
    task_service = TaskService(db_session)

    async def create_tasks_for_user(user_id: UUID, task_count: int = 5):
        """Create multiple tasks for a single user."""
        tasks = []
        for i in range(task_count):
            task = await task_service.create_task(
                user_id=user_id,
                title=f"User {str(user_id)[:8]} - Task {i+1}"
            )
            tasks.append(task)
        return tasks

    # Act - All users create tasks concurrently
    tasks = await asyncio.gather(*[
        create_tasks_for_user(user_id, 5)
        for user_id in user_ids
    ])

    # Assert - Verify each user has exactly 5 tasks
    for i, user_id in enumerate(user_ids):
        user_tasks = await task_service.list_tasks(user_id=user_id)
        assert len(user_tasks) == 5, f"User {i} should have 5 tasks"

        # Verify all tasks belong to this user
        assert all(task["user_id"] == str(user_id) for task in user_tasks)

        # Verify no cross-contamination from other users
        for task in user_tasks:
            assert f"User {str(user_id)[:8]}" in task["title"]


@pytest.mark.asyncio
async def test_ten_concurrent_users_with_conversations(db_session: AsyncSession):
    """
    Test that 10 concurrent users can create conversations without data mixing.
    """
    # Arrange
    num_users = 10
    user_ids = [uuid4() for _ in range(num_users)]
    chat_service = ChatService(db_session)

    async def create_conversation_for_user(user_id: UUID):
        """Create a conversation with messages for a user."""
        conv = await chat_service.create_conversation(user_id=user_id)
        conv_id = UUID(conv["conversation_id"])

        # Add a few messages
        await chat_service.save_message(
            conversation_id=conv_id,
            role="user",
            content=f"Message from {str(user_id)[:8]}"
        )
        await chat_service.save_message(
            conversation_id=conv_id,
            role="assistant",
            content=f"Response to {str(user_id)[:8]}"
        )

        return conv_id

    # Act - All users create conversations concurrently
    conversation_ids = await asyncio.gather(*[
        create_conversation_for_user(user_id)
        for user_id in user_ids
    ])

    # Assert - Verify each user's conversation is isolated
    for i, (user_id, conv_id) in enumerate(zip(user_ids, conversation_ids)):
        history = await chat_service.get_conversation_history(
            conversation_id=conv_id,
            user_id=user_id
        )

        assert history is not None
        assert len(history) == 2
        assert f"Message from {str(user_id)[:8]}" in history[0]["content"]
        assert f"Response to {str(user_id)[:8]}" in history[1]["content"]


@pytest.mark.asyncio
async def test_concurrent_operations_no_data_mixing(db_session: AsyncSession):
    """
    Test that concurrent create, read, update, delete operations don't mix data.
    """
    # Arrange
    num_users = 15
    user_ids = [uuid4() for _ in range(num_users)]
    task_service = TaskService(db_session)

    async def user_operations(user_id: UUID):
        """Simulate a user performing various operations."""
        # Create tasks
        tasks = []
        for i in range(3):
            task = await task_service.create_task(
                user_id=user_id,
                title=f"User {str(user_id)[:8]} - Task {i+1}"
            )
            tasks.append(task["task_id"])

        # Complete first task
        if tasks:
            await task_service.complete_task(
                task_id=tasks[0],
                user_id=user_id
            )

        # Update second task
        if len(tasks) > 1:
            await task_service.update_task(
                task_id=tasks[1],
                user_id=user_id,
                title=f"Updated: User {str(user_id)[:8]} - Task 2"
            )

        # Delete third task
        if len(tasks) > 2:
            await task_service.delete_task(
                task_id=tasks[2],
                user_id=user_id
            )

        # List tasks
        return await task_service.list_tasks(user_id=user_id)

    # Act - All users perform operations concurrently
    results = await asyncio.gather(*[
        user_operations(user_id)
        for user_id in user_ids
    ])

    # Assert - Verify each user's data is correct
    for i, (user_id, user_tasks) in enumerate(zip(user_ids, results)):
        # Each user should have 2 tasks (1 created, 1 completed, 1 deleted)
        assert len(user_tasks) == 2, f"User {i} should have 2 tasks"

        # Verify all tasks belong to this user
        assert all(task["user_id"] == str(user_id) for task in user_tasks)

        # Verify no cross-user contamination
        for task in user_tasks:
            assert str(user_id)[:8] in task["title"]


@pytest.mark.asyncio
async def test_stress_concurrent_user_isolation(db_session: AsyncSession):
    """
    Stress test with 20 concurrent users performing rapid operations.
    """
    # Arrange
    num_users = 20
    user_ids = [uuid4() for _ in range(num_users)]
    task_service = TaskService(db_session)

    async def rapid_operations(user_id: UUID):
        """Perform rapid operations to stress test isolation."""
        operations = []

        # Create 10 tasks rapidly
        for i in range(10):
            task = await task_service.create_task(
                user_id=user_id,
                title=f"User {str(user_id)[:8]} - Task {i+1}"
            )
            operations.append(("create", task["task_id"]))

        # List tasks
        user_tasks = await task_service.list_tasks(user_id=user_id)
        operations.append(("list", len(user_tasks)))

        # Complete half the tasks
        for i in range(0, len(user_tasks), 2):
            await task_service.complete_task(
                task_id=user_tasks[i]["task_id"],
                user_id=user_id
            )
            operations.append(("complete", user_tasks[i]["task_id"]))

        return operations

    # Act - Run stress test concurrently
    results = await asyncio.gather(*[
        rapid_operations(user_id)
        for user_id in user_ids
    ])

    # Assert - Verify isolation maintained
    for i, (user_id, operations) in enumerate(zip(user_ids, results)):
        # Count creates
        creates = [op for op in operations if op[0] == "create"]
        assert len(creates) == 10, f"User {i} should have created 10 tasks"

        # Verify list operation count
        lists = [op for op in operations if op[0] == "list"]
        assert lists[0][1] == 10, f"User {i} should list 10 tasks"

        # Verify final state
        user_tasks = await task_service.list_tasks(user_id=user_id)
        assert len(user_tasks) == 10, f"User {i} should still have 10 tasks"

        # Verify ownership
        assert all(task["user_id"] == str(user_id) for task in user_tasks)


@pytest.mark.asyncio
async def test_concurrent_conversation_and_task_operations(db_session: AsyncSession):
    """
    Test concurrent conversation and task operations maintain isolation.
    """
    # Arrange
    num_users = 12
    user_ids = [uuid4() for _ in range(num_users)]
    task_service = TaskService(db_session)
    chat_service = ChatService(db_session)

    async def mixed_operations(user_id: UUID):
        """Perform mixed task and conversation operations."""
        # Create tasks
        for i in range(3):
            await task_service.create_task(
                user_id=user_id,
                title=f"User {str(user_id)[:8]} - Task {i+1}"
            )

        # Create conversation
        conv = await chat_service.create_conversation(user_id=user_id)
        conv_id = UUID(conv["conversation_id"])

        # Add messages
        await chat_service.save_message(
            conversation_id=conv_id,
            role="user",
            content=f"User {str(user_id)[:8]} message"
        )

        # Get conversation history
        history = await chat_service.get_conversation_history(
            conversation_id=conv_id,
            user_id=user_id
        )

        # Get tasks
        tasks = await task_service.list_tasks(user_id=user_id)

        return {
            "user_id": user_id,
            "task_count": len(tasks),
            "message_count": len(history) if history else 0
        }

    # Act - Run mixed operations concurrently
    results = await asyncio.gather(*[
        mixed_operations(user_id)
        for user_id in user_ids
    ])

    # Assert - Verify isolation
    for result in results:
        assert result["task_count"] == 3
        assert result["message_count"] == 1


@pytest.mark.asyncio
async def test_no_race_conditions_in_concurrent_access(db_session: AsyncSession):
    """
    Test that concurrent access to same conversation/task doesn't cause race conditions.
    """
    # Arrange
    user_id = uuid4()
    task_service = TaskService(db_session)
    chat_service = ChatService(db_session)

    # Create conversation and tasks
    conv = await chat_service.create_conversation(user_id=user_id)
    conv_id = UUID(conv["conversation_id"])

    task_ids = []
    for i in range(5):
        task = await task_service.create_task(
            user_id=user_id,
            title=f"Task {i+1}"
        )
        task_ids.append(task["task_id"])

    async def concurrent_message_adds():
        """Add multiple messages concurrently."""
        tasks = []
        for i in range(10):
            task = chat_service.save_message(
                conversation_id=conv_id,
                role="user",
                content=f"Concurrent message {i+1}"
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def concurrent_task_completions():
        """Complete multiple tasks concurrently."""
        tasks = []
        for task_id in task_ids:
            task = task_service.complete_task(
                task_id=task_id,
                user_id=user_id
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    # Act - Run concurrent operations
    await asyncio.gather(
        concurrent_message_adds(),
        concurrent_task_completions()
    )

    # Assert - Verify all operations succeeded without corruption
    history = await chat_service.get_conversation_history(
        conversation_id=conv_id,
        user_id=user_id
    )

    assert history is not None
    assert len(history) == 10

    tasks = await task_service.list_tasks(user_id=user_id)
    assert len(tasks) == 5
    assert all(task["completed"] for task in tasks)
