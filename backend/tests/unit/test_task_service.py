"""
Unit tests for TaskService.

Tests business logic with mocked database.
Tests should FAIL before implementation, then PASS after.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.services.task_service import TaskService
from src.models.task import Task


@pytest.fixture
def task_service():
    """Provide TaskService instance."""
    return TaskService()


@pytest.fixture
def mock_session():
    """Provide mocked database session."""
    return AsyncMock()


class TestTaskServiceCreate:
    """Test task creation."""

    @pytest.mark.asyncio
    async def test_create_task(self, task_service, mock_session):
        """Test creating a new task."""
        user_id = uuid4()
        title = "Buy groceries"

        # Mock session behavior
        mock_task = Task(id=uuid4(), user_id=user_id, title=title, completed=False)
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = mock_task

        result = await task_service.create(user_id, title, mock_session)

        assert result.title == title
        assert result.completed is False
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


class TestTaskServiceList:
    """Test task listing."""

    @pytest.mark.asyncio
    async def test_list_all_tasks(self, task_service, mock_session):
        """Test listing all user tasks."""
        user_id = uuid4()
        tasks = [
            Task(id=uuid4(), user_id=user_id, title="Task 1", completed=False),
            Task(id=uuid4(), user_id=user_id, title="Task 2", completed=True),
        ]

        # Mock query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = tasks
        mock_session.execute.return_value = mock_result

        result = await task_service.list(user_id, session=mock_session)

        assert len(result) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_completed_tasks_only(self, task_service, mock_session):
        """Test filtering tasks by completion status."""
        user_id = uuid4()
        tasks = [
            Task(id=uuid4(), user_id=user_id, title="Task 1", completed=True),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = tasks
        mock_session.execute.return_value = mock_result

        result = await task_service.list(user_id, completed=True, session=mock_session)

        assert len(result) == 1
        assert all(t.completed for t in result)


class TestTaskServiceGet:
    """Test getting a specific task."""

    @pytest.mark.asyncio
    async def test_get_existing_task(self, task_service, mock_session):
        """Test getting an existing task owned by user."""
        user_id = uuid4()
        task_id = uuid4()
        task = Task(id=task_id, user_id=user_id, title="Test task", completed=False)

        mock_result = MagicMock()
        mock_result.one_or_none.return_value = task
        mock_session.execute.return_value = mock_result

        result = await task_service.get(task_id, user_id, mock_session)

        assert result is not None
        assert result.id == task_id
        assert result.user_id == user_id

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, task_service, mock_session):
        """Test getting a non-existent task."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await task_service.get(uuid4(), uuid4(), mock_session)

        assert result is None


class TestTaskServiceComplete:
    """Test marking task as completed."""

    @pytest.mark.asyncio
    async def test_complete_existing_task(self, task_service, mock_session):
        """Test completing an existing uncompleted task."""
        user_id = uuid4()
        task_id = uuid4()
        task = Task(id=task_id, user_id=user_id, title="Test task", completed=False)

        # Mock get operation
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = task
        mock_session.execute.return_value = mock_result

        result = await task_service.complete(task_id, user_id, mock_session)

        assert result is not None
        assert result.completed is True
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self, task_service, mock_session):
        """Test completing a non-existent task."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await task_service.complete(uuid4(), uuid4(), mock_session)

        assert result is None


class TestTaskServiceUpdate:
    """Test updating task title."""

    @pytest.mark.asyncio
    async def test_update_existing_task(self, task_service, mock_session):
        """Test updating an existing task."""
        user_id = uuid4()
        task_id = uuid4()
        task = Task(id=task_id, user_id=user_id, title="Old title", completed=False)

        # Mock get operation
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = task
        mock_session.execute.return_value = mock_result

        result = await task_service.update(task_id, user_id, "New title", mock_session)

        assert result is not None
        assert result.title == "New title"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, task_service, mock_session):
        """Test updating a non-existent task."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await task_service.update(uuid4(), uuid4(), "New title", mock_session)

        assert result is None


class TestTaskServiceDelete:
    """Test deleting tasks."""

    @pytest.mark.asyncio
    async def test_delete_existing_task(self, task_service, mock_session):
        """Test deleting an existing task."""
        user_id = uuid4()
        task_id = uuid4()
        task = Task(id=task_id, user_id=user_id, title="Test task", completed=False)

        # Mock get operation
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = task
        mock_session.execute.return_value = mock_result

        result = await task_service.delete(task_id, user_id, mock_session)

        assert result is True
        mock_session.delete.assert_called_once_with(task)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, task_service, mock_session):
        """Test deleting a non-existent task."""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await task_service.delete(uuid4(), uuid4(), mock_session)

        assert result is False
        mock_session.delete.assert_not_called()
