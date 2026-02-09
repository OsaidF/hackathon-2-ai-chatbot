"""
ChatService for Todo AI Chatbot.

Handles conversation and message persistence for chat functionality.
Implements conversation continuity across server restarts.

Constitution Compliance:
- Stateless: All conversation data stored in database
- Database as Single Source of Truth: No in-memory conversation storage
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.conversation import Conversation
from src.models.message import Message


class ChatService:
    """
    Service for managing conversations and messages.

    Methods:
        create_conversation: Create a new conversation for a user
        get_conversation_history: Retrieve message history for a conversation
        save_message: Add a message to a conversation
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize ChatService with database session.

        Args:
            session: Async SQLAlchemy session for database operations
        """
        self.session = session

    async def create_conversation(self, user_id: UUID) -> dict:
        """
        Create a new conversation for a user.

        Args:
            user_id: UUID of the user creating the conversation

        Returns:
            Dictionary containing:
                - conversation_id: UUID of new conversation
                - user_id: UUID of conversation owner
                - created_at: Timestamp when conversation was created

        Raises:
            ValueError: If user_id is invalid
        """
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow()
        )

        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)

        return {
            "conversation_id": str(conversation.id),
            "user_id": str(conversation.user_id),
            "created_at": conversation.created_at
        }

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> Optional[list[dict]]:
        """
        Retrieve message history for a conversation.

        Args:
            conversation_id: UUID of the conversation
            user_id: UUID of the user requesting history

        Returns:
            List of message dictionaries ordered by created_at ASC, or None if:
                - Conversation doesn't exist
                - Conversation belongs to different user
            Each message dictionary contains:
                - id: Message UUID
                - role: "user" or "assistant"
                - content: Message text
                - created_at: Timestamp
        """
        # First verify the conversation exists and belongs to the user
        conv_stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conv_result = await self.session.execute(conv_stmt)
        conversation = conv_result.scalar_one_or_none()

        if conversation is None:
            return None

        # Retrieve messages in chronological order
        msg_stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        msg_result = await self.session.execute(msg_stmt)
        messages = msg_result.scalars().all()

        # Convert to list of dictionaries
        return [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]

    async def save_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str
    ) -> dict:
        """
        Save a message to a conversation.

        Args:
            conversation_id: UUID of the conversation
            role: Message role ("user" or "assistant")
            content: Message content (max 10,000 characters)

        Returns:
            Dictionary containing:
                - message_id: UUID of new message
                - conversation_id: UUID of conversation
                - role: Message role
                - content: Message content
                - created_at: Timestamp when message was created

        Raises:
            ValueError: If role is invalid or content is empty
        """
        # Validate role
        if role not in ["user", "assistant"]:
            raise ValueError(
                f"Invalid role: {role}. Must be 'user' or 'assistant'"
            )

        # Validate content
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content.strip(),
            created_at=datetime.utcnow()
        )

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        return {
            "message_id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
