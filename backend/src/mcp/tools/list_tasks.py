"""
MCP Tool: list_tasks

Retrieves all tasks for a specific user, optionally filtered by completion status.

Contract:
- Input: user_id (UUID), filter_completed (optional boolean)
- Output: {tasks: [...], count: integer}
- Errors: INVALID_USER_ID, DATABASE_ERROR
"""

import json
from typing import Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


async def list_tasks(
    user_id: str,
    filter_completed: bool = None,
    session: AsyncSession = None
) -> str:
    """
    List all tasks for a user, optionally filtered by completion status.

    Args:
        user_id: User identifier (UUID string)
        filter_completed: Optional filter (True=completed only, False=uncompleted only)
        session: Database session

    Returns:
        str: JSON string with tasks list

    Raises:
        ValueError: If user_id is invalid
    """
    # Validate user_id
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValueError("INVALID_USER_ID: user_id must be a valid UUID")

    try:
        # Build query
        statement = select(Task).where(Task.user_id == user_uuid)

        # Apply filter if specified
        if filter_completed is not None:
            statement = statement.where(Task.completed == filter_completed)

        # Execute query
        result = await session.execute(statement)
        tasks = result.scalars().all()

        # Format output
        tasks_list = [
            {
                "task_id": str(task.id),
                "title": task.title,
                "completed": task.completed,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tags,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]

        return json.dumps({
            "tasks": tasks_list,
            "count": len(tasks_list)
        })

    except Exception as e:
        raise ValueError(f"DATABASE_ERROR: {str(e)}")


# Tool schema for MCP server registration
TOOL_SCHEMA = {
    "description": "Retrieve all tasks for a specific user. Optionally filter by completion status.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "filter_completed": {
                "type": "boolean",
                "description": "Optional filter (True=completed only, False=uncompleted only)"
            }
        },
        "required": ["user_id"]
    }
}
