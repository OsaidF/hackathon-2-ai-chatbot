"""
MCP Tool: delete_task

Permanently removes a task from the database.

Contract:
- Input: user_id (UUID), task_id (UUID)
- Output: {task_id, status: "deleted", title}
- Errors: INVALID_USER_ID, INVALID_TASK_ID, TASK_NOT_FOUND, DATABASE_ERROR
"""

import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


async def delete_task(
    user_id: str,
    task_id: str,
    session: AsyncSession = None
) -> str:
    """
    Permanently delete a task. This operation cannot be undone.

    Args:
        user_id: User identifier (UUID string)
        task_id: Task identifier (UUID string)
        session: Database session

    Returns:
        str: JSON string with deletion confirmation

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

        # Store task info for response
        task_title = task.title

        # Delete task
        await session.delete(task)
        await session.commit()

        return json.dumps({
            "task_id": str(task_uuid),
            "status": "deleted",
            "title": task_title
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
    "description": "Permanently remove a task from the database. This operation cannot be undone.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "task_id": {
                "type": "string",
                "description": "Unique identifier of the task to delete (UUID format)"
            }
        },
        "required": ["user_id", "task_id"]
    }
}
