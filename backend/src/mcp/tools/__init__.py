"""
MCP Tools initialization.

This module imports all MCP tools for direct use by the agent.
"""

from .add_task import add_task, add_task as add_task_module
from .list_tasks import list_tasks, list_tasks as list_tasks_module
from .complete_task import complete_task, complete_task as complete_task_module
from .delete_task import delete_task, delete_task as delete_task_module
from .update_task import update_task, update_task as update_task_module


__all__ = [
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
    "add_task_module",
    "list_tasks_module",
    "complete_task_module",
    "delete_task_module",
    "update_task_module",
]
