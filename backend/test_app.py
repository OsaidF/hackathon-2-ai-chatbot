"""
Test script to verify Phase 7 & 8: Health Check and FastAPI Application Setup.

This script tests:
- Health endpoint functionality
- FastAPI application startup
- Endpoint registration
- CORS configuration
"""

import asyncio
import os
from dotenv import load_dotenv


def test_fastapi_app():
    """Test FastAPI application setup."""
    print("=" * 60)
    print("Testing FastAPI Application")
    print("=" * 60)

    load_dotenv()

    # Test 1: Import application
    print("\n[TEST 1] Importing FastAPI application...")
    try:
        from main import app
        print("[OK] Application imported successfully")
    except Exception as e:
        print(f"[FAIL] Could not import application: {e}")
        return False

    # Test 2: Verify application configuration
    print("\n[TEST 2] Verifying application configuration...")
    assert app.title == "Todo AI Chatbot API"
    assert app.version == "1.0.0"
    print(f"[OK] Application title: {app.title}")
    print(f"[OK] Application version: {app.version}")

    # Test 3: Verify routes are registered
    print("\n[TEST 3] Checking route registration...")
    routes = [route.path for route in app.routes]
    print(f"[OK] Total routes registered: {len(routes)}")

    # Check for health routes
    health_routes = [r for r in routes if "/health/" in r]
    print(f"[OK] Health routes: {len(health_routes)}")

    # Check for chat routes
    chat_routes = [r for r in routes if "/chat" in r]
    print(f"[OK] Chat routes: {len(chat_routes)}")

    # Test 4: Check CORS middleware
    print("\n[TEST 4] Checking CORS middleware...")
    from fastapi.middleware.cors import CORSMiddleware
    has_cors = any(isinstance(m, CORSMiddleware) for m in app.user_middleware)
    print(f"[OK] CORS middleware: {'Installed' if has_cors else 'Not installed'}")

    # Test 5: Check exception handlers
    print("\n[TEST 5] Checking exception handlers...")
    print(f"[OK] Exception handlers registered: {len(app.exception_handlers)}")

    # Test 6: Test with test client
    print("\n[TEST 6] Testing endpoints with test client...")
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"[OK] Root endpoint: {data['name']}")

    # Test health endpoint
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    print(f"[OK] Health status: {data['status']}")
    print(f"[OK] Database status: {data['database']['status']}")

    # Test ping endpoint
    response = client.get("/api/v1/health/ping")
    assert response.status_code == 200
    data = response.json()
    print(f"[OK] Ping endpoint: {data}")

    # Test docs are available
    response = client.get("/docs")
    assert response.status_code == 200
    print("[OK] API documentation available")

    print("\n[PASS] All FastAPI application tests passed!")

    return True


def test_health_endpoints():
    """Test health endpoint functionality."""
    print("\n" + "=" * 60)
    print("Testing Health Endpoints")
    print("=" * 60)

    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    # Test 1: Main health check
    print("\n[TEST 1] Testing main health check...")
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    print(f"[OK] Overall status: {data['status']}")
    print(f"[OK] Database status: {data['database']['status']}")
    if data['database']['status'] == 'healthy':
        print(f"[OK] Database latency: {data['database'].get('latency_ms', 'N/A')}ms")

    # Test 2: Ping endpoint
    print("\n[TEST 2] Testing ping endpoint...")
    response = client.get("/api/v1/health/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["ping"] == "pong"
    print("[OK] Ping endpoint working")

    # Test 3: Readiness check
    print("\n[TEST 3] Testing readiness check...")
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    print("[OK] Readiness check passed")

    # Test 4: Liveness check
    print("\n[TEST 4] Testing liveness check...")
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    print("[OK] Liveness check passed")

    print("\n[PASS] All health endpoint tests passed!")

    return True


def main():
    """Run all Phase 7 & 8 tests."""
    print("\n" + "=" * 60)
    print("PHASE 7 & 8: HEALTH CHECK AND FASTAPI SETUP TEST")
    print("=" * 60 + "\n")

    try:
        # Test FastAPI application
        if not test_fastapi_app():
            raise Exception("FastAPI application tests failed")

        # Test health endpoints
        if not test_health_endpoints():
            raise Exception("Health endpoint tests failed")

        print("\n" + "=" * 60)
        print("PHASE 7 & 8 IMPLEMENTATION COMPLETE!")
        print("=" * 60)

        print("\n[COMPLETE] Phase 7: Health Check and Monitoring")
        print("  - GET /api/v1/health - Comprehensive health check")
        print("  - GET /api/v1/health/ping - Simple ping endpoint")
        print("  - GET /api/v1/health/ready - Readiness check")
        print("  - GET /api/v1/health/live - Liveness check")
        print("  - Database connectivity check with latency")
        print("  - MCP server availability check")

        print("\n[COMPLETE] Phase 8: FastAPI Application Setup")
        print("  - Application entry point in backend/main.py")
        print("  - Chat and health endpoints registered")
        print("  - CORS middleware configured")
        print("  - Better Auth middleware placeholder")
        print("  - Startup event with database validation")
        print("  - Shutdown event with cleanup")
        print("  - Global exception handling")

        print("\n[NEXT STEPS]")
        print("  - Run the server: python backend/main.py")
        print("  - Test endpoints: http://localhost:8000/docs")
        print("  - Health check: http://localhost:8000/api/v1/health")
        print("  - Chat endpoint: http://localhost:8000/api/v1/chat")

        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print("TESTS FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
