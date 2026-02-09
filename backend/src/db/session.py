"""
Database session management for Todo AI Chatbot.

This module provides async database session management using SQLModel and SQLAlchemy.
Follows stateless architecture principles - no session state is maintained between requests.
"""

from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_url() -> str:
    """
    Get database URL from environment variables.

    Returns:
        str: PostgreSQL database URL with async driver
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    # Convert to async PostgreSQL driver if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Remove sslmode parameter (asyncpg doesn't support it in URL, Neon uses SSL by default)
    if "sslmode=" in database_url:
        # Remove sslmode parameter from URL query string
        database_url = database_url.split("?")[0]  # Keep only base URL without params

    return database_url


# Async engine factory
async_engine = create_async_engine(
    get_database_url(),
    echo=os.getenv("LOG_LEVEL", "info") == "debug",
    future=True,
    # Connection pool settings to prevent stale connection errors
    pool_pre_ping=True,  # Validate connections before use
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Additional connections beyond pool_size
    pool_recycle=3600,   # Recycle connections after 1 hour (prevents timeout issues)
    connect_args={
        "timeout": 30,   # Connection timeout in seconds
        "command_timeout": 30,  # Command timeout in seconds
        "server_settings": {"application_name": "todo_ai_chatbot"},
    },
)

# Async session factory
async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session generator for dependency injection.

    This function is used as a FastAPI dependency to provide database sessions
    to endpoint functions. Each request gets a new session that is automatically
    closed after the request completes.

    Yields:
        AsyncSession: Async database session

    Example:
        @app.get("/tasks")
        async def list_tasks(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
            return tasks
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_sync_engine():
    """
    Get synchronous database engine for migrations and scripts.

    Returns:
        Engine: Synchronous SQLAlchemy engine

    Note:
        This should only be used for migration scripts and administrative tasks.
        Application code should use async engine via get_session().
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    return create_engine(database_url, echo=False)
