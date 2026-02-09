"""
Integration test for agent error handling (T066).

This test verifies that the agent handles errors gracefully and provides
helpful error messages when operations fail.
"""

import pytest
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_agent_handles_invalid_task_id_gracefully(db_session: AsyncSession):
    """
    Test that agent provides helpful error when task ID is invalid.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    fake_task_id = str(uuid4())
    user_message = f"Complete task '{fake_task_id}'"

    # TODO: After agent implementation (T061-T065):
    # from src.agent.agent import AgentService
    # agent = AgentService()
    # response = await agent.process_message(user_message, user_id, session=db_session)
    #
    # # Assert - Agent should provide helpful error message
    # assert "not found" in response["assistant_message"].lower() or \
    #        "couldn't find" in response["assistant_message"].lower() or \
    #        "doesn't exist" in response["assistant_message"].lower()

    pass


@pytest.mark.asyncio
async def test_agent_handles_empty_message_gracefully(db_session: AsyncSession):
    """
    Test that agent handles empty or whitespace-only messages.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    empty_messages = [
        "",
        "   ",
        "\n",
        "\t"
    ]

    for empty_message in empty_messages:
        # TODO: After agent implementation:
        # from src.agent.agent import AgentService
        # agent = AgentService()
        # response = await agent.process_message(empty_message, user_id, session=db_session)
        #
        # # Assert - Agent should ask for clarification or provide help
        # assert len(response["assistant_message"]) > 0  # Should respond somehow
        pass


@pytest.mark.asyncio
async def test_agent_handles_ambiguous_task_identifier(db_session: AsyncSession):
    """
    Test that agent handles ambiguous task references gracefully.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    from src.services.task_service import TaskService

    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    # Create multiple similar tasks
    task_service = TaskService(db_session)
    await task_service.create_task(user_id=user_id, title="Call mom")
    await task_service.create_task(user_id=user_id, title="Call dad")

    user_message = "Complete the call task"

    # TODO: After agent implementation:
    # from src.agent.agent import AgentService
    # agent = AgentService()
    # response = await agent.process_message(user_message, user_id, session=db_session)
    #
    # # Assert - Agent should ask for clarification
    # assert "which" in response["assistant_message"].lower() or \
    #        "clarify" in response["assistant_message"].lower() or \
    #        "more specific" in response["assistant_message"].lower()

    pass


@pytest.mark.asyncio
async def test_agent_handles_database_errors_gracefully(db_session: AsyncSession):
    """
    Test that agent handles database errors without crashing.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    user_message = "Add a task that will fail due to some database error"

    # TODO: After agent implementation:
    # This test would need to mock a database error scenario
    # For now, the test structure is in place

    pass


@pytest.mark.asyncio
async def test_agent_handles_unauthorized_access_gracefully(db_session: AsyncSession):
    """
    Test that agent handles attempts to access other users' tasks.
    """
    # Arrange
    user1_id = uuid4()
    user2_id = uuid4()

    from src.models.user import User
    from src.services.task_service import TaskService

    user1 = User(id=user1_id, email=f"user1_{user1_id.hex[:8]}@example.com")
    user2 = User(id=user2_id, email=f"user2_{user2_id.hex[:8]}@example.com")
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # User 1 creates a task
    task_service = TaskService(db_session)
    task = await task_service.create_task(user_id=user1_id, title="Secret task")
    task_id = task["task_id"]

    # User 2 tries to complete User 1's task
    user_message = f"Complete task '{task_id}'"

    # TODO: After agent implementation:
    # from src.agent.agent import AgentService
    # agent = AgentService()
    # response = await agent.process_message(user_message, user2_id, session=db_session)
    #
    # # Assert - Agent should handle this gracefully
    # assert "not found" in response["assistant_message"].lower() or \
    #        "can't access" in response["assistant_message"].lower() or \
    #        "doesn't exist" in response["assistant_message"].lower()

    pass


@pytest.mark.asyncio
async def test_agent_provides_helpful_error_for_unknown_intents(db_session: AsyncSession):
    """
    Test that agent provides helpful guidance for unclear intents.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    unclear_messages = [
        "do something",
        "help me",
        "what's the weather",
        "tell me a joke"
    ]

    for message in unclear_messages:
        # TODO: After agent implementation:
        # from src.agent.agent import AgentService
        # agent = AgentService()
        # response = await agent.process_message(message, user_id, session=db_session)
        #
        # # Assert - Agent should explain what it can do
        # assert len(response["assistant_message"]) > 0
        # # Should mention available capabilities
        # assert any(word in response["assistant_message"].lower() for word in
        #        ["task", "todo", "add", "list", "complete", "delete", "update"])
        pass


@pytest.mark.asyncio
async def test_agent_handles_multiple_interpretations(db_session: AsyncSession):
    """
    Test that agent asks for clarification when intent is ambiguous.
    """
    # Arrange
    user_id = uuid4()
    from src.models.user import User
    user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
    db_session.add(user)
    await db_session.commit()

    # Create a task
    from src.services.task_service import TaskService
    task_service = TaskService(db_session)
    await task_service.create_task(user_id=user_id, title="Buy groceries")

    ambiguous_messages = [
        "The groceries task",
        "That thing about groceries",
        "The grocery one"
    ]

    for message in ambiguous_messages:
        # TODO: After agent implementation:
        # from src.agent.agent import AgentService
        # agent = AgentService()
        # response = await agent.process_message(message, user_id, session=db_session)
        #
        # # Assert - Agent should ask for clarification or make reasonable guess
        # # It should either:
        # # 1. Ask "What would you like to do with the groceries task?"
        # # 2. Show task details: "Would you like to complete, delete, or update 'Buy groceries'?"
        # assert len(response["assistant_message"]) > 0
        pass
