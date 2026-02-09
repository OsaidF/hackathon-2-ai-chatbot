"""
Integration test for health endpoint (T070).

This test verifies the health check endpoint properly reports system status.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.api.health import router as health_router


@pytest.fixture
def health_client():
    """Create test client for health endpoint."""
    app = FastAPI()
    app.include_router(health_router)

    return TestClient(app)


def test_health_check_returns_status(health_client: TestClient):
    """
    Test that health check endpoint returns status information.
    """
    response = health_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "database" in data
    assert "mcp_server" in data

    # Verify database health status
    assert "status" in data["database"]
    assert "latency_ms" in data["database"]
    assert "message" in data["database"]

    # Verify MCP server health status
    assert "status" in data["mcp_server"]
    assert "message" in data["mcp_server"]


def test_health_check_overall_status_logic(health_client: TestClient):
    """
    Test that overall status reflects component statuses.
    """
    response = health_client.get("/api/v1/health")
    data = response.json()

    # Overall status should be one of: healthy, degraded, unhealthy
    assert data["status"] in ["healthy", "degraded", "unhealthy"]

    # If database is unhealthy, overall should be unhealthy
    if data["database"]["status"] == "unhealthy":
        assert data["status"] == "unhealthy"

    # If MCP server is unhealthy, overall should be unhealthy
    if data["mcp_server"]["status"] == "unhealthy":
        assert data["status"] == "unhealthy"


def test_ping_endpoint(health_client: TestClient):
    """
    Test simple ping endpoint.
    """
    response = health_client.get("/api/v1/health/ping")

    assert response.status_code == 200
    data = response.json()

    assert data["ping"] == "pong"


def test_readiness_endpoint(health_client: TestClient):
    """
    Test readiness check endpoint.
    """
    response = health_client.get("/api/v1/health/ready")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "ready"


def test_liveness_endpoint(health_client: TestClient):
    """
    Test liveness check endpoint.
    """
    response = health_client.get("/api/v1/health/live")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "alive"


def test_database_latency_reported(health_client: TestClient):
    """
    Test that database check reports latency.
    """
    response = health_client.get("/api/v1/health")
    data = response.json()

    # If database is healthy, latency should be reported
    if data["database"]["status"] == "healthy":
        assert "latency_ms" in data["database"]
        assert data["database"]["latency_ms"] is not None
        assert data["database"]["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_database_check_connects_to_actual_database():
    """
    Test that database check makes actual connection to database.
    """
    from src.api.health import check_database_health

    result = await check_database_health()

    # Should return status structure
    assert "status" in result
    assert "message" in result

    # If database is configured and accessible, should be healthy
    # If not configured, should be unhealthy with error message
    assert result["status"] in ["healthy", "unhealthy"]


def test_mcp_server_check_returns_status():
    """
    Test that MCP server check returns status structure.
    """
    from src.api.health import check_mcp_server_health

    result = check_mcp_server_health()

    # Should return status structure
    assert "status" in result
    assert "message" in result

    # Currently returns healthy (placeholder implementation)
    assert result["status"] == "healthy"


def test_all_health_endpoints_accessible(health_client: TestClient):
    """
    Test that all health endpoints are accessible.
    """
    endpoints = [
        "/api/v1/health",
        "/api/v1/health/ping",
        "/api/v1/health/ready",
        "/api/v1/health/live"
    ]

    for endpoint in endpoints:
        response = health_client.get(endpoint)
        assert response.status_code == 200, f"Endpoint {endpoint} should return 200"


@pytest.mark.asyncio
async def test_health_check_includes_all_required_fields():
    """
    Test that health check includes all required fields.
    """
    from src.api.health import health_check

    response = await health_check()

    # Verify all top-level fields
    assert hasattr(response, "status")
    assert hasattr(response, "timestamp")
    assert hasattr(response, "version")
    assert hasattr(response, "database")
    assert hasattr(response, "mcp_server")

    # Verify database fields
    assert "status" in response.database
    assert "message" in response.database

    # Verify MCP server fields
    assert "status" in response.mcp_server
    assert "message" in response.mcp_server
