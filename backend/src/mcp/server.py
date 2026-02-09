"""
MCP (Model Context Protocol) Server for Todo AI Chatbot.

This module sets up the MCP server with stdio transport and tool registry.
All task operations are exposed as stateless MCP tools.

Constitution Compliance:
- Principle II (MCP-First Design): All task operations through MCP tools only
- Principle I (Stateless Architecture): Tools query database directly, no state
"""

from typing import Any, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server instance
server = Server("todo-mcp-server")

# Tool registry - stores all available MCP tools
tool_registry: Dict[str, Any] = {}


def register_tool(name: str, handler: Any, schema: dict) -> None:
    """
    Register an MCP tool with the server.

    Args:
        name: Tool name (e.g., "add_task")
        handler: Async function that implements the tool
        schema: Tool schema describing parameters and returns
    """
    tool_registry[name] = {
        "handler": handler,
        "schema": schema
    }
    logger.info(f"Registered MCP tool: {name}")


async def call_tool(name: str, arguments: dict) -> str:
    """
    Call an MCP tool by name.

    Args:
        name: Tool name to call
        arguments: Tool parameters

    Returns:
        str: JSON string with tool result

    Raises:
        ValueError: If tool not found
        Exception: If tool execution fails
    """
    if name not in tool_registry:
        raise ValueError(f"Tool '{name}' not found in registry")

    tool = tool_registry[name]
    handler = tool["handler"]

    logger.info(f"Calling MCP tool: {name} with arguments: {arguments}")

    try:
        result = await handler(**arguments)
        return result
    except Exception as e:
        logger.error(f"Tool {name} failed: {str(e)}")
        raise


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools.

    Returns:
        list[Tool]: List of tool descriptions
    """
    tools = []

    for name, tool_data in tool_registry.items():
        schema = tool_data["schema"]

        tools.append(Tool(
            name=name,
            description=schema.get("description", ""),
            inputSchema=schema.get("parameters", {})
        ))

    logger.info(f"Listed {len(tools)} MCP tools")
    return tools


@server.call_tool()
async def handle_tool_call(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle incoming tool calls from the agent.

    Args:
        name: Tool name to call
        arguments: Tool parameters

    Returns:
        list[TextContent]: Tool result as text content
    """
    logger.info(f"Received tool call: {name} with arguments: {arguments}")

    try:
        result = await call_tool(name, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        error_msg = f"Error calling tool '{name}': {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point for MCP server."""
    logger.info("Starting MCP server for Todo AI Chatbot")

    # Import and register all tools
    # Tools will be registered when server starts
    # See: backend/src/mcp/tools/*.py

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
