"""
Database initialization module for Todo AI Chatbot.

This module handles database engine creation, table initialization, and
provides FastAPI dependencies for database session management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from .session import async_engine, get_session


async def init_database() -> None:
    """
    Initialize database by creating all tables.

    This function should be called during application startup to ensure
    all required tables exist. It uses SQLModel's metadata to create tables.

    Note:
        In production, use proper migration scripts (alembic or custom)
        instead of automatic table creation.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_database() -> None:
    """
    Close database connections.

    This function should be called during application shutdown to ensure
    all connections are properly closed.
    """
    await async_engine.dispose()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.

    This is an alternative to get_session() that can be used with
    async context managers instead of FastAPI dependencies.

    Yields:
        AsyncSession: Database session

    Example:
        async with get_db_session() as session:
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
    """
    async with get_session() as session:
        yield session


async def get_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    This function is used as a FastAPI dependency to provide database sessions
    to endpoint functions. Each request gets a new session.

    Yields:
        AsyncSession: Database session for the request

    Example:
        @app.get("/tasks")
        async def list_tasks(session: AsyncSession = Depends(get_session_dependency)):
            result = await session.execute(select(Task))
            return result.scalars().all()
    """
    async for session in get_session():
        yield session


# Export the commonly used dependency
get_session = get_session_dependency
