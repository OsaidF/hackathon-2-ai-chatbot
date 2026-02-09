"""
MCP Tool: add_task

Creates a new todo task for a user.

Contract:
- Input: user_id (UUID), title (string 1-500 chars)
- Output: {task_id, status: "created", title, completed, created_at}
- Errors: INVALID_USER_ID, INVALID_TITLE, DATABASE_ERROR
"""

import json
from datetime import datetime
from typing import Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


async def add_task(
    user_id: str,
    title: str,
    priority: str = "medium",
    due_date: str = None,
    tags: str = None,
    session: AsyncSession = None
) -> str:
    """
    Create a new task for a user.

    Args:
        user_id: User identifier (UUID string)
        title: Task title (1-500 characters)
        priority: Task priority (low, medium, high) - defaults to medium
        due_date: Optional due date (ISO format string)
        tags: Optional comma-separated tags
        session: Database session

    Returns:
        str: JSON string with created task

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate user_id
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError("INVALID_USER_ID: user_id must be a valid UUID")

    # Validate title
    if not title or not title.strip():
        raise ValueError("INVALID_TITLE: title cannot be empty")

    title = title.strip()
    if len(title) > 500:
        raise ValueError("INVALID_TITLE: title cannot exceed 500 characters")

    # Validate priority
    valid_priorities = ["low", "medium", "high"]
    if priority and priority not in valid_priorities:
        raise ValueError(f"INVALID_PRIORITY: priority must be one of {valid_priorities}")

    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("INVALID_DUE_DATE: due_date must be ISO format (e.g., 2025-01-25T10:30:00)")

    # Create task
    task = Task(
        id=uuid4(),
        user_id=user_uuid,
        title=title,
        completed=False,
        priority=priority or "medium",
        due_date=parsed_due_date,
        tags=tags,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return json.dumps({
            "task_id": str(task.id),
            "status": "created",
            "title": task.title,
            "completed": task.completed,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags,
            "created_at": task.created_at.isoformat()
        })

    except Exception as e:
        await session.rollback()
        raise ValueError(f"DATABASE_ERROR: {str(e)}")


# Tool schema for MCP server registration
TOOL_SCHEMA = {
    "description": "Create a new todo task for a user. Accepts a task title and creates an uncompleted task.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "title": {
                "type": "string",
                "description": "The task title/description (1-500 characters)"
            },
            "priority": {
                "type": "string",
                "description": "Task priority (low, medium, high) - defaults to medium",
                "enum": ["low", "medium", "high"]
            },
            "due_date": {
                "type": "string",
                "description": "Optional due date in ISO format (e.g., 2025-01-25T10:30:00)"
            },
            "tags": {
                "type": "string",
                "description": "Optional comma-separated tags (e.g., 'work,urgent')"
            }
        },
        "required": ["user_id", "title"]
    }
}
