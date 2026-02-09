"""
MCP Tool: update_task

Modifies properties of an existing task (title, completed, priority, due_date, tags).

Contract:
- Input: user_id (UUID), task_id (UUID), new_title (string 1-500 chars, optional),
        completed (bool, optional), priority (string: low/medium/high, optional),
        due_date (ISO datetime string, optional), tags (string, optional)
- Output: {task_id, status: "updated", title, completed, priority, due_date, tags, updated_at}
- Errors: INVALID_USER_ID, INVALID_TASK_ID, TASK_NOT_FOUND, INVALID_TITLE,
          INVALID_PRIORITY, INVALID_DUE_DATE, DATABASE_ERROR
"""

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


async def update_task(
    user_id: str,
    task_id: str,
    new_title: str = None,
    completed: bool = None,
    priority: str = None,
    due_date: str = None,
    tags: str = None,
    session: AsyncSession = None
) -> str:
    """
    Update properties of an existing task.

    Args:
        user_id: User identifier (UUID string)
        task_id: Task identifier (UUID string)
        new_title: New task title (1-500 characters, optional)
        completed: Task completion status (optional)
        priority: Task priority level (low/medium/high, optional)
        due_date: Task due date in ISO format (optional)
        tags: Task tags/categories (comma-separated, optional)
        session: Database session

    Returns:
        str: JSON string with updated task

    Raises:
        ValueError: If parameters are invalid or task not found
    """
    # Validate user_id
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError("INVALID_USER_ID: user_id must be a valid UUID")

    # Validate task_id
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise ValueError("INVALID_TASK_ID: task_id must be a valid UUID")

    # Validate new_title if provided
    if new_title is not None:
        if not new_title or not new_title.strip():
            raise ValueError("INVALID_TITLE: new_title cannot be empty")
        new_title = new_title.strip()
        if len(new_title) > 500:
            raise ValueError("INVALID_TITLE: new_title cannot exceed 500 characters")

    # Validate priority if provided
    if priority is not None:
        valid_priorities = ["low", "medium", "high"]
        if priority not in valid_priorities:
            raise ValueError(f"INVALID_PRIORITY: priority must be one of {valid_priorities}")

    # Parse due_date if provided
    parsed_due_date = None
    if due_date is not None:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("INVALID_DUE_DATE: due_date must be ISO format (e.g., 2025-01-25T10:30:00Z)")

    # Validate tags if provided
    if tags is not None:
        tags = tags.strip()
        if len(tags) > 500:
            raise ValueError("INVALID_TAGS: tags cannot exceed 500 characters")

    try:
        # Get task
        statement = select(Task).where(Task.id == task_uuid)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError("TASK_NOT_FOUND: Task does not exist")

        # Verify ownership
        if task.user_id != user_uuid:
            raise ValueError("TASK_NOT_FOUND: Task belongs to different user")

        # Update only provided fields
        if new_title is not None:
            task.title = new_title
        if completed is not None:
            task.completed = completed
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = parsed_due_date
        if tags is not None:
            task.tags = tags

        task.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(task)

        return json.dumps({
            "task_id": str(task.id),
            "status": "updated",
            "title": task.title,
            "completed": task.completed,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags,
            "updated_at": task.updated_at.isoformat()
        })

    except ValueError as e:
        # Re-raise our custom errors
        if "TASK_NOT_FOUND" in str(e) or "INVALID" in str(e):
            raise
        raise ValueError(f"DATABASE_ERROR: {str(e)}")
    except Exception as e:
        await session.rollback()
        raise ValueError(f"DATABASE_ERROR: {str(e)}")


# Tool schema for MCP server registration
TOOL_SCHEMA = {
    "description": "Modify properties of an existing task (title, completed, priority, due_date, tags). The user_id must match the task owner. At least one field to update must be provided.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "task_id": {
                "type": "string",
                "description": "Unique identifier of the task to update (UUID format)"
            },
            "new_title": {
                "type": "string",
                "description": "The new task title (1-500 characters)"
            },
            "completed": {
                "type": "boolean",
                "description": "Task completion status (true/false)"
            },
            "priority": {
                "type": "string",
                "description": "Task priority level",
                "enum": ["low", "medium", "high"]
            },
            "due_date": {
                "type": "string",
                "description": "Task due date in ISO format (e.g., 2025-01-25T10:30:00Z)"
            },
            "tags": {
                "type": "string",
                "description": "Task tags/categories (comma-separated)"
            }
        },
        "required": ["user_id", "task_id"]
    }
}
