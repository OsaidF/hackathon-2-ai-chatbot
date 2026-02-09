"""
Task model for Todo AI Chatbot.

Represents a single todo item managed by users through natural language commands.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, DateTime, Boolean, Text
from uuid import UUID, uuid4
from sqlalchemy import func


class Task(SQLModel, table=True):
    """
    Task entity representing a single todo item.

    Attributes:
        id: Unique task identifier (UUID)
        user_id: Owner of this task (foreign key to User)
        title: Task description (what the user needs to do)
        completed: Task completion status
        created_at: When task was created
        updated_at: When task was last modified

    State Transitions:
        Created (completed=False) → Completed (completed=True)

    Multi-Tenancy:
        All queries MUST filter by user_id
        Users can only access their own tasks
        No cross-user task visibility

    Constitution Compliance:
        - Stateless: Task state persisted to database only
        - MCP Tools: All task operations through MCP tools only
        - Database as Single Source of Truth: No in-memory task storage
    """

    __tablename__ = "todo_tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique task identifier"
    )

    user_id: UUID = Field(
        foreign_key="todo_users.id",
        index=True,
        description="Owner of this task (references User.id)"
    )

    title: str = Field(
        max_length=500,
        description="Task description (what the user needs to do)"
    )

    completed: bool = Field(
        default=False,
        index=True,
        description="Task completion status"
    )

    priority: str = Field(
        default="medium",
        max_length=20,
        index=True,
        description="Task priority level (low, medium, high)"
    )

    due_date: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Task due date (optional)"
    )

    tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Task tags/categories (comma-separated)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When task was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": func.now()},
        description="When task was last modified"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "completed": False,
                "priority": "medium",
                "due_date": "2025-01-25T10:30:00Z",
                "tags": "shopping,food",
                "created_at": "2025-01-24T10:30:00Z",
                "updated_at": "2025-01-24T10:30:00Z"
            }
        }


class TaskPublic(SQLModel):
    """Public task information returned to users."""

    id: UUID
    title: str
    completed: bool
    priority: str
    due_date: Optional[datetime]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime


class TaskCreate(SQLModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=500)
    priority: str = Field(default="medium", max_length=20)
    due_date: Optional[datetime] = None
    tags: Optional[str] = None


class TaskUpdate(SQLModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[str] = None


class TaskList(SQLModel):
    """Schema for listing multiple tasks."""

    tasks: list[TaskPublic]
    count: int
