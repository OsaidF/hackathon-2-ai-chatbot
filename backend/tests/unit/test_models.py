"""
Unit tests for data models.

Tests model validation, relationships, and constraints.
Tests should FAIL before implementation, then PASS after implementation.
"""

import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from datetime import datetime
from uuid import UUID, uuid4

from src.models.user import User, UserCreate, UserUpdate
from src.models.task import Task, TaskCreate, TaskUpdate, TaskList
from src.models.conversation import Conversation, ConversationCreate
from src.models.message import Message, MessageRole, MessageCreate, MessageList


# Test fixtures
@pytest.fixture
def test_engine():
    """Create in-memory SQLite database for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def test_user_id():
    """Provide a test user ID."""
    return uuid4()


@pytest.fixture
def test_conversation_id():
    """Provide a test conversation ID."""
    return uuid4()


class TestUserModel:
    """Test User model validation and constraints."""

    def test_user_creation_with_valid_data(self, test_session):
        """Test creating a user with valid data succeeds."""
        user = User(
            id=uuid4(),
            email="test@example.com"
        )
        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)

        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.email == "test@example.com"
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_email_must_be_unique(self, test_session):
        """Test that user emails must be unique."""
        user_id = uuid4()
        user1 = User(id=user_id, email="test@example.com")
        user2 = User(id=uuid4(), email="test@example.com")

        test_session.add(user1)
        test_session.commit()

        test_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            test_session.commit()

    def test_user_create_schema_validation(self):
        """Test UserCreate schema validation."""
        user_data = UserCreate(email="test@example.com")
        assert user_data.email == "test@example.com"


class TestTaskModel:
    """Test Task model validation and constraints."""

    def test_task_creation_with_valid_data(self, test_session, test_user_id):
        """Test creating a task with valid data succeeds."""
        task = Task(
            id=uuid4(),
            user_id=test_user_id,
            title="Buy groceries",
            completed=False
        )
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        assert task.id is not None
        assert isinstance(task.id, UUID)
        assert task.user_id == test_user_id
        assert task.title == "Buy groceries"
        assert task.completed is False
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_title_cannot_be_empty(self, test_session, test_user_id):
        """Test that task title must not be empty."""
        task = Task(
            id=uuid4(),
            user_id=test_user_id,
            title=""  # Empty title
        )

        test_session.add(task)
        with pytest.raises(Exception):  # Should fail validation or database constraint
            test_session.commit()

    def test_task_title_max_length(self, test_session, test_user_id):
        """Test that task title has max length of 500 characters."""
        long_title = "x" * 501  # Exceeds max length

        task = Task(
            id=uuid4(),
            user_id=test_user_id,
            title=long_title
        )

        test_session.add(task)
        with pytest.raises(Exception):  # Should fail validation
            test_session.commit()

    def test_task_completed_defaults_to_false(self, test_session, test_user_id):
        """Test that task.completed defaults to False."""
        task = Task(
            id=uuid4(),
            user_id=test_user_id,
            title="Test task"
        )

        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        assert task.completed is False

    def test_task_create_schema_validation(self):
        """Test TaskCreate schema validation."""
        task_data = TaskCreate(title="Buy groceries")
        assert task_data.title == "Buy groceries"

    def test_task_create_rejects_empty_title(self):
        """Test that TaskCreate rejects empty titles."""
        with pytest.raises(Exception):
            TaskCreate(title="")

    def test_task_create_rejects_too_long_title(self):
        """Test that TaskCreate rejects titles exceeding max length."""
        with pytest.raises(Exception):
            TaskCreate(title="x" * 501)


class TestConversationModel:
    """Test Conversation model validation and constraints."""

    def test_conversation_creation_with_valid_data(self, test_session, test_user_id):
        """Test creating a conversation with valid data succeeds."""
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id
        )
        test_session.add(conversation)
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.id is not None
        assert isinstance(conversation.id, UUID)
        assert conversation.user_id == test_user_id
        assert conversation.created_at is not None

    def test_conversation_requires_valid_user_id(self, test_session):
        """Test that conversation requires valid user_id."""
        conversation = Conversation(
            id=uuid4(),
            user_id=uuid4()  # User doesn't exist
        )

        test_session.add(conversation)
        # Should fail foreign key constraint
        with pytest.raises(Exception):
            test_session.commit()


class TestMessageModel:
    """Test Message model validation and constraints."""

    def test_message_creation_with_valid_data(self, test_session, test_conversation_id):
        """Test creating a message with valid data succeeds."""
        message = Message(
            id=uuid4(),
            conversation_id=test_conversation_id,
            role=MessageRole.USER,
            content="Hello, assistant"
        )
        test_session.add(message)
        test_session.commit()
        test_session.refresh(message)

        assert message.id is not None
        assert isinstance(message.id, UUID)
        assert message.conversation_id == test_conversation_id
        assert message.role == MessageRole.USER
        assert message.content == "Hello, assistant"
        assert message.created_at is not None

    def test_message_role_must_be_valid(self, test_session, test_conversation_id):
        """Test that message role must be user or assistant."""
        with pytest.raises(Exception):
            Message(
                id=uuid4(),
                conversation_id=test_conversation_id,
                role="invalid_role",  # Invalid role
                content="Test message"
            )

    def test_message_content_cannot_be_empty(self, test_session, test_conversation_id):
        """Test that message content cannot be empty."""
        message = Message(
            id=uuid4(),
            conversation_id=test_conversation_id,
            role=MessageRole.USER,
            content=""  # Empty content
        )

        test_session.add(message)
        with pytest.raises(Exception):
            test_session.commit()

    def test_message_content_max_length(self, test_session, test_conversation_id):
        """Test that message content has max length of 10000 characters."""
        long_content = "x" * 10001  # Exceeds max length

        message = Message(
            id=uuid4(),
            conversation_id=test_conversation_id,
            role=MessageRole.USER,
            content=long_content
        )

        test_session.add(message)
        with pytest.raises(Exception):
            test_session.commit()

    def test_message_requires_valid_conversation_id(self, test_session):
        """Test that message requires valid conversation_id."""
        message = Message(
            id=uuid4(),
            conversation_id=uuid4(),  # Conversation doesn't exist
            role=MessageRole.USER,
            content="Test message"
        )

        test_session.add(message)
        with pytest.raises(Exception):  # Foreign key constraint
            test_session.commit()


class TestModelRelationships:
    """Test relationships between models."""

    def test_user_cascade_deletes_conversations(self, test_session):
        """Test that deleting a user cascades to conversations."""
        user_id = uuid4()
        user = User(id=user_id, email="test@example.com")
        conversation = Conversation(id=uuid4(), user_id=user_id)

        test_session.add(user)
        test_session.add(conversation)
        test_session.commit()

        # Delete user
        test_session.delete(user)
        test_session.commit()

        # Verify conversation is deleted
        conversations = test_session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all()
        assert len(conversations) == 0

    def test_user_cascade_deletes_tasks(self, test_session):
        """Test that deleting a user cascades to tasks."""
        user_id = uuid4()
        user = User(id=user_id, email="test@example.com")
        task = Task(id=uuid4(), user_id=user_id, title="Test task")

        test_session.add(user)
        test_session.add(task)
        test_session.commit()

        # Delete user
        test_session.delete(user)
        test_session.commit()

        # Verify task is deleted
        tasks = test_session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()
        assert len(tasks) == 0

    def test_conversation_cascade_deletes_messages(self, test_session):
        """Test that deleting a conversation cascades to messages."""
        conversation_id = uuid4()
        user_id = uuid4()
        user = User(id=user_id, email="test@example.com")
        conversation = Conversation(id=conversation_id, user_id=user_id)
        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Test message"
        )

        test_session.add(user)
        test_session.add(conversation)
        test_session.add(message)
        test_session.commit()

        # Delete conversation
        test_session.delete(conversation)
        test_session.commit()

        # Verify message is deleted
        messages = test_session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        assert len(messages) == 0
