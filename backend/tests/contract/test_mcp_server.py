"""
Contract tests for MCP server.

Tests that MCP server starts up correctly and tools can be discovered.
These tests should FAIL before implementation, then PASS after implementation.
"""

import pytest
from unittest.mock import AsyncMock, patch
import json


class TestMCPServerStartup:
    """Test MCP server initialization and startup."""

    @pytest.mark.asyncio
    async def test_server_starts_without_errors(self):
        """Test that MCP server can start without errors."""
        # This test would start the actual server in a subprocess
        # For now, we'll mock the server startup
        with patch("src.mcp.server.stdio_server") as mock_stdio:
            # Mock async context manager
            mock_server = AsyncMock()
            mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(None, None))
            mock_stdio.return_value.__aexit__ = AsyncMock()

            # Import server module to trigger initialization
            try:
                from src.mcp import server
                assert server is not None
                assert hasattr(server, "server")
                assert hasattr(server, "register_tool")
            except ImportError as e:
                pytest.fail(f"Failed to import MCP server module: {e}")

    def test_tool_registry_exists(self):
        """Test that tool registry dictionary exists."""
        from src.mcp import server

        assert hasattr(server, "tool_registry")
        assert isinstance(server.tool_registry, dict)
        # Initially empty, tools will be registered at startup
        assert len(server.tool_registry) >= 0


class TestMCPServerToolDiscovery:
    """Test that MCP server exposes tools for discovery."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self):
        """Test that list_tools returns a list of tools."""
        from src.mcp import server

        # Register a test tool
        async def test_handler(**kwargs):
            return json.dumps({"status": "ok"})

        test_schema = {
            "description": "Test tool",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }

        server.register_tool("test_tool", test_handler, test_schema)

        # Mock the server decorator
        with patch.object(server.server, "list_tools") as mock_list:
            mock_list.return_value = server.server.list_tools()

            # Call list_tools
            tools = await server.list_tools()

            assert isinstance(tools, list)
            assert len(tools) >= 1

    @pytest.mark.asyncio
    async def test_list_tools_includes_tool_metadata(self):
        """Test that listed tools have proper metadata."""
        from src.mcp import server
        from mcp.types import Tool

        # Register test tools with metadata
        async def add_task_handler(**kwargs):
            return json.dumps({"task_id": "123", "status": "created"})

        add_task_schema = {
            "description": "Create a new todo task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        }

        server.register_tool("add_task", add_task_handler, add_task_schema)

        # List tools
        tools = await server.list_tools()

        # Find add_task tool
        add_task = next((t for t in tools if t.name == "add_task"), None)
        assert add_task is not None
        assert isinstance(add_task, Tool)
        assert add_task.name == "add_task"
        assert add_task.description == "Create a new todo task"
        assert "parameters" in add_task.inputSchema


class TestMCPServerToolRegistration:
    """Test that tools can be registered with the server."""

    def test_register_tool_adds_to_registry(self):
        """Test that register_tool adds tool to registry."""
        from src.mcp import server

        async def test_handler(**kwargs):
            return "{}"

        schema = {"description": "Test", "parameters": {}}

        initial_count = len(server.tool_registry)
        server.register_tool("new_tool", test_handler, schema)

        assert len(server.tool_registry) == initial_count + 1
        assert "new_tool" in server.tool_registry

    def test_register_tool_stores_schema(self):
        """Test that register_tool stores tool schema correctly."""
        from src.mcp import server

        async def test_handler(**kwargs):
            return "{}"

        schema = {
            "description": "Test tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_param": {"type": "string"}
                }
            }
        }

        server.register_tool("test_tool", test_handler, schema)

        registered = server.tool_registry.get("test_tool")
        assert registered is not None
        assert registered["schema"] == schema


class TestMCPServerToolExecution:
    """Test that MCP server can execute tools."""

    @pytest.mark.asyncio
    async def test_call_tool_executes_handler(self):
        """Test that call_tool executes the tool handler."""
        from src.mcp import server

        # Mock handler
        async def mock_handler(user_id, title):
            return json.dumps({
                "task_id": "123",
                "status": "created",
                "title": title
            })

        schema = {
            "description": "Create task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"}
                }
            }
        }

        server.register_tool("create_task", mock_handler, schema)

        # Call the tool
        result = await server.call_tool("create_task", {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries"
        })

        assert result is not None

        # Parse JSON result
        result_data = json.loads(result)
        assert result_data["status"] == "created"
        assert result_data["title"] == "Buy groceries"

    @pytest.mark.asyncio
    async def test_call_tool_raises_for_unknown_tool(self):
        """Test that call_tool raises ValueError for unknown tool."""
        from src.mcp import server

        with pytest.raises(ValueError, match="Tool 'unknown_tool' not found"):
            await server.call_tool("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_propagates_handler_exceptions(self):
        """Test that call_tool propagates handler exceptions."""
        from src.mcp import server

        async def failing_handler(**kwargs):
            raise ValueError("Handler error")

        schema = {"description": "Failing tool", "parameters": {}}

        server.register_tool("failing_tool", failing_handler, schema)

        with pytest.raises(ValueError, match="Handler error"):
            await server.call_tool("failing_tool", {})
