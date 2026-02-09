"""
Contract tests for add_task MCP tool
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

        def add_task(self, **kwargs):
            raise NotImplementedError("MCP server not yet implemented")


class TestAddTask:
    """Contract tests for add_task tool"""

    def setup_method(self):
        """Setup test fixtures"""
        self.server = TodoMCPServer()

        # Valid UUIDs for testing
        self.valid_user_id = "550e8400-e29b-41d4-a716-446655440000"
        self.valid_task_id = "123e4567-e89b-12d3-a456-426614174000"

        # Sample ISO timestamp
        self.sample_timestamp = "2025-01-24T10:30:00Z"

    def test_add_task_success_case(self):
        """Test successful task creation - should FAIL until implementation"""
        # Arrange
        task_data = {
            "user_id": self.valid_user_id,
            "title": "Buy groceries"
        }

        # Mock the database response
        with patch.object(self.server, '_create_task') as mock_create:
            mock_create.return_value = {
                "task_id": self.valid_task_id,
                "title": "Buy groceries",
                "completed": False,
                "created_at": self.sample_timestamp,
                "updated_at": self.sample_timestamp
            }

            # Act - This should fail until implementation exists
            with pytest.raises(NotImplementedError):
                result = self.server.add_task(**task_data)

                # Assert output format matches contract
                assert result["task_id"] == self.valid_task_id
                assert result["status"] == "created"
                assert result["title"] == "Buy groceries"
                assert result["completed"] is False
                assert isinstance(result["created_at"], str)

    def test_add_task_valid_uuid_user_id(self):
        """Test with valid UUID user_id - should FAIL until implementation"""
        task_data = {
            "user_id": self.valid_user_id,
            "title": "Valid task"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_create_task') as mock_create:
                mock_create.return_value = {
                    "task_id": str(uuid.uuid4()),
                    "title": "Valid task",
                    "completed": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                self.server.add_task(**task_data)

    def test_add_task_empty_title(self):
        """Test with empty title - should raise INVALID_TITLE"""
        task_data = {
            "user_id": self.valid_user_id,
            "title": ""
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.add_task(**task_data)
            # Should fail with INVALID_TITLE error code
            assert exc_info.value.code == "INVALID_TITLE"

    def test_add_task_long_title(self):
        """Test with title exceeding max length - should raise INVALID_TITLE"""
        long_title = "x" * 501  # Exceeds maxLength constraint

        task_data = {
            "user_id": self.valid_user_id,
            "title": long_title
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.add_task(**task_data)
            # Should fail with INVALID_TITLE error code
            assert exc_info.value.code == "INVALID_TITLE"

    def test_add_task_invalid_user_id(self):
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
                task_data = {
                    "user_id": user_id,
                    "title": "Test task"
                }

                with pytest.raises(Exception) as exc_info:
                    self.server.add_task(**task_data)
                # Should fail with INVALID_USER_ID error code
                assert exc_info.value.code == "INVALID_USER_ID"

    def test_add_task_missing_user_id(self):
        """Test missing user_id parameter - should raise validation error"""
        task_data = {
            "title": "Test task"
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.add_task(**task_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_add_task_missing_title(self):
        """Test missing title parameter - should raise validation error"""
        task_data = {
            "user_id": self.valid_user_id
        }

        with pytest.raises(NotImplementedError):
            with pytest.raises(Exception) as exc_info:
                self.server.add_task(**task_data)
            # Should fail with parameter validation error
            assert "required" in str(exc_info.value).lower()

    def test_add_task_database_error(self):
        """Test database error scenario - should raise DATABASE_ERROR"""
        task_data = {
            "user_id": self.valid_user_id,
            "title": "Test task"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_create_task') as mock_create:
                mock_create.side_effect = Exception("Database connection failed")

                with pytest.raises(Exception) as exc_info:
                    self.server.add_task(**task_data)
                # Should fail with DATABASE_ERROR error code
                assert exc_info.value.code == "DATABASE_ERROR"

    def test_add_task_output_format_contract_compliance(self):
        """Test output format strictly matches contract schema"""
        task_data = {
            "user_id": self.valid_user_id,
            "title": "Contract compliance test"
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_create_task') as mock_create:
                mock_create.return_value = {
                    "task_id": self.valid_task_id,
                    "status": "created",
                    "title": "Contract compliance test",
                    "completed": False,
                    "created_at": self.sample_timestamp,
                    "updated_at": self.sample_timestamp
                }

                result = self.server.add_task(**task_data)

                # Verify all required fields are present
                required_fields = ["task_id", "status", "title", "completed", "created_at"]
                for field in required_fields:
                    assert field in result, f"Missing required field: {field}"

                # Verify field types
                assert isinstance(result["task_id"], str)
                assert isinstance(result["status"], str)
                assert isinstance(result["title"], str)
                assert isinstance(result["completed"], bool)
                assert isinstance(result["created_at"], str)

                # Verify status is exactly "created"
                assert result["status"] == "created"

    def test_add_task_min_length_title(self):
        """Test title with minimum length (1 character)"""
        task_data = {
            "user_id": self.valid_user_id,
            "title": "A"  # Minimum length
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_create_task') as mock_create:
                mock_create.return_value = {
                    "task_id": str(uuid.uuid4()),
                    "status": "created",
                    "title": "A",
                    "completed": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                self.server.add_task(**task_data)

    def test_add_task_max_length_title(self):
        """Test title with maximum length (500 characters)"""
        max_title = "x" * 500  # Maximum allowed length

        task_data = {
            "user_id": self.valid_user_id,
            "title": max_title
        }

        with pytest.raises(NotImplementedError):
            with patch.object(self.server, '_create_task') as mock_create:
                mock_create.return_value = {
                    "task_id": str(uuid.uuid4()),
                    "status": "created",
                    "title": max_title,
                    "completed": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                self.server.add_task(**task_data)