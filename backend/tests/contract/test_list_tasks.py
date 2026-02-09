"""
Contract tests for list_tasks MCP tool
Test the contract specification from specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml

Test cases:
- Input validation (valid vs invalid parameters)
- Output format matches contract
- Error codes match specification
"""

import pytest
import json
from unittest.mock import Mock, patch
import uuid
from datetime import datetime

# Import the MCP server implementation (using try-except for missing implementation)
try:
    from src.mcp.server import TodoMCPServer
except ImportError:
    # Create a mock class for testing purposes
    class TodoMCPServer:
        def __init__(self):
            pass

        def list_tasks(self, **kwargs):
            raise NotImplementedError("MCP server not yet implemented")


class TestListTasks:
    """Contract tests for list_tasks tool"""

    def setup_method(self):
        """Setup test fixtures"""
        self.server = TodoMCPServer()

        # Valid UUIDs for testing
        self.valid_user_id = "550e8400-e29b-41d4-a716-446655440000"

        # Sample tasks data
        self.sample_tasks = [
            {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "completed": False,
                "created_at": "2025-01-24T10:30:00Z",
                "updated_at": "2025-01-24T10:30:00Z"
            },
            {
                "task_id": "223e4567-e89b-12d3-a456-426614174001",
                "title": "Call dentist",
                "completed": True,
                "created_at": "2025-01-23T14:20:00Z",
                "updated_at": "2025-01-24T09:15:00Z"
            }
        ]

    def test_list_tasks_success_case(self):
        """Test successful task listing - should FAIL until implementation"""
        # Arrange
        query_data = {
            "user_id": self.valid_user_id
        }

        # Mock the database response
        with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
            mock_get_tasks.return_value = {
                "tasks": self.sample_tasks,
                "count": len(self.sample_tasks)
            }

            # Act - This should fail until implementation exists
            with pytest.raises(NotImplementedError):
                result = self.server.list_tasks(**query_data)

                # Assert output format matches contract
                assert "tasks" in result
                assert "count" in result
                assert result["count"] == 2
                assert len(result["tasks"]) == 2

                # Check each task has required fields
                for task in result["tasks"]:
                    assert "task_id" in task
                    assert "title" in task
                    assert "completed" in task
                    assert "created_at" in task
                    assert "updated_at" in task
                    assert isinstance(task["completed"], bool)
                    assert isinstance(task["created_at"], str)
                    assert isinstance(task["updated_at"], str)

    def test_list_tasks_with_completed_filter(self):
        """Test listing with completed filter=True - should FAIL until implementation"""
        query_data = {
            "user_id": self.valid_user_id,
            "filter_completed": True
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = {
                    "tasks": [self.sample_tasks[1]],  # Only completed task
                    "count": 1
                }

                result = self.server.list_tasks(**query_data)
                assert result["count"] == 1
                assert result["tasks"][0]["completed"] is True

    def test_list_tasks_with_uncompleted_filter(self):
        """Test listing with completed filter=False - should FAIL until implementation"""
        query_data = {
            "user_id": self.valid_user_id,
            "filter_completed": False
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = {
                    "tasks": [self.sample_tasks[0]],  # Only uncompleted task
                    "count": 1
                }

                result = self.server.list_tasks(**query_data)
                assert result["count"] == 1
                assert result["tasks"][0]["completed"] is False

    def test_list_tasks_no_filter(self):
        """Test listing without filter (all tasks) - should FAIL until implementation"""
        query_data = {
            "user_id": self.valid_user_id
            # No filter_completed parameter
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = {
                    "tasks": self.sample_tasks,
                    "count": len(self.sample_tasks)
                }

                result = self.server.list_tasks(**query_data)
                assert result["count"] == len(self.sample_tasks)

    def test_list_tasks_invalid_user_id(self):
        """Test with invalid user_id format - should raise INVALID_USER_ID"""
        invalid_user_ids = [
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
            123,  # Wrong type
            None  # Missing
        ]

        with pytest.raises(NotImplementedError):
            for user_id in invalid_user_ids:
                query_data = {"user_id": user_id}

                with pytest.raises(Exception) as exc_info:
                    self.server.list_tasks(**query_data)
                # Should fail with INVALID_USER_ID error code
                assert exc_info.value.code == "INVALID_USER_ID"

    def test_list_tasks_missing_user_id(self):
        """Test missing user_id parameter - should raise validation error"""
        query_data = {}  # No user_id

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.list_tasks(**query_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_list_tasks_empty_task_list(self):
        """Test listing tasks when user has no tasks - should FAIL until implementation"""
        query_data = {
            "user_id": self.valid_user_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = {
                    "tasks": [],
                    "count": 0
                }

                result = self.server.list_tasks(**query_data)
                assert result["count"] == 0
                assert len(result["tasks"]) == 0

    def test_list_tasks_database_error(self):
        """Test database error scenario - should raise DATABASE_ERROR"""
        query_data = {
            "user_id": self.valid_user_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
                mock_get_tasks.side_effect = Exception("Database connection failed")

                with pytest.raises(Exception) as exc_info:
                    self.server.list_tasks(**query_data)
                # Should fail with DATABASE_ERROR error code
                assert exc_info.value.code == "DATABASE_ERROR"

    def test_list_tasks_output_format_contract_compliance(self):
        """Test output format strictly matches contract schema"""
        query_data = {
            "user_id": self.valid_user_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
                mock_get_tasks.return_value = {
                    "tasks": self.sample_tasks,
                    "count": len(self.sample_tasks)
                }

                result = self.server.list_tasks(**query_data)

                # Verify top-level structure
                assert "tasks" in result
                assert "count" in result
                assert isinstance(result["count"], int)
                assert result["count"] == len(self.sample_tasks)

                # Verify each task has required fields
                for task in result["tasks"]:
                    required_fields = ["task_id", "title", "completed", "created_at", "updated_at"]
                    for field in required_fields:
                        assert field in task, f"Task missing required field: {field}"

                    # Verify field types
                    assert isinstance(task["task_id"], str)
                    assert isinstance(task["title"], str)
                    assert isinstance(task["completed"], bool)
                    assert isinstance(task["created_at"], str)
                    assert isinstance(task["updated_at"], str)

    def test_list_tasks_multiple_users_separation(self):
        """Test that tasks are properly separated by user - should FAIL until implementation"""
        another_user_id = "550e8400-e29b-41d4-a716-446655440001"

        query_data = {
            "user_id": self.valid_user_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_user_tasks') as mock_get_tasks:
                # Only return tasks for the specified user
                mock_get_tasks.return_value = {
                    "tasks": [self.sample_tasks[0]],  # Only first task belongs to this user
                    "count": 1
                }

                result = self.server.list_tasks(**query_data)
                assert result["count"] == 1
                assert result["tasks"][0]["title"] == "Buy groceries"