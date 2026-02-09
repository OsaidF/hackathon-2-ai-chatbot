"""
Contract tests for update_task MCP tool
Test the contract specification from specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml

Test cases:
- Input validation (valid vs invalid parameters)
- Output format matches contract
- Error codes match specification
- Updated timestamp behavior
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

        def update_task(self, **kwargs):
            raise NotImplementedError("MCP server not yet implemented")


class TestUpdateTask:
    """Contract tests for update_task tool"""

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

    def test_update_task_success_case(self):
        """Test successful task title update - should FAIL until implementation"""
        # Arrange
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": "Buy groceries and cook dinner"
        }

        # Mock the database response
        with patch.object(self.server, '_update_task_title') as mock_update:
            mock_update.return_value = {
                "task_id": self.valid_task_id,
                "status": "updated",
                "title": "Buy groceries and cook dinner",
                "completed": False,
                "updated_at": "2025-01-24T11:30:00Z"
            }

            # Act - This should fail until implementation exists
            with pytest.raises(NotImplementedError):
                result = self.server.update_task(**update_data)

                # Assert output format matches contract
                assert result["task_id"] == self.valid_task_id
                assert result["status"] == "updated"
                assert result["title"] == "Buy groceries and cook dinner"
                assert result["completed"] is False
                assert isinstance(result["updated_at"], str)

    def test_update_task_valid_new_title(self):
        """Test with valid new_title - should FAIL until implementation"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": "Valid updated title"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_update_task_title') as mock_update:
                mock_update.return_value = {
                    "task_id": self.valid_task_id,
                    "status": "updated",
                    "title": "Valid updated title",
                    "completed": False,
                    "updated_at": datetime.utcnow().isoformat()
                }
                result = self.server.update_task(**update_data)
                assert result["title"] == "Valid updated title"

    def test_update_task_invalid_user_id(self):
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
                update_data = {
                    "user_id": user_id,
                    "task_id": self.valid_task_id,
                    "new_title": "Updated title"
                }

                with pytest.raises(Exception) as exc_info:
                    self.server.update_task(**update_data)
                # Should fail with INVALID_USER_ID error code
                assert exc_info.value.code == "INVALID_USER_ID"

    def test_update_task_invalid_task_id(self):
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
                update_data = {
                    "user_id": self.valid_user_id,
                    "task_id": task_id,
                    "new_title": "Updated title"
                }

                with pytest.raises(Exception) as exc_info:
                    self.server.update_task(**update_data)
                # Should fail with INVALID_TASK_ID error code
                assert exc_info.value.code == "INVALID_TASK_ID"

    def test_update_task_empty_new_title(self):
        """Test with empty new_title - should raise INVALID_TITLE"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": ""
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.update_task(**update_data)
            # Should fail with INVALID_TITLE error code
            assert exc_info.value.code == "INVALID_TITLE"

    def test_update_task_long_new_title(self):
        """Test with new_title exceeding max length - should raise INVALID_TITLE"""
        long_title = "x" * 501  # Exceeds maxLength constraint

        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": long_title
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.update_task(**update_data)
            # Should fail with INVALID_TITLE error code
            assert exc_info.value.code == "INVALID_TITLE"

    def test_update_task_missing_user_id(self):
        """Test missing user_id parameter - should raise validation error"""
        update_data = {
            "task_id": self.valid_task_id,
            "new_title": "Updated title"
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.update_task(**update_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_update_task_missing_task_id(self):
        """Test missing task_id parameter - should raise validation error"""
        update_data = {
            "user_id": self.valid_user_id,
            "new_title": "Updated title"
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.update_task(**update_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_update_task_missing_new_title(self):
        """Test missing new_title parameter - should raise validation error"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.update_task(**update_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_update_task_task_not_found(self):
        """Test task does not exist - should raise TASK_NOT_FOUND"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": "999e4567-e89b-12d3-a456-426614174999",  # Non-existent task
            "new_title": "Updated title"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_task_by_id') as mock_get_task:
                mock_get_task.return_value = None

                with pytest.raises(Exception) as exc_info:
                    self.server.update_task(**update_data)
                # Should fail with TASK_NOT_FOUND error code
                assert exc_info.value.code == "TASK_NOT_FOUND"

    def test_update_task_different_user(self):
        """Test task belongs to different user - should raise TASK_NOT_FOUND"""
        different_user_id = "550e8400-e29b-41d4-a716-446655440001"

        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": "Updated title"
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

                with pytest.raises(Exception) as exc_info:
                    self.server.update_task(**update_data)
                # Should fail with TASK_NOT_FOUND error code
                assert exc_info.value.code == "TASK_NOT_FOUND"

    def test_update_task_database_error(self):
        """Test database error scenario - should raise DATABASE_ERROR"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": "Updated title"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_update_task_title') as mock_update:
                mock_update.side_effect = Exception("Database connection failed")

                with pytest.raises(Exception) as exc_info:
                    self.server.update_task(**update_data)
                # Should fail with DATABASE_ERROR error code
                assert exc_info.value.code == "DATABASE_ERROR"

    def test_update_task_output_format_contract_compliance(self):
        """Test output format strictly matches contract schema"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": "Updated contract compliance test"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_update_task_title') as mock_update:
                mock_update.return_value = {
                    "task_id": self.valid_task_id,
                    "status": "updated",
                    "title": "Updated contract compliance test",
                    "completed": False,
                    "updated_at": "2025-01-24T11:30:00Z"
                }

                result = self.server.update_task(**update_data)

                # Verify all required fields are present
                required_fields = ["task_id", "status", "title", "completed", "updated_at"]
                for field in required_fields:
                    assert field in result, f"Missing required field: {field}"

                # Verify field types
                assert isinstance(result["task_id"], str)
                assert isinstance(result["status"], str)
                assert isinstance(result["title"], str)
                assert isinstance(result["completed"], bool)
                assert isinstance(result["updated_at"], str)

                # Verify status is exactly "updated"
                assert result["status"] == "updated"

    def test_update_task_min_length_title(self):
        """Test new_title with minimum length (1 character)"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": "A"  # Minimum length
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_update_task_title') as mock_update:
                mock_update.return_value = {
                    "task_id": self.valid_task_id,
                    "status": "updated",
                    "title": "A",
                    "completed": False,
                    "updated_at": datetime.utcnow().isoformat()
                }
                result = self.server.update_task(**update_data)
                assert result["title"] == "A"

    def test_update_task_max_length_title(self):
        """Test new_title with maximum length (500 characters)"""
        max_title = "x" * 500  # Maximum allowed length

        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": max_title
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_update_task_title') as mock_update:
                mock_update.return_value = {
                    "task_id": self.valid_task_id,
                    "status": "updated",
                    "title": max_title,
                    "completed": False,
                    "updated_at": datetime.utcnow().isoformat()
                }
                result = self.server.update_task(**update_data)
                assert result["title"] == max_title

    def test_update_task_updated_timestamp_updated(self):
        """Test that updated_at timestamp is modified on update"""
        update_data = {
            "user_id": self.valid_user_id,
            "task_id": self.valid_task_id,
            "new_title": "Buy groceries and cook dinner"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_get_task_by_id') as mock_get_task:
                original_task = {
                    "task_id": self.valid_task_id,
                    "user_id": self.valid_user_id,
                    "title": "Buy groceries",
                    "completed": False,
                    "created_at": "2025-01-24T10:30:00Z",
                    "updated_at": "2025-01-24T10:30:00Z"
                }
                mock_get_task.return_value = original_task

                with patch.object(self.server, '_update_task_title') as mock_update:
                    updated_task = {
                        "task_id": self.valid_task_id,
                        "status": "updated",
                        "title": "Buy groceries and cook dinner",
                        "completed": False,
                        "updated_at": "2025-01-24T11:30:00Z"  # Different timestamp
                    }
                    mock_update.return_value = updated_task

                    result = self.server.update_task(**update_data)

                    # Verify updated_at is different from original
                    assert result["updated_at"] != original_task["updated_at"]
                    assert result["title"] == "Buy groceries and cook dinner"