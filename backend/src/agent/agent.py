"""
Agent configuration for Todo AI Chatbot (T061).

This module sets up the AI agent using OpenAI's API with Gemini model
to interpret user messages and invoke appropriate MCP tools.

Constitution Compliance:
- Stateless: Agent is stateless, all context from database
- MCP-First: All operations go through MCP tools
"""

import os
import json
from typing import Optional, List, Dict, Any
from uuid import UUID
from openai import OpenAI

from src.services.task_service import TaskService
from src.services.chat_service import ChatService
from src.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
)


# Tool schemas for OpenAI function calling
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new todo task for a user. Accepts a task title with optional priority, due date, and tags.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "title": {
                "type": "string",
                "description": "The task title/description (1-500 characters)"
            },
            "priority": {
                "type": "string",
                "description": "Task priority level (default: medium)",
                "enum": ["low", "medium", "high"]
            },
            "due_date": {
                "type": "string",
                "description": "Task due date in ISO format (e.g., 2025-01-25T10:30:00Z)"
            },
            "tags": {
                "type": "string",
                "description": "Task tags/categories (comma-separated)"
            }
        },
        "required": ["user_id", "title"]
    }
}

LIST_TASKS_SCHEMA = {
    "name": "list_tasks",
    "description": "Retrieve all tasks for a specific user. Optionally filter by completion status.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "filter_completed": {
                "type": "boolean",
                "description": "Optional filter (True=completed only, False=uncompleted only)"
            }
        },
        "required": ["user_id"]
    }
}

COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a specific task as completed. Use the task_id from the task list. Idempotent operation - completing an already-completed task succeeds.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "task_id": {
                "type": "string",
                "description": "Unique identifier of the task to complete (UUID format). Get this from the task list shown when listing tasks."
            }
        },
        "required": ["user_id", "task_id"]
    }
}

DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": "Permanently delete a specific task. Use the task_id from the task list. This operation cannot be undone.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "task_id": {
                "type": "string",
                "description": "Unique identifier of the task to delete (UUID format). Get this from the task list shown when listing tasks."
            }
        },
        "required": ["user_id", "task_id"]
    }
}

UPDATE_TASK_SCHEMA = {
    "name": "update_task",
    "description": "Update an existing task's properties (title, completed, priority, due_date, tags). Use to modify task details.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier of the user (UUID format)"
            },
            "task_id": {
                "type": "string",
                "description": "Unique identifier of the task to update (UUID format)"
            },
            "new_title": {
                "type": "string",
                "description": "New task title/description (1-500 characters)"
            },
            "completed": {
                "type": "boolean",
                "description": "Task completion status (true/false)"
            },
            "priority": {
                "type": "string",
                "description": "Task priority level",
                "enum": ["low", "medium", "high"]
            },
            "due_date": {
                "type": "string",
                "description": "Task due date in ISO format (e.g., 2025-01-25T10:30:00Z)"
            },
            "tags": {
                "type": "string",
                "description": "Task tags/categories (comma-separated)"
            }
        },
        "required": ["user_id", "task_id"]
    }
}


class AgentService:
    """
    AI Agent for natural language task management.

    Uses Google Gemini API with function calling to:
    - Interpret user intent from natural language
    - Select appropriate MCP tool
    - Extract parameters from user message
    - Generate natural language confirmations
    """

    def __init__(self):
        """Initialize agent with OpenAI client using Gemini model."""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Define available tools for function calling
        self.tools = [
            {
                "type": "function",
                "function": ADD_TASK_SCHEMA
            },
            {
                "type": "function",
                "function": LIST_TASKS_SCHEMA
            },
            {
                "type": "function",
                "function": COMPLETE_TASK_SCHEMA
            },
            {
                "type": "function",
                "function": DELETE_TASK_SCHEMA
            },
            {
                "type": "function",
                "function": UPDATE_TASK_SCHEMA
            }
        ]

    async def process_message(
        self,
        user_message: str,
        user_id: UUID,
        conversation_id: Optional[UUID],
        session
    ) -> Dict[str, Any]:
        """
        Process user message through AI agent.

        Args:
            user_message: User's natural language message
            user_id: User ID from authentication
            conversation_id: Optional conversation ID for context
            session: Database session

        Returns:
            Dictionary with:
                - assistant_message: Natural language response
                - history: Full conversation history
                - conversation_id: Conversation ID
        """
        # Get conversation history if conversation_id provided
        history = []
        if conversation_id:
            chat_service = ChatService(session)
            history = await chat_service.get_conversation_history(
                conversation_id=conversation_id,
                user_id=user_id
            )

        # Format conversation history for OpenAI
        messages = self._format_messages_for_openai(user_message, history)

        # Call OpenAI API with Gemini model and function calling
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
        except Exception as e:
            # Fallback to simple response if API call fails
            print(f"OpenAI API error: {e}")
            assistant_message = f"I encountered an error processing your request: {str(e)}"
        else:
            # Process the response
            assistant_message = await self._process_openai_response(
                response, user_id, session
            )

        # Save messages to conversation
        if conversation_id:
            await chat_service.save_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            )
            await chat_service.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_message
            )

        return {
            "assistant_message": assistant_message,
            "history": history,
            "conversation_id": str(conversation_id) if conversation_id else None
        }

    def _format_messages_for_openai(
        self,
        user_message: str,
        history: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        Format conversation history for OpenAI API.

        OpenAI uses an array of message objects with role and content.

        Args:
            user_message: Current user message
            history: Conversation history from database

        Returns:
            Formatted messages array for OpenAI API
        """
        messages = []

        # Add system prompt
        messages.append({
            "role": "system",
            "content": self._get_system_prompt()
        })

        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg['content']
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

    async def _process_openai_response(
        self,
        response,
        user_id: UUID,
        session
    ) -> str:
        """
        Process OpenAI API response and execute function calls.

        Args:
            response: OpenAI chat completion response
            user_id: User ID for MCP tools
            session: Database session

        Returns:
            str: Natural language response to user
        """
        message = response.choices[0].message

        # Check if the model wants to call a function
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"[DEBUG] Model extracted: {function_name}({function_args})")

            # Add user_id to the function arguments
            function_args['user_id'] = str(user_id)

            print(f"[DEBUG] After adding user_id: {function_args}")

            # Execute the appropriate MCP tool
            try:
                result = await self._execute_tool(function_name, function_args, session)

                # Generate a natural language response based on the result
                return self._generate_response_from_result(function_name, result)
            except Exception as e:
                # Return error message if tool execution fails
                return f"Sorry, I encountered an error: {str(e)}"
        else:
            # Return the direct response if no function call
            return message.content or "I understand. How can I help you with your tasks?"

    async def _execute_tool(
        self,
        function_name: str,
        function_args: Dict[str, Any],
        session
    ) -> str:
        """
        Execute an MCP tool by name.

        Args:
            function_name: Name of the tool/function to execute
            function_args: Arguments to pass to the tool
            session: Database session

        Returns:
            str: JSON string result from the tool
        """
        # Map function names to MCP tool functions
        tools_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task
        }

        if function_name not in tools_map:
            raise ValueError(f"Unknown tool: {function_name}")

        tool_function = tools_map[function_name]

        # Debug logging
        print(f"[DEBUG] Executing {function_name} with args: {function_args}")
        print(f"[DEBUG] Session type: {type(session)}, Session is None: {session is None}")

        # Validate required parameters based on function
        required_params = {
            "add_task": ["user_id", "title"],
            "list_tasks": ["user_id"],
            "complete_task": ["user_id", "task_id"],
            "delete_task": ["user_id", "task_id"],
            "update_task": ["user_id", "task_id"]
        }

        if function_name in required_params:
            missing = [p for p in required_params[function_name] if p not in function_args]
            if missing:
                raise ValueError(f"Missing required parameters: {missing}")

        # Execute the tool
        try:
            result = await tool_function(**function_args, session=session)
            print(f"[DEBUG] {function_name} result: {result[:200] if len(result) > 200 else result}...")
            return result
        except Exception as e:
            print(f"[ERROR] {function_name} failed: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _format_task_for_display(self, index: int, task: dict) -> str:
        """
        Format a single task for display in the task list.

        Args:
            index: Task number (0-based index)
            task: Task dictionary

        Returns:
            str: Formatted task string
        """
        status = '✓' if task.get('completed') else '○'
        title = task.get('title', 'Untitled')
        task_id = task.get('task_id', 'Unknown')

        # Build task details string
        details = []
        priority = task.get('priority')
        if priority and priority != 'medium':
            details.append(f"Priority: {priority}")

        due_date = task.get('due_date')
        if due_date:
            details.append(f"Due: {due_date}")

        tags = task.get('tags')
        if tags:
            details.append(f"Tags: {tags}")

        # Combine title with details
        if details:
            detail_str = " | ".join(details)
            return f"{index+1}. {status} {title}\n   (ID: {task_id})\n   [{detail_str}]"
        else:
            return f"{index+1}. {status} {title}\n   (ID: {task_id})"

    def _generate_response_from_result(self, function_name: str, result: str) -> str:
        """
        Generate a natural language response from tool execution result.

        Args:
            function_name: Name of the tool that was executed
            result: JSON string result from the tool

        Returns:
            str: Natural language response
        """
        try:
            result_data = json.loads(result)
        except json.JSONDecodeError:
            # If result is not JSON, return it as is
            return result

        # Generate responses based on function name and result
        if function_name == "add_task":
            if result_data.get("status") == "created":
                return f"I've added the task '{result_data.get('title')}' to your todo list."
            else:
                return "I tried to add the task but encountered an issue."

        elif function_name == "list_tasks":
            tasks = result_data.get("tasks", [])
            count = result_data.get("count", 0)
            if count == 0:
                return "You don't have any tasks yet. You can ask me to add one!"
            else:
                # Show tasks with numbered list for easy reference, including new fields
                task_list = "\n".join([
                    self._format_task_for_display(i, task)
                    for i, task in enumerate(tasks)
                ])
                return f"Here are your {count} task(s):\n{task_list}\n\nTip: Refer to tasks by number or use the full ID."

        elif function_name == "complete_task":
            if result_data.get("status") == "completed":
                return f"I've marked the task '{result_data.get('title')}' as completed."
            else:
                return "I tried to complete the task but encountered an issue."

        elif function_name == "delete_task":
            if result_data.get("status") == "deleted":
                return f"I've deleted the task '{result_data.get('title')}'."
            else:
                return "I tried to delete the task but encountered an issue."

        elif function_name == "update_task":
            if result_data.get("status") == "updated":
                return f"I've updated the task to: '{result_data.get('title')}'."
            else:
                return "I tried to update the task but encountered an issue."

        else:
            return "I've processed your request."

    def _get_system_prompt(self) -> str:
        """
        Get system prompt for the AI agent (T063).

        Defines the agent's behavior and capabilities.
        """
        return """You are a helpful task management assistant. You help users manage their todo list through natural language.

Available tools:
1. add_task: Create a new task with a title, optional priority (low/medium/high), due date, and tags
2. list_tasks: Show all tasks for the user with numbers and full UUIDs
3. complete_task: Mark a task as completed using the full task_id UUID
4. delete_task: Delete a task using the full task_id UUID
5. update_task: Change task properties (title, completed, priority, due_date, tags) using the full task_id UUID

IMPORTANT: For complete_task, delete_task, and update_task, you MUST use the full task_id UUID (not the number). When users say "complete task 1", translate it to the full UUID shown in the task list.

When users ask for help, be friendly and helpful. Always confirm what action you took.

Example interactions:
User: "Add a high priority task to buy groceries by Friday"
Assistant: I've added the task 'Buy groceries' to your todo list with high priority.

User: "Show me my tasks"
Assistant: Here are your 1 task(s):
1. ○ Buy groceries
   (ID: abc123de-1234-5678-9012-abcdef123456)

Tip: Refer to tasks by number or use the full ID.

User: "Complete task 1"
Assistant: I've marked 'Buy groceries' as completed.

User: "Delete task abc123de-1234-5678-9012-abcdef123456"
Assistant: I've deleted the task 'Buy groceries'.

Keep responses concise and friendly."""


# Singleton instance
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """
    Get or create singleton AgentService instance.

    Returns:
        AgentService: The agent service instance
    """
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
