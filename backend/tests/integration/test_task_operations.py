"""
Integration tests for complete task operations user journey.

Tests the full user workflow:
1. Create task → 2. List tasks → 3. Complete task → 4. Delete task
Verifies data persistence and correct sequencing of operations.

Constitution Compliance:
- Principle I (Stateless): Tests stateless operations through MCP tools
- Principle II (MCP-First): Tests only through MCP server interface
- Principle IV (Test-First): Written first, expected to fail until implementation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
import json
from typing import Dict, Any

# Import the actual MCP server implementation (will fail until implemented)
try:
    from src.mcp.server import call_tool
except ImportError:
    # This will cause tests to fail until implementation exists
    call_tool = None


class TestTaskOperationsUserJourney:
    """Integration tests for complete task operations user journey"""

    @pytest.fixture
    def test_user_id(self):
        """Generate test user ID"""
        return str(uuid4())

    @pytest.fixture
    def timestamp(self):
        """Generate test timestamp"""
        return datetime.now(timezone.utc).isoformat()

    @pytest.mark.asyncio
    async def test_complete_user_journey_single_task(self, test_user_id, timestamp):
        """Test complete user journey with single task"""
        # This test should FAIL until MCP tools are implemented

        # Step 1: Create task
        if call_tool is None:
            pytest.fail("MCP server not implemented yet")

        result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": "Buy groceries"
        })

        # Verify task creation
        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"
        assert result["completed"] is False
        assert "task_id" in result

        task_id = result["task_id"]

        # Step 2: List tasks to verify persistence
        list_result = await call_tool("list_tasks", {"user_id": test_user_id})

        # Verify list response
        assert list_result["count"] == 1
        assert len(list_result["tasks"]) == 1

        # Verify task data matches creation
        listed_task = list_result["tasks"][0]
        assert listed_task["id"] == task_id
        assert listed_task["title"] == "Buy groceries"
        assert listed_task["completed"] is False

        # Step 3: Complete task
        complete_result = await call_tool("complete_task", {
            "user_id": test_user_id,
            "task_id": task_id
        })

        # Verify completion
        assert complete_result["status"] == "completed"
        assert complete_result["task_id"] == task_id
        assert complete_result["completed"] is True

        # Step 4: Verify task is marked as complete in list
        list_after_complete = await call_tool("list_tasks", {"user_id": test_user_id})

        assert list_after_complete["count"] == 1
        listed_after = list_after_complete["tasks"][0]
        assert listed_after["id"] == task_id
        assert listed_after["completed"] is True

        # Step 5: Delete task
        delete_result = await call_tool("delete_task", {
            "user_id": test_user_id,
            "task_id": task_id
        })

        # Verify deletion
        assert delete_result["status"] == "deleted"
        assert delete_result["task_id"] == task_id

        # Step 6: Verify task is gone
        list_after_delete = await call_tool("list_tasks", {"user_id": test_user_id})

        assert list_after_delete["count"] == 0
        assert len(list_after_delete["tasks"]) == 0

    @pytest.mark.asyncio
    async def test_complete_user_journey_multiple_tasks(self, test_user_id, timestamp):
        """Test complete user journey with multiple tasks"""
        if call_tool is None:
            pytest.fail("MCP server not implemented yet")

        # Create multiple tasks
        task1_result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": "Buy groceries"
        })
        task2_result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": "Call dentist"
        })
        task3_result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": "Finish report"
        })

        task1_id = task1_result["task_id"]
        task2_id = task2_result["task_id"]
        task3_id = task3_result["task_id"]

        # Verify all tasks created
        list_result = await call_tool("list_tasks", {"user_id": test_user_id})
        assert list_result["count"] == 3

        # Complete one task
        await call_tool("complete_task", {
            "user_id": test_user_id,
            "task_id": task1_id
        })

        # Verify only task1 is completed
        list_after_complete = await call_tool("list_tasks", {"user_id": test_user_id})
        assert list_after_complete["count"] == 3

        completed_tasks = [t for t in list_after_complete["tasks"] if t["completed"]]
        incomplete_tasks = [t for t in list_after_complete["tasks"] if not t["completed"]]

        assert len(completed_tasks) == 1
        assert len(incomplete_tasks) == 2

        # Delete completed task
        await call_tool("delete_task", {
            "user_id": test_user_id,
            "task_id": task1_id
        })

        # Verify deletion
        final_list = await call_tool("list_tasks", {"user_id": test_user_id})
        assert final_list["count"] == 2

        # Verify remaining tasks are still incomplete
        for task in final_list["tasks"]:
            assert not task["completed"]
            assert task["id"] in [task2_id, task3_id]

    @pytest.mark.asyncio
    async def test_data_persistence_between_operations(self, test_user_id, timestamp):
        """Test data persistence across multiple operations"""
        if call_tool is None:
            pytest.fail("MCP server not implemented yet")

        # Create task
        create_result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": "Test persistence"
        })
        task_id = create_result["task_id"]

        # Verify data persists through multiple list operations
        list1 = await call_tool("list_tasks", {"user_id": test_user_id})
        list2 = await call_tool("list_tasks", {"user_id": test_user_id})
        list3 = await call_tool("list_tasks", {"user_id": test_user_id})

        # All lists should show the same task
        for lst in [list1, list2, list3]:
            assert lst["count"] == 1
            assert lst["tasks"][0]["id"] == task_id
            assert lst["tasks"][0]["title"] == "Test persistence"

        # Complete task and verify persistence
        await call_tool("complete_task", {
            "user_id": test_user_id,
            "task_id": task_id
        })

        list_after_complete = await call_tool("list_tasks", {"user_id": test_user_id})
        assert list_after_complete["count"] == 1
        assert list_after_complete["tasks"][0]["completed"] is True

        # Delete and verify persistence
        await call_tool("delete_task", {
            "user_id": test_user_id,
            "task_id": task_id
        })

        list_after_delete = await call_tool("list_tasks", {"user_id": test_user_id})
        assert list_after_delete["count"] == 0

    @pytest.mark.asyncio
    async def test_error_handling_for_nonexistent_task(self, test_user_id):
        """Test error handling for operations on non-existent tasks"""
        if call_tool is None:
            pytest.fail("MCP server not implemented yet")

        # Try to complete non-existent task
        result = await call_tool("complete_task", {
            "user_id": test_user_id,
            "task_id": "non-existent-id"
        })

        assert result["error"] == "Task not found"
        assert result["code"] == "TASK_NOT_FOUND"

        # Try to delete non-existent task
        result = await call_tool("delete_task", {
            "user_id": test_user_id,
            "task_id": "non-existent-id"
        })

        assert result["error"] == "Task not found"
        assert result["code"] == "TASK_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_user_isolation(self, test_user_id):
        """Test that tasks are isolated between users"""
        if call_tool is None:
            pytest.fail("MCP server not implemented yet")

        user1_id = str(uuid4())
        user2_id = str(uuid4())

        # User1 creates a task
        user1_task = await call_tool("add_task", {
            "user_id": user1_id,
            "title": "User1 task"
        })
        user1_task_id = user1_task["task_id"]

        # User2 creates a different task
        user2_task = await call_tool("add_task", {
            "user_id": user2_id,
            "title": "User2 task"
        })
        user2_task_id = user2_task["task_id"]

        # User1 should only see their own task
        user1_tasks = await call_tool("list_tasks", {"user_id": user1_id})
        assert user1_tasks["count"] == 1
        assert user1_tasks["tasks"][0]["id"] == user1_task_id
        assert user1_tasks["tasks"][0]["title"] == "User1 task"

        # User2 should only see their own task
        user2_tasks = await call_tool("list_tasks", {"user_id": user2_id})
        assert user2_tasks["count"] == 1
        assert user2_tasks["tasks"][0]["id"] == user2_task_id
        assert user2_tasks["tasks"][0]["title"] == "User2 task"

        # User1 cannot complete user2's task
        result = await call_tool("complete_task", {
            "user_id": user1_id,
            "task_id": user2_task_id
        })
        assert result["error"] == "Access denied"
        assert result["code"] == "ACCESS_DENIED"

        # Verify user2's task is still incomplete
        user2_tasks_after = await call_tool("list_tasks", {"user_id": user2_id})
        assert not user2_tasks_after["tasks"][0]["completed"]

    @pytest.mark.asyncio
    async def test_input_validation(self, test_user_id):
        """Test input validation for all MCP tools"""
        if call_tool is None:
            pytest.fail("MCP server not implemented yet")

        # Test add_task validation
        # Empty title
        result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": ""
        })
        assert result["error"] == "INVALID_TITLE"
        assert result["code"] == "INVALID_TITLE"

        # Long title
        long_title = "x" * 501
        result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": long_title
        })
        assert result["error"] == "INVALID_TITLE"
        assert result["code"] == "INVALID_TITLE"

        # Invalid user_id
        result = await call_tool("add_task", {
            "user_id": "invalid-uuid",
            "title": "Test task"
        })
        assert result["error"] == "INVALID_USER_ID"
        assert result["code"] == "INVALID_USER_ID"

        # Missing required parameters
        result = await call_tool("add_task", {})
        assert "error" in result
        assert "required" in result["error"].lower()

        # Test list_tasks validation
        result = await call_tool("list_tasks", {})
        assert "error" in result
        assert "required" in result["error"].lower()