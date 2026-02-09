"""
Integration tests for database migrations.

Tests that schema creation, constraints, and data integrity work correctly.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


@pytest.fixture
def migration_engine():
    """Create an in-memory SQLite database for testing migrations."""
    # Use SQLite for fast testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    return engine


@pytest.fixture
def migration_session(migration_engine):
    """Create a test session for migration testing."""
    SQLModel.metadata.create_all(migration_engine)
    Session = sessionmaker(bind=migration_engine)
    with Session() as session:
        yield session


class TestMigrationSchemaCreation:
    """Test that migration creates all required tables."""

    def test_users_table_exists(self, migration_engine):
        """Test that users table is created."""
        with migration_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='todo_users'"
            ))
            tables = result.fetchall()
            assert len(tables) == 1
            assert tables[0][0] == "todo_users"

    def test_conversations_table_exists(self, migration_engine):
        """Test that conversations table is created."""
        with migration_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='todo_conversations'"
            ))
            tables = result.fetchall()
            assert len(tables) == 1

    def test_messages_table_exists(self, migration_engine):
        """Test that messages table is created."""
        with migration_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='todo_messages'"
            ))
            tables = result.fetchall()
            assert len(tables) == 1

    def test_tasks_table_exists(self, migration_engine):
        """Test that tasks table is created."""
        with migration_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='todo_tasks'"
            ))
            tables = result.fetchall()
            assert len(tables) == 1


class TestMigrationConstraints:
    """Test that constraints are properly enforced."""

    def test_users_email_unique_constraint(self, migration_session):
        """Test that users.email unique constraint works."""
        from src.models.user import User
        from uuid import uuid4

        user1 = User(id=uuid4(), email="test@example.com")
        user2 = User(id=uuid4(), email="test@example.com")

        migration_session.add(user1)
        migration_session.commit()

        migration_session.add(user2)
        with pytest.raises(Exception):  # Unique constraint violation
            migration_session.commit()

    def test_tasks_title_not_empty_constraint(self, migration_session):
        """Test that tasks.title not empty constraint works."""
        from src.models.task import Task
        from uuid import uuid4

        user_id = uuid4()
        task = Task(
            id=uuid4(),
            user_id=user_id,
            title=""  # Empty title
        )

        migration_session.add(task)
        with pytest.raises(Exception):  # Constraint violation
            migration_session.commit()

    def test_messages_role_check_constraint(self, migration_session):
        """Test that messages.role check constraint works."""
        from src.models.message import Message
        from uuid import uuid4

        conversation_id = uuid4()

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="invalid_role",  # Invalid role
            content="Test"
        )

        migration_session.add(message)
        # Should fail check constraint
        with pytest.raises(Exception):
            migration_session.commit()

    def test_messages_content_not_empty_constraint(self, migration_session):
        """Test that messages.content not empty constraint works."""
        from src.models.message import Message, MessageRole
        from uuid import uuid4

        conversation_id = uuid4()

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=""  # Empty content
        )

        migration_session.add(message)
        with pytest.raises(Exception):  # Constraint violation
            migration_session.commit()


class TestMigrationCascadeDeletes:
    """Test that cascade deletes work correctly."""

    def test_user_delete_cascades_to_conversations(self, migration_session):
        """Test that deleting a user cascades to conversations."""
        from src.models.user import User
        from src.models.conversation import Conversation
        from sqlmodel import select
        from uuid import uuid4

        user_id = uuid4()
        user = User(id=user_id, email="test@example.com")
        conversation = Conversation(id=uuid4(), user_id=user_id)

        migration_session.add(user)
        migration_session.add(conversation)
        migration_session.commit()

        # Delete user
        migration_session.delete(user)
        migration_session.commit()

        # Verify conversation is deleted
        conversations = migration_session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all()
        assert len(conversations) == 0

    def test_user_delete_cascades_to_tasks(self, migration_session):
        """Test that deleting a user cascades to tasks."""
        from src.models.user import User
        from src.models.task import Task
        from sqlmodel import select
        from uuid import uuid4

        user_id = uuid4()
        user = User(id=user_id, email="test@example.com")
        task = Task(id=uuid4(), user_id=user_id, title="Test task")

        migration_session.add(user)
        migration_session.add(task)
        migration_session.commit()

        # Delete user
        migration_session.delete(user)
        migration_session.commit()

        # Verify task is deleted
        tasks = migration_session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()
        assert len(tasks) == 0

    def test_conversation_delete_cascades_to_messages(self, migration_session):
        """Test that deleting a conversation cascades to messages."""
        from src.models.user import User
        from src.models.conversation import Conversation
        from src.models.message import Message, MessageRole
        from sqlmodel import select
        from uuid import uuid4

        user_id = uuid4()
        conversation_id = uuid4()

        user = User(id=user_id, email="test@example.com")
        conversation = Conversation(id=conversation_id, user_id=user_id)
        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Test message"
        )

        migration_session.add(user)
        migration_session.add(conversation)
        migration_session.add(message)
        migration_session.commit()

        # Delete conversation
        migration_session.delete(conversation)
        migration_session.commit()

        # Verify message is deleted
        messages = migration_session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        assert len(messages) == 0


class TestMigrationIndexes:
    """Test that indexes are properly created."""

    def test_conversations_user_id_index_exists(self, migration_engine):
        """Test that conversations.user_id index exists."""
        with migration_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%conversations_user_id%'"
            ))
            indexes = result.fetchall()
            assert len(indexes) > 0

    def test_messages_conversation_id_index_exists(self, migration_engine):
        """Test that messages conversation_id indexes exist."""
        with migration_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%messages_conversation_id%'"
            ))
            indexes = result.fetchall()
            assert len(indexes) > 0

    def test_tasks_user_id_index_exists(self, migration_engine):
        """Test that tasks.user_id indexes exist."""
        with migration_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%tasks_user_id%'"
            ))
            indexes = result.fetchall()
            assert len(indexes) > 0
