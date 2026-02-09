"""
Chat endpoint for Todo AI Chatbot (T046, T047, T048).

Provides POST /api/v1/chat endpoint for:
- Accepting user messages and optional conversation_id
- Loading conversation history if conversation_id provided
- Creating new conversation if conversation_id not provided
- Persisting user messages and assistant responses

Constitution Compliance:
- Stateless: All conversation data retrieved from database
- Database as Single Source of Truth: No in-memory conversation storage
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.services.chat_service import ChatService
from src.auth.dependencies import get_current_user
from src.agent.agent import get_agent_service


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message content"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID to continue existing conversation"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    conversation_id: str = Field(
        ...,
        description="Conversation ID (new or existing)"
    )
    user_message: str = Field(
        ...,
        description="User message that was sent"
    )
    assistant_message: str = Field(
        ...,
        description="Assistant response (placeholder for AI integration)"
    )
    history: list[dict] = Field(
        ...,
        description="Full conversation history including new messages"
    )


# Create router
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user)
):
    """
    Process chat message and return response.

    Args:
        request: Chat request with message and optional conversation_id
        session: Database session (dependency injected)
        user_id: User ID from JWT (extracted via Better Auth)

    Returns:
        ChatResponse with:
            - conversation_id: Existing or newly created conversation ID
            - user_message: The message user sent
            - assistant_message: Assistant response (placeholder for now)
            - history: Full conversation history including new messages

    Behavior:
        1. If conversation_id provided:
           - Load existing conversation
           - Verify user owns the conversation
           - Retrieve conversation history
        2. If conversation_id not provided:
           - Create new conversation for user
        3. Persist user message to database
        4. Generate assistant response (placeholder - will use AI in Phase 6)
        5. Persist assistant response to database
        6. Return full conversation history

    Raises:
        HTTPException 404: If conversation_id provided but not found or doesn't belong to user
    """
    chat_service = ChatService(session)
    conversation_id = None

    # Step 1 & 2: Load existing conversation or create new one
    if request.conversation_id:
        # Load existing conversation
        conversation_id = UUID(request.conversation_id)
        history = await chat_service.get_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id
        )

        if history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
    else:
        # Create new conversation
        conversation_result = await chat_service.create_conversation(user_id=user_id)
        conversation_id = UUID(conversation_result["conversation_id"])
        history = []

    # Step 3 & 4 & 5: Process message through AI agent
    # The agent will:
    # - Interpret the user's message
    # - Select appropriate tool (when fully implemented in T062-T065)
    # - Invoke MCP tools
    # - Generate natural language response
    # - Save both messages to conversation
    agent_service = get_agent_service()
    agent_response = await agent_service.process_message(
        user_message=request.message,
        user_id=user_id,
        conversation_id=conversation_id,
        session=session
    )

    # Step 6: Retrieve full conversation history
    full_history = await chat_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=user_id
    )

    return ChatResponse(
        conversation_id=str(conversation_id),
        user_message=request.message,
        assistant_message=agent_response["assistant_message"],
        history=full_history
    )


# Health check endpoint
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for chat service."""
    return {"status": "healthy", "service": "chat"}
