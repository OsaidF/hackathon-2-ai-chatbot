"""
Integration test for end-to-end agent→tool→DB flow (T060).

This test verifies the complete flow from user message through agent
to MCP tool invocation to database update.
"""

import pytest
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.task_service import TaskService


@pytest.mark.asyncio
async def test_end_to_end_create_task_flow(db_session: AsyncSession):
    """
    Test complete flow: User message → Agent → add_task tool → Database.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    user_message = "Add a task: Buy groceries"

    # Act - Agent processes message and invokes tool
    # TODO: After agent implementation (T061-T065):
    # from src.agent.agent import AgentService
    # agent = AgentService()
    #
    # # Agent interprets message and calls MCP tool
    # response = await agent.process_message(user_message, user_id, session=db_session)
    #
    # # Assert - Verify task was created in database
    # task_service = TaskService(db_session)
    # tasks = await task_service.list_tasks(user_id=user_id)
    # assert len(tasks) == 1
    # assert tasks[0]["title"] == "Buy groceries"
    # assert tasks[0]["completed"] is False
    #
    # # Assert - Verify agent response
    # assert "created" in response["assistant_message"].lower() or "added" in response["assistant_message"].lower()
    # assert "groceries" in response["assistant_message"].lower()

    # Placeholder - Implementation will come in T061-T065
    pass


@pytest.mark.asyncio
async def test_end_to_end_complete_task_flow(db_session: AsyncSession):
    """
    Test complete flow: Complete task message → Agent → complete_task tool → Database update.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    # Create a task first
    task_service = TaskService(db_session)
    task = await task_service.create_task(user_id=user_id, title="Buy groceries")
    task_id = task["task_id"]

    # Act - Agent processes complete task message
    user_message = f"Mark task '{task_id}' as done"

    # TODO: After agent implementation:
    # from src.agent.agent import AgentService
    # agent = AgentService()
    # response = await agent.process_message(user_message, user_id, session=db_session)
    #
    # # Assert - Verify task was completed in database
    # task = await task_service.get_task(task_id=UUID(task_id), user_id=user_id)
    # assert task["completed"] is True
    #
    # # Assert - Verify agent response
    # assert "completed" in response["assistant_message"].lower() or "done" in response["assistant_message"].lower()

    pass


@pytest.mark.asyncio
async def test_end_to_end_list_tasks_flow(db_session: AsyncSession):
    """
    Test complete flow: List tasks message → Agent → list_tasks tool → Database query → Response.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    # Create some tasks
    task_service = TaskService(db_session)
    await task_service.create_task(user_id=user_id, title="Buy groceries")
    await task_service.create_task(user_id=user_id, title="Call mom")
    await task_service.create_task(user_id=user_id, title="Finish report")

    # Act - Agent processes list tasks message
    user_message = "Show me my tasks"

    # TODO: After agent implementation:
    # from src.agent.agent import AgentService
    # agent = AgentService()
    # response = await agent.process_message(user_message, user_id, session=db_session)
    #
    # # Assert - Verify agent response includes tasks
    # assert "groceries" in response["assistant_message"].lower()
    # assert "mom" in response["assistant_message"].lower()
    # assert "report" in response["assistant_message"].lower()
    #
    # # Assert - Verify conversation history includes the response
    # assert len(response["history"]) > 0

    pass


@pytest.mark.asyncio
async def test_end_to_end_delete_task_flow(db_session: AsyncSession):
    """
    Test complete flow: Delete task message → Agent → delete_task tool → Database deletion.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    # Create a task
    task_service = TaskService(db_session)
    task = await task_service.create_task(user_id=user_id, title="Buy groceries")
    task_id = task["task_id"]

    # Act - Agent processes delete message
    user_message = f"Delete task '{task_id}'"

    # TODO: After agent implementation:
    # from src.agent.agent import AgentService
    # agent = AgentService()
    # response = await agent.process_message(user_message, user_id, session=db_session)
    #
    # # Assert - Verify task was deleted from database
    # tasks = await task_service.list_tasks(user_id=user_id)
    # assert len(tasks) == 0
    #
    # # Assert - Verify agent response
    # assert "deleted" in response["assistant_message"].lower() or "removed" in response["assistant_message"].lower()

    pass


@pytest.mark.asyncio
async def test_end_to_end_update_task_flow(db_session: AsyncSession):
    """
    Test complete flow: Update task message → Agent → update_task tool → Database update.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    # Create a task
    task_service = TaskService(db_session)
    task = await task_service.create_task(user_id=user_id, title="Buy groceries")
    task_id = task["task_id"]

    # Act - Agent processes update message
    user_message = f"Update task '{task_id}' to 'Buy groceries and milk'"

    # TODO: After agent implementation:
    # from src.agent.agent import AgentService
    # agent = AgentService()
    # response = await agent.process_message(user_message, user_id, session=db_session)
    #
    # # Assert - Verify task was updated in database
    # updated_task = await task_service.get_task(task_id=UUID(task_id), user_id=user_id)
    # assert updated_task["title"] == "Buy groceries and milk"
    #
    # # Assert - Verify agent response
    # assert "updated" in response["assistant_message"].lower() or "changed" in response["assistant_message"].lower()

    pass


@pytest.mark.asyncio
async def test_conversation_context_in_agent_flow(db_session: AsyncSession):
    """
    Test that agent maintains conversation context across multiple messages.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    from src.services.chat_service import ChatService

    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    chat_service = ChatService(db_session)
    conv_result = await chat_service.create_conversation(user_id=user_id)
    conversation_id = UUID(conv_result["conversation_id"])

    # TODO: After agent implementation:
    # from src.agent.agent import AgentService
    # agent = AgentService()
    #
    # # Message 1: Create task
    # response1 = await agent.process_message(
    #     "Add a task: Buy groceries",
    #     user_id,
    #     conversation_id=conversation_id,
    #     session=db_session
    # )
    #
    # # Message 2: Create another task (agent should know it's the same user)
    # response2 = await agent.process_message(
    #     "Add another task: Call mom",
    #     user_id,
    #     conversation_id=conversation_id,
    #     session=db_session
    # )
    #
    # # Message 3: Complete first task (agent should know which task)
    # response3 = await agent.process_message(
    #     "Mark the first task as done",
    #     user_id,
    #     conversation_id=conversation_id,
    #     session=db_session
    # )
    #
    # # Assert - Verify both tasks were created and one was completed
    # task_service = TaskService(db_session)
    # tasks = await task_service.list_tasks(user_id=user_id)
    # assert len(tasks) == 2
    #
    # completed_tasks = [t for t in tasks if t["completed"]]
    # assert len(completed_tasks) == 1

    pass
