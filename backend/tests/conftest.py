"""
Pytest configuration and fixtures for Todo AI Chatbot tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
from src.db.session import get_database_url


# Test database engine
test_engine = None
async_test_session_maker = None


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_test_database():
    """
    Set up test database engine and session maker.
    """
    global test_engine, async_test_session_maker

    # Get test database URL
    database_url = get_database_url()

    # Create async engine for tests
    test_engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )

    # Create session maker
    async_test_session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    yield

    # Cleanup: close engine
    await test_engine.dispose()


@pytest.fixture
async def db_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for each test.

    The session is rolled back after each test to ensure test isolation.
    Tests are responsible for managing their own transactions.
    """
    async with async_test_session_maker() as session:
        yield session

        # Rollback any pending changes after test (cleanup)
        await session.rollback()


@pytest.fixture
async def db_session_with_data(db_session: AsyncSession) -> AsyncSession:
    """
    Create a database session with test data.
    Creates a test user for use in tests.
    """
    # Create a test user
    test_user = User(
        id=uuid4(),
        email="test@example.com"
    )
    db_session.add(test_user)
    await db_session.commit()

    yield db_session


@pytest.fixture
def test_user_id():
    """
    Provide a consistent test user ID for tests.
    """
    return UUID("550e8400-e29b-41d4-a716-446655440000")


@pytest.fixture
async def db_session_with_user(db_session: AsyncSession, test_user_id) -> AsyncSession:
    """
    Create a database session with a test user already created.
    """
    # Create the test user
    test_user = User(
        id=test_user_id,
        email="test@example.com"
    )
    db_session.add(test_user)
    await db_session.commit()

    yield db_session
