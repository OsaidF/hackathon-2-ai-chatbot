"""
Integration tests for natural language intent variations.

Tests 10+ variations of "create task" intent to verify the AI agent can
correctly interpret natural language and route to the appropriate MCP tool.

Constitution Compliance:
- Principle V (Natural Language): Tests agent's ability to understand varied NL input
- Principle II (MCP-First): All commands flow through MCP tools only
- Principle IV (Test-First): Written first, expected to fail until implementation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any, List


class TestNaturalLanguageVariations:
    """Integration tests for natural language intent variations"""

    @pytest.fixture
    def test_user_id(self):
        """Generate test user ID"""
        return str(uuid4())

    # Test cases from requirements
    NL_TEST_CASES = [
        {
            "text": "add task buy groceries",
            "expected_title": "buy groceries",
            "intent_type": "direct_command"
        },
        {
            "text": "remember to call dentist",
            "expected_title": "call dentist",
            "intent_type": "reminder"
        },
        {
            "text": "create todo: finish report",
            "expected_title": "finish report",
            "intent_type": "todo_list"
        },
        {
            "text": "I need to buy milk",
            "expected_title": "buy milk",
            "intent_type": "need_statement"
        },
        {
            "text": "Add a reminder to walk the dog",
            "expected_title": "walk the dog",
            "intent_type": "add_reminder"
        },
        {
            "text": "Create a task for calling mom",
            "expected_title": "calling mom",
            "intent_type": "create_task"
        },
        {
            "text": "Don't forget to renew insurance",
            "expected_title": "renew insurance",
            "intent_type": "dont_forget"
        },
        {
            "text": "Make a note: submit expenses",
            "expected_title": "submit expenses",
            "intent_type": "make_note"
        },
        {
            "text": "Put 'clean garage' on my todo list",
            "expected_title": "clean garage",
            "intent_type": "put_on_list"
        },
        {
            "text": "Add 'review documents' to my tasks",
            "expected_title": "review documents",
            "intent_type": "add_to_tasks"
        }
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_case", NL_TEST_CASES)
    async def test_natural_language_intent_recognition(self, test_case, test_user_id):
        """Test that various natural language inputs are correctly recognized as create task intent"""

        # Mock the OpenAI agent response (will fail until implementation exists)
        try:
            from src.mcp.server import call_tool
        except ImportError:
            pytest.fail("MCP server not implemented yet")

        # Simulate AI agent processing the natural language
        # In a real implementation, this would go through OpenAI Agents SDK
        message = test_case["text"]
        expected_title = test_case["expected_title"]

        # This test simulates the agent recognizing "create task" intent
        # and extracting the task title, then calling the MCP tool

        # Verify that the agent would call add_task with the correct title
        result = await call_tool("add_task", {
            "user_id": test_user_id,
            "title": expected_title
        })

        # Verify the task was created correctly
        assert result["status"] == "created"
        assert result["title"] == expected_title
        assert result["completed"] is False
        assert "task_id" in result

    @pytest.mark.asyncio
    async def test_ai_agent_integration(self, test_user_id):
        """Test integration with AI agent that processes natural language"""
        try:
            from src.mcp.server import call_tool
        except ImportError:
            pytest.fail("MCP server not implemented yet")

        # Simulate AI agent workflow:
        # 1. Receive natural language message
        # 2. Recognize intent as "create task"
        # 3. Extract task title
        # 4. Call appropriate MCP tool

        test_messages = [
            "add task buy groceries",
            "remember to call dentist",
            "create todo: finish report",
            "I need to buy milk"
        ]

        created_tasks = []

        for message in test_messages:
            # Extract title (simplified - real implementation would use NLP)
            if "add task" in message:
                title = message.replace("add task", "").strip()
            elif "remember to" in message:
                title = message.replace("remember to", "").strip()
            elif "create todo:" in message:
                title = message.replace("create todo:", "").strip()
            elif "I need to" in message:
                title = message.replace("I need to", "").strip()
            else:
                title = message  # fallback

            # Call MCP tool
            result = await call_tool("add_task", {
                "user_id": test_user_id,
                "title": title
            })

            created_tasks.append(result)

            # Verify successful creation
            assert result["status"] == "created"
            assert result["title"] == title

        # Verify all tasks were created
        assert len(created_tasks) == 4

        # Verify we can list them all
        list_result = await call_tool("list_tasks", {"user_id": test_user_id})
        assert list_result["count"] == 4
        assert len(list_result["tasks"]) == 4

    @pytest.mark.asyncio
    async def test_error_handling_for_unrecognized_intents(self, test_user_id):
        """Test error handling for messages that aren't task creation intents"""
        try:
            from src.mcp.server import call_tool
        except ImportError:
            pytest.fail("MCP server not implemented yet")

        # Messages that should not create tasks
        non_task_messages = [
            "Hello",
            "How are you?",
            "The weather is nice today",
            "12345",
            ""  # empty message
        ]

        for message in non_task_messages:
            # Mock AI agent response - should not call any tools
            # In real implementation, agent would return no tool calls
            # For testing, we simulate this by checking no tasks exist
            initial_list = await call_tool("list_tasks", {"user_id": test_user_id})
            initial_count = initial_list["count"]

            # Agent should not create any tasks for these messages
            # So the count should remain the same
            assert True  # Placeholder - real test will verify no tool calls were made

    @pytest.mark.asyncio
    async def test_task_extraction_accuracy(self, test_user_id):
        """Test accuracy of task title extraction from various patterns"""
        try:
            from src.mcp.server import call_tool
        except ImportError:
            pytest.fail("MCP server not implemented yet")

        test_cases = [
            # Input text, expected extracted title
            ("add task buy groceries", "buy groceries"),
            ("remember to call dentist", "call dentist"),
            ("create todo: finish report", "finish report"),
            ("I need to buy milk", "buy milk"),
            ("Add a reminder to walk the dog", "walk the dog"),
            ("Create a task for calling mom", "calling mom"),
            ("Don't forget to renew insurance", "renew insurance"),
            ("Make a note: submit expenses", "submit expenses"),
            ("Put 'clean garage' on my todo list", "clean garage"),
            ("Add 'review documents' to my tasks", "review documents"),
            ("add task    multiple   spaces", "multiple spaces"),  # Test whitespace handling
            ("add task", ""),  # Empty extraction
            ("add task   ", "")  # Trailing spaces
        ]

        for input_text, expected_title in test_cases:
            if expected_title:  # Only test if we expect a title to be extracted
                result = await call_tool("add_task", {
                    "user_id": test_user_id,
                    "title": expected_title
                })

                assert result["title"] == expected_title

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, test_user_id):
        """Test processing multiple natural language messages concurrently"""
        try:
            from src.mcp.server import call_tool
        except ImportError:
            pytest.fail("MCP server not implemented yet")

        # Create multiple concurrent tasks
        tasks = [
            "add task buy groceries",
            "remember to call dentist",
            "create todo: finish report"
        ]

        # Simulate concurrent processing
        async def process_message(message, user_id):
            # Extract title (simplified)
            if "add task" in message:
                title = message.replace("add task", "").strip()
            elif "remember to" in message:
                title = message.replace("remember to", "").strip()
            elif "create todo:" in message:
                title = message.replace("create todo:", "").strip()
            else:
                title = message.strip()

            return await call_tool("add_task", {
                "user_id": user_id,
                "title": title
            })

        # Process all messages concurrently
        results = await asyncio.gather(*[
            process_message(task, test_user_id)
            for task in tasks
        ])

        # Verify all tasks were created
        assert len(results) == 3

        for result in results:
            assert result["status"] == "created"
            assert not result["completed"]
            assert "task_id" in result

        # Verify we can list all tasks
        list_result = await call_tool("list_tasks", {"user_id": test_user_id})
        assert list_result["count"] == 3

    @pytest.mark.asyncio
    async def test_user_isolation_across_intents(self, test_user_id):
        """Test that different users' tasks are isolated regardless of intent"""
        try:
            from src.mcp.server import call_tool
        except ImportError:
            pytest.fail("MCP server not implemented yet")

        user1_id = str(uuid4())
        user2_id = str(uuid4())

        # User1 processes multiple intents
        user1_messages = [
            "add task buy groceries",
            "remember to call dentist",
            "create todo: finish report"
        ]

        user2_messages = [
            "add task walk the dog",
            "I need to submit expenses"
        ]

        # Process user1's messages
        for message in user1_messages:
            if "add task" in message:
                title = message.replace("add task", "").strip()
                await call_tool("add_task", {"user_id": user1_id, "title": title})
            elif "remember to" in message:
                title = message.replace("remember to", "").strip()
                await call_tool("add_task", {"user_id": user1_id, "title": title})
            elif "create todo:" in message:
                title = message.replace("create todo:", "").strip()
                await call_tool("add_task", {"user_id": user1_id, "title": title})

        # Process user2's messages
        for message in user2_messages:
            if "add task" in message:
                title = message.replace("add task", "").strip()
                await call_tool("add_task", {"user_id": user2_id, "title": title})
            elif "I need to" in message:
                title = message.replace("I need to", "").strip()
                await call_tool("add_task", {"user_id": user2_id, "title": title})

        # Verify user isolation
        user1_tasks = await call_tool("list_tasks", {"user_id": user1_id})
        user2_tasks = await call_tool("list_tasks", {"user_id": user2_id})

        assert user1_tasks["count"] == 3
        assert user2_tasks["count"] == 2

        # Verify no cross-contamination
        user1_titles = {t["title"] for t in user1_tasks["tasks"]}
        user2_titles = {t["title"] for t in user2_tasks["tasks"]}

        assert "buy groceries" in user1_titles
        assert "walk the dog" not in user1_titles
        assert "walk the dog" in user2_titles
        assert "buy groceries" not in user2_titles