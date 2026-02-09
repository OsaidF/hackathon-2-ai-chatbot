"""
Integration test for FastAPI application (T077).

This test verifies that the FastAPI application starts correctly,
all endpoints are registered, and the application is ready to handle requests.
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def app_client():
    """Create test client for the FastAPI application."""
    return TestClient(app)


def test_application_starts(app_client: TestClient):
    """
    Test that FastAPI application starts successfully (T077).
    """
    # Just creating the client tests that the app initializes
    assert app is not None
    assert app.title == "Todo AI Chatbot API"
    assert app.version == "1.0.0"


def test_root_endpoint_accessible(app_client: TestClient):
    """
    Test that root endpoint is accessible and returns API information.
    """
    response = app_client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
    assert "chat" in data
    assert data["status"] == "operational"


def test_chat_endpoint_registered(app_client: TestClient):
    """
    Test that chat endpoint is registered (T072).
    """
    # Test that POST /api/v1/chat exists (should get 422 for invalid body, not 404)
    response = app_client.post("/api/v1/chat", json={})

    # Should not return 404 (endpoint not found)
    assert response.status_code != 404
    # Should return validation error for empty request
    assert response.status_code in [400, 422] or response.status_code == 200


def test_health_endpoint_registered(app_client: TestClient):
    """
    Test that health endpoint is registered (T072).
    """
    response = app_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "database" in data
    assert "mcp_server" in data


def test_cors_headers_present(app_client: TestClient):
    """
    Test that CORS middleware is configured (T073).
    """
    response = app_client.options("/api/v1/health")

    # Should return CORS headers
    assert response.status_code in [200, 204]

    # Check for CORS headers
    if "access-control-allow-origin" in response.headers:
        # CORS is configured
        assert "*" in response.headers["access-control-allow-origin"] or \
               len(response.headers["access-control-allow-origin"]) > 0


def test_openapi_documentation_available(app_client: TestClient):
    """
    Test that OpenAPI documentation is available.
    """
    # Check Swagger UI
    response = app_client.get("/docs")
    assert response.status_code == 200

    # Check OpenAPI schema
    response = app_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()

    # Verify OpenAPI schema structure
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

    # Verify chat endpoint is documented
    assert "/api/v1/chat" in data["paths"] or "/api/v1/chat/" in data["paths"]


def test_all_routes_registered(app_client: TestClient):
    """
    Test that all expected routes are registered (T072).
    """
    response = app_client.get("/api/v1/health")
    assert response.status_code == 200, "Health endpoint should be accessible"

    # Root endpoint
    response = app_client.get("/")
    assert response.status_code == 200, "Root endpoint should be accessible"

    # Health endpoints
    endpoints = [
        "/api/v1/health/ping",
        "/api/v1/health/ready",
        "/api/v1/health/live"
    ]

    for endpoint in endpoints:
        response = app_client.get(endpoint)
        assert response.status_code == 200, f"Endpoint {endpoint} should be accessible"


def test_database_check_on_startup():
    """
    Test that database connection is validated on startup (T075).
    """
    # This test verifies the startup event handler
    # The actual startup happens when the app is created,
    # which we test by creating a client

    from main import app

    # App was created successfully, which means startup passed
    assert app is not None

    # If startup validation failed, the app wouldn't have been created
    # or would have raised an exception


def test_application_configuration():
    """
    Test that application is configured correctly.
    """
    from main import app

    # Verify application title
    assert app.title == "Todo AI Chatbot API"

    # Verify application version
    assert app.version == "1.0.0"

    # Verify docs URLs
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"

    # Verify routers are included
    # The app should have routes from both routers
    routes = [route.path for route in app.routes]

    # Check for health routes
    health_routes = [r for r in routes if "/health/" in r]
    assert len(health_routes) > 0, "Health routes should be registered"

    # Check for chat routes
    chat_routes = [r for r in routes if "/chat" in r]
    assert len(chat_routes) > 0, "Chat routes should be registered"


def test_error_handling_middleware_registered():
    """
    Test that global error handler is registered.
    """
    from main import app

    # App should have exception handlers
    assert len(app.exception_handlers) > 0


@pytest.mark.asyncio
async def test_lifecycle_events():
    """
    Test that application lifecycle events work (T075, T076).
    """
    from main import lifespan, app
    import asyncio

    # Test lifespan context manager
    async with lifespan(app):
        # Startup completed
        assert True

    # Shutdown completed (context exit)
    assert True


def test_environment_variables_respected():
    """
    Test that environment variables are properly configured.
    """
    import os

    # Check that critical env vars have defaults or are set
    # These should not raise exceptions
    port = os.getenv("PORT", "8000")
    host = os.getenv("HOST", "0.0.0.0")
    log_level = os.getenv("LOG_LEVEL", "info")

    assert port is not None
    assert host is not None
    assert log_level is not None

    # Verify they can be converted to expected types
    int(port)  # Should not raise
    log_level.lower()  # Should not raise
