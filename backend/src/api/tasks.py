"""
Tasks API endpoints for Todo AI Chatbot.

Provides REST API endpoints for direct task management:
- GET /api/v1/tasks - List all tasks for authenticated user
- POST /api/v1/tasks - Create a new task
- PUT /api/v1/tasks/{task_id} - Update a task
- DELETE /api/v1/tasks/{task_id} - Delete a task
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional
from uuid import UUID

from src.db.session import get_session
from src.auth.dependencies import get_current_user
from src.models.task import Task, TaskPublic, TaskCreate, TaskUpdate, TaskList

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=TaskList)
async def list_tasks(
    filter_completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all tasks for the authenticated user.

    Args:
        filter_completed: Optional filter (True=completed only, False=uncompleted only)
        current_user: Authenticated user ID
        session: Database session

    Returns:
        TaskList with tasks array and count
    """
    # Build query
    statement = select(Task).where(Task.user_id == current_user)

    # Apply filter if specified
    if filter_completed is not None:
        statement = statement.where(Task.completed == filter_completed)

    # Order by created_at descending
    statement = statement.order_by(Task.created_at.desc())

    # Execute query
    result = await session.execute(statement)
    tasks = result.scalars().all()

    # Convert to public format
    task_publics = [
        TaskPublic(
            id=task.id,
            title=task.title,
            completed=task.completed,
            priority=task.priority,
            due_date=task.due_date,
            tags=task.tags,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]

    return TaskList(tasks=task_publics, count=len(task_publics))


@router.post("", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    Args:
        task_data: Task creation data
        current_user: Authenticated user ID
        session: Database session

    Returns:
        Created task
    """
    from datetime import datetime
    from uuid import uuid4

    # Create new task
    task = Task(
        id=uuid4(),
        user_id=current_user,
        title=task_data.title,
        completed=False,
        priority=task_data.priority or "medium",
        due_date=task_data.due_date,
        tags=task_data.tags,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskPublic(
        id=task.id,
        title=task.title,
        completed=task.completed,
        priority=task.priority,
        due_date=task.due_date,
        tags=task.tags,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/{task_id}", response_model=TaskPublic)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing task.

    Args:
        task_id: Task ID to update
        task_data: Task update data
        current_user: Authenticated user ID
        session: Database session

    Returns:
        Updated task
    """
    from datetime import datetime

    # Get task
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.tags is not None:
        task.tags = task_data.tags

    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskPublic(
        id=task.id,
        title=task.title,
        completed=task.completed,
        priority=task.priority,
        due_date=task.due_date,
        tags=task.tags,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a task.

    Args:
        task_id: Task ID to delete
        current_user: Authenticated user ID
        session: Database session
    """
    # Get task
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    await session.delete(task)
    await session.commit()
