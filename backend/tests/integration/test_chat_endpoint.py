"""
Integration test for chat endpoint (T050).

This test verifies the full request/response cycle of the chat endpoint:
- Creating new conversations
- Continuing existing conversations
- Persisting messages
- Retrieving conversation history
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.chat import router
from src.db.session import get_session
from src.services.chat_service import ChatService
from src.models.user import User


# Test client fixture
@pytest.fixture
def client(db_session: AsyncSession):
    """Create test client with database session override."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    # Override database dependency
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    # Override auth dependency for testing
    from src.auth.dependencies import get_current_user

    async def override_get_current_user():
        # Return a test user UUID
        return uuid4()

    app.dependency_overrides[get_current_user] = override_get_current_user

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_endpoint_new_conversation(db_session: AsyncSession, client: TestClient):
    """
    Test chat endpoint creates new conversation when conversation_id not provided.
    """
    # Arrange
    user_id = uuid4()

    # Override auth to return specific user
    from src.api.chat import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    async def override_get_session():
        yield db_session

    from src.auth.dependencies import get_current_user

    async def override_auth():
        return user_id

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_auth

    test_client = TestClient(app)

    # Act
    response = test_client.post(
        "/api/v1/chat",
        json={
            "message": "Add a task: Buy groceries"
        }
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert data["user_message"] == "Add a task: Buy groceries"
    assert "assistant_message" in data
    assert "history" in data
    assert len(data["history"]) == 2  # User message + assistant response

    # Verify messages in history
    assert data["history"][0]["role"] == "user"
    assert data["history"][0]["content"] == "Add a task: Buy groceries"
    assert data["history"][1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_chat_endpoint_existing_conversation(db_session: AsyncSession, client: TestClient):
    """
    Test chat endpoint continues existing conversation when conversation_id provided.
    """
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    # Create a conversation
    conv_result = await chat_service.create_conversation(user_id=user_id)
    conversation_id = conv_result["conversation_id"]

    # Add an initial message
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content="Initial message"
    )
    await chat_service.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content="Initial response"
    )

    # Override auth
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    async def override_get_session():
        yield db_session

    from src.auth.dependencies import get_current_user

    async def override_auth():
        return user_id

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_auth

    test_client = TestClient(app)

    # Act - send message to existing conversation
    response = test_client.post(
        "/api/v1/chat",
        json={
            "message": "Add another task: Clean room",
            "conversation_id": conversation_id
        }
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["conversation_id"] == conversation_id
    assert data["user_message"] == "Add another task: Clean room"
    assert len(data["history"]) == 4  # 2 initial + 2 new messages


@pytest.mark.asyncio
async def test_chat_endpoint_conversation_not_found(db_session: AsyncSession):
    """
    Test chat endpoint returns 404 when conversation_id doesn't exist or belongs to different user.
    """
    # Arrange
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    async def override_get_session():
        yield db_session

    from src.auth.dependencies import get_current_user

    async def override_auth():
        return uuid4()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_auth

    test_client = TestClient(app)

    # Act - try to access non-existent conversation
    response = test_client.post(
        "/api/v1/chat",
        json={
            "message": "Test message",
            "conversation_id": str(uuid4())  # Fake conversation ID
        }
    )

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_chat_endpoint_message_persistence(db_session: AsyncSession):
    """
    Test that messages are persisted to database and retrievable.
    """
    # Arrange
    user_id = uuid4()
    chat_service = ChatService(db_session)

    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    async def override_get_session():
        yield db_session

    from src.auth.dependencies import get_current_user

    async def override_auth():
        return user_id

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_auth

    test_client = TestClient(app)

    # Act - send message
    response = test_client.post(
        "/api/v1/chat",
        json={
            "message": "Test message for persistence"
        }
    )

    # Assert - check response
    assert response.status_code == 200
    data = response.json()
    conversation_id = data["conversation_id"]

    # Verify messages were persisted by retrieving from database
    history = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id
    )

    assert history is not None
    assert len(history) == 2
    assert history[0]["content"] == "Test message for persistence"
    assert history[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_chat_endpoint_health_check(client: TestClient):
    """
    Test health check endpoint.
    """
    # Act
    response = client.get("/api/v1/chat/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "chat"
