"""
TaskService - Business logic layer for task operations.

Provides stateless methods for CRUD operations on tasks.
All operations query the database directly per constitution principles.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


class TaskService:
    """
    Stateless service for task management operations.

    All methods are stateless and query the database directly.
    This ensures horizontal scaling and server restart resilience.

    Multi-User Enforcement:
        - All methods verify user ownership before operations
        - user_id filtering on all database queries
        - Cross-user access attempts return None
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize TaskService with database session.

        Args:
            session: Async SQLAlchemy session for database operations
        """
        self.session = session

    async def create_task(
        self,
        user_id: UUID,
        title: str
    ) -> dict:
        """
        Create a new task for a user.

        Args:
            user_id: Owner of the task
            title: Task description

        Returns:
            dict: Created task data with task_id, user_id, title, completed
        """
        task = Task(
            user_id=user_id,
            title=title,
            completed=False
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return {
            "task_id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "completed": task.completed
        }

    async def list_tasks(
        self,
        user_id: UUID,
        completed: Optional[bool] = None
    ) -> List[dict]:
        """
        List tasks for a user, optionally filtered by completion status.

        Args:
            user_id: Owner of the tasks
            completed: Optional filter (True=completed, False=uncompleted, None=all)

        Returns:
            List[dict]: List of tasks with task_id, user_id, title, completed
        """
        statement = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        result = await self.session.execute(statement)
        tasks = result.scalars().all()

        return [
            {
                "task_id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "completed": task.completed
            }
            for task in tasks
        ]

    async def get_task(
        self,
        task_id: UUID,
        user_id: UUID
    ) -> Optional[dict]:
        """
        Get a specific task by ID (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership

        Returns:
            Optional[dict]: Task data if found and owned by user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            return None

        return {
            "task_id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "completed": task.completed
        }

    async def complete_task(
        self,
        task_id: UUID,
        user_id: UUID
    ) -> Optional[dict]:
        """
        Mark a task as completed (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership

        Returns:
            Optional[dict]: Updated task data if found and owned by user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            return None

        task.completed = True
        await self.session.commit()
        await self.session.refresh(task)

        return {
            "task_id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "completed": task.completed
        }

    async def update_task(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str
    ) -> Optional[dict]:
        """
        Update task title (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership
            title: New task title

        Returns:
            Optional[dict]: Updated task data if found and owned by user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            return None

        task.title = title
        await self.session.commit()
        await self.session.refresh(task)

        return {
            "task_id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "completed": task.completed
        }

    async def delete_task(
        self,
        task_id: UUID,
        user_id: UUID
    ) -> Optional[dict]:
        """
        Delete a task (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership

        Returns:
            Optional[dict]: Deleted task data if found and owned by user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            return None

        task_data = {
            "task_id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "completed": task.completed
        }

        await self.session.delete(task)
        await self.session.commit()

        return task_data

    # Legacy methods for backward compatibility
    async def create(
        self,
        user_id: UUID,
        title: str,
        session: AsyncSession
    ) -> Task:
        """
        Create a new task.

        Args:
            user_id: Owner of the task
            title: Task description
            session: Database session

        Returns:
            Task: Created task
        """
        task = Task(
            id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder, DB will generate
            user_id=user_id,
            title=title,
            completed=False
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def list(
        self,
        user_id: UUID,
        completed: Optional[bool] = None,
        session: AsyncSession = None
    ) -> List[Task]:
        """
        List tasks for a user, optionally filtered by completion status.

        Args:
            user_id: Owner of the tasks
            completed: Optional filter (True=completed, False=uncompleted, None=all)
            session: Database session

        Returns:
            List[Task]: List of tasks
        """
        statement = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        result = await session.execute(statement)
        return list(result.scalars().all())

    async def get(
        self,
        task_id: UUID,
        user_id: UUID,
        session: AsyncSession = None
    ) -> Optional[Task]:
        """
        Get a specific task by ID (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership
            session: Database session

        Returns:
            Optional[Task]: Task if found and owned by user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        return result.one_or_none()

    async def complete(
        self,
        task_id: UUID,
        user_id: UUID,
        session: AsyncSession = None
    ) -> Optional[Task]:
        """
        Mark a task as completed (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership
            session: Database session

        Returns:
            Optional[Task]: Completed task if found and owned by user, None otherwise
        """
        task = await self.get(task_id, user_id, session)
        if task:
            task.completed = True
            await session.commit()
            await session.refresh(task)
        return task

    async def update(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str,
        session: AsyncSession = None
    ) -> Optional[Task]:
        """
        Update task title (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership
            title: New task title
            session: Database session

        Returns:
            Optional[Task]: Updated task if found and owned by user, None otherwise
        """
        task = await self.get(task_id, user_id, session)
        if task:
            task.title = title
            await session.commit()
            await session.refresh(task)
        return task

    async def delete(
        self,
        task_id: UUID,
        user_id: UUID,
        session: AsyncSession = None
    ) -> bool:
        """
        Delete a task (with user ownership verification).

        Args:
            task_id: Task identifier
            user_id: User claiming ownership
            session: Database session

        Returns:
            bool: True if deleted, False if not found or not owned by user
        """
        task = await self.get(task_id, user_id, session)
        if task:
            await session.delete(task)
            await session.commit()
            return True
        return False
