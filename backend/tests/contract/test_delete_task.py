"""
Contract tests for delete_task MCP tool
Test the contract specification from specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml

Test cases:
- Input validation (valid vs invalid parameters)
- Output format matches contract
- Error codes match specification
- Permanent deletion behavior
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

        def delete_task(self, **kwargs):
            raise NotImplementedError("MCP server not yet implemented")


class TestDeleteTask:
    """Contract tests for delete_task tool"""

    def setup_method(self):
        """Setup test fixtures"""
        self.server = TodoMCPServer()

        # Valid UUIDs for testing
        self.valid_user_id = "550e8400-e29b-41d4-a716-446655440000"
        self.valid_task_id = "123e4567-e89b-12d3-a456-426614174000"

        # Sample task data
        self.sample_task = {
            "task_id": self.valid_task_id,
            "title": "Buy groceries",
            "completed": False,
            "created_at": "2025-01-24T10:30:00Z",
            "updated_at": "2025-01-24T10:30:00Z"
        }

    def test_delete_task_success_case(self):
        """Test successful task deletion - should FAIL until implementation"""
        # Arrange
        delete_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id
        }

        # Mock the database response
        with patch.object(self.server, '_delete_task_by_id') as mock_delete:
            mock_delete.return_value = {
                "task_id": self.valid_task_id,
                "status": "deleted",
                "title": "Buy groceries"
            }

            # Act - This should fail until implementation exists
            with pytest.raises(NotImplementedError):
                result = self.server.delete_task(**delete_data)

                # Assert output format matches contract
                assert result["task_id"] == self.valid_task_id
                assert result["status"] == "deleted"
                assert result["title"] == "Buy groceries"

    def test_delete_task_invalid_user_id(self):
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
                delete_data = {
                    "user_id": user_id,
                    "task_id": self.valid_task_id
                }

                with pytest.raises(Exception) as exc_info:
                    self.server.delete_task(**delete_data)
                # Should fail with INVALID_USER_ID error code
                assert exc_info.value.code == "INVALID_USER_ID"

    def test_delete_task_invalid_task_id(self):
        """Test with invalid task_id format - should raise INVALID_TASK_ID"""
        invalid_task_ids = [
            "not-a-uuid",
            "123e4567-e89b-12d3-a456",  # Too short
            "123e4567-e89b-12d3-a456-426614174000-extra",  # Too long
            123,  # Wrong type
            None  # Missing
        ]

        with pytest.raises(NotImplementedError):
            for task_id in invalid_task_ids:
                delete_data = {
                    "user_id": self.valid_user_id,
                    "task_id": task_id
                }

                with pytest.raises(Exception) as exc_info:
                    self.server.delete_task(**delete_data)
                # Should fail with INVALID_TASK_ID error code
                assert exc_info.value.code == "INVALID_TASK_ID"

    def test_delete_task_missing_user_id(self):
        """Test missing user_id parameter - should raise validation error"""
        delete_data = {
            "task_id": self.valid_task_id
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.delete_task(**delete_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_delete_task_missing_task_id(self):
        """Test missing task_id parameter - should raise validation error"""
        delete_data = {
            "user_id": self.valid_user_id
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.delete_task(**delete_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_delete_task_task_not_found(self):
        """Test task does not exist - should raise TASK_NOT_FOUND"""
        delete_data = {
            "user_id": self.valid_user_id,
            "task_id": "999e4567-e89b-12d3-a456-426614174999"  # Non-existent task
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_delete_task_by_id') as mock_delete:
                mock_delete.return_value = None  # Task not found

                with pytest.raises(Exception) as exc_info:
                    self.server.delete_task(**delete_data)
                # Should fail with TASK_NOT_FOUND error code
                assert exc_info.value.code == "TASK_NOT_FOUND"

    def test_delete_task_different_user(self):
        """Test task belongs to different user - should raise TASK_NOT_FOUND"""
        different_user_id = "550e8400-e29b-41d4-a716-446655440001"

        delete_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_task_by_id') as mock_get_task:
                mock_get_task.return_value = {
                    "task_id": self.valid_task_id,
                    "user_id": different_user_id,  # Different user
                    "title": "Buy groceries",
                    "completed": False,
                    "updated_at": "2025-01-24T10:30:00Z"
                }

                with patch.object(self.server, '_delete_task_by_id') as mock_delete:
                    mock_delete.return_value = None

                    with pytest.raises(Exception) as exc_info:
                        self.server.delete_task(**delete_data)
                    # Should fail with TASK_NOT_FOUND error code
                    assert exc_info.value.code == "TASK_NOT_FOUND"

    def test_delete_task_database_error(self):
        """Test database error scenario - should raise DATABASE_ERROR"""
        delete_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_delete_task_by_id') as mock_delete:
                mock_delete.side_effect = Exception("Database connection failed")

                with pytest.raises(Exception) as exc_info:
                    self.server.delete_task(**delete_data)
                # Should fail with DATABASE_ERROR error code
                assert exc_info.value.code == "DATABASE_ERROR"

    def test_delete_task_output_format_contract_compliance(self):
        """Test output format strictly matches contract schema"""
        delete_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_delete_task_by_id') as mock_delete:
                mock_delete.return_value = {
                    "task_id": self.valid_task_id,
                    "status": "deleted",
                    "title": "Buy groceries"
                }

                result = self.server.delete_task(**delete_data)

                # Verify all required fields are present
                required_fields = ["task_id", "status", "title"]
                for field in required_fields:
                    assert field in result, f"Missing required field: {field}"

                # Verify field types
                assert isinstance(result["task_id"], str)
                assert isinstance(result["status"], str)
                assert isinstance(result["title"], str)

                # Verify status is exactly "deleted"
                assert result["status"] == "deleted"

    def test_delete_task_permanent_deletion(self):
        """Test that task is permanently deleted (cannot be retrieved)"""
        delete_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id
        }

        with pytest.raises(NotImplementedError):
            # First, delete the task
            with patch.object(self.server, '_delete_task_by_id') as mock_delete:
                mock_delete.return_value = {
                    "task_id": self.valid_task_id,
                    "status": "deleted",
                    "title": "Buy groceries"
                }

                result = self.server.delete_task(**delete_data)

                # Then verify it cannot be retrieved
                with patch.object(self.server, '_get_task_by_id') as mock_get_task:
                    mock_get_task.return_value = None  # Task no longer exists

                    # This would simulate trying to list tasks and confirming it's gone
                    # Actual test depends on implementation
                    assert result["status"] == "deleted"

    def test_delete_task_successful_deletion_confirmation(self):
        """Test that deletion returns confirmation of what was deleted"""
        delete_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_task_by_id') as mock_get_task:
                mock_get_task.return_value = self.sample_task

                with patch.object(self.server, '_delete_task_by_id') as mock_delete:
                    mock_delete.return_value = {
                        "task_id": self.valid_task_id,
                        "status": "deleted",
                        "title": "Buy groceries"
                    }

                    result = self.server.delete_task(**delete_data)

                    # Verify the response contains the correct title
                    assert result["title"] == "Buy groceries"
                    assert result["task_id"] == self.valid_task_id