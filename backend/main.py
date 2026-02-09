"""
FastAPI application entry point for Todo AI Chatbot (T071).

This is the main application file that wires together all components:
- Chat endpoint
- Health check endpoint
- CORS middleware (T073)
- Better Auth middleware (T074)
- Lifecycle events (T075, T076)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
import logging
import os

from src.api.chat import router as chat_router
from src.api.health import router as health_router
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.db.session import async_engine

# Import all models to register them with SQLAlchemy metadata
# This is required for ORM operations and foreign key relationships
from src.models import *


# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title="Todo AI Chatbot API",
    description="AI-powered task management with natural language interface",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


async def ensure_dev_user():
    """
    Ensure development user exists in database.

    In development mode, creates a default user if it doesn't exist.
    This matches the hardcoded user ID used in frontend AuthContext.
    """
    from sqlalchemy import select
    from src.models import User
    from src.db.session import async_session_maker
    from src.services.jwt_service import jwt_service

    dev_user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    async with async_session_maker() as session:
        # Check if dev user exists
        result = await session.execute(
            select(User).where(User.id == dev_user_id)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            # Create dev user with password
            dev_user = User(
                id=dev_user_id,
                email="dev@example.com",
                hashed_password=jwt_service.get_password_hash("password123")
            )
            session.add(dev_user)
            await session.commit()
            logger.info(f"✓ Development user created: {dev_user_id} (email: dev@example.com, password: password123)")
        else:
            logger.info(f"✓ Development user exists: {dev_user_id}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager (T075, T076).

    Handles startup and shutdown events for:
    - Database connection validation (T075)
    - Development user creation (dev mode only)
    - Database connection cleanup (T076)
    """
    # Startup
    logger.info("Starting Todo AI Chatbot API...")

    # Validate database connection (T075)
    try:
        from sqlalchemy import text

        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()

        logger.info("✓ Database connection validated")

    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )

    # Ensure development user exists (development mode only)
    if os.getenv("ENVIRONMENT") == "development":
        try:
            await ensure_dev_user()
        except Exception as e:
            logger.error(f"✗ Failed to create development user: {e}")
            # Don't fail startup, just log the error

    # TODO: Initialize MCP server here when needed
    logger.info("✓ Startup complete")

    yield

    # Shutdown (T076)
    logger.info("Shutting down Todo AI Chatbot API...")

    # Dispose database engine
    try:
        await async_engine.dispose()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Error closing database connections: {e}")

    logger.info("Shutdown complete")


# Register lifespan manager
app.router.lifespan_context = lifespan


# Add CORS middleware (T073)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO: Add Better Auth middleware (T074)
# This would integrate with your Better Auth setup for JWT validation
# For now, authentication is handled via dependency injection in endpoints


# Register routers (T072)
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)
app.include_router(health_router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        Welcome message with links to documentation.
    """
    return {
        "name": "Todo AI Chatbot API",
        "version": "1.0.0",
        "description": "AI-powered task management with natural language interface",
        "docs": "/docs",
        "health": "/api/v1/health",
        "chat": "/api/v1/chat",
        "status": "operational"
    }


# Global exception handler
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if os.getenv("DEBUG") == "true" else "Internal server error"
        }
    )


# Run with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
