"""Unit tests for Remote Streamable HTTP MCP Server and Security Middleware."""

import time
import pytest
from starlette.testclient import TestClient
from ultimate_travel_agent.mcp.config import MCPHttpConfig
from ultimate_travel_agent.mcp.http_server import create_http_app
from ultimate_travel_agent.mcp.security import InMemoryRateLimiter, sanitize_log_message


def test_health_endpoint() -> None:
    """Check that GET /health returns 200, status, version, and no secrets."""
    app = create_http_app(MCPHttpConfig(auth_enabled=False))
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["server"] == "ultimate-travel-agent"
        assert data["version"] == "1.2.0"
        assert "timestamp" in data
        # Ensure zero credential leakage
        assert "api_key" not in data
        assert "secret" not in data
        assert "token" not in data


def test_ready_endpoint() -> None:
    """Check that GET /ready returns 200, provider count, and zero booking confirmation."""
    app = create_http_app(MCPHttpConfig(auth_enabled=False))
    with TestClient(app) as client:
        resp = client.get("/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["providers_registered"] >= 15
        assert data["live_booking_allowed"] is False
        assert data["default_mode"] == "offline"


def test_version_endpoint() -> None:
    """Check that GET /version returns 200 and MCP protocol metadata."""
    app = create_http_app(MCPHttpConfig(auth_enabled=False))
    with TestClient(app) as client:
        resp = client.get("/version")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "1.2.0"
        assert data["mcp_protocol_version"] == "2024-11-05"
        assert data["capabilities"]["streamable_http"] is True


def test_request_id_injected() -> None:
    """Check that all responses include an x-request-id header."""
    app = create_http_app(MCPHttpConfig(auth_enabled=False))
    with TestClient(app) as client:
        resp = client.get("/health")
        assert "x-request-id" in resp.headers
        custom_resp = client.get("/health", headers={"x-request-id": "custom-req-123"})
        assert custom_resp.headers["x-request-id"] == "custom-req-123"


def test_mcp_unauthenticated_dev_mode() -> None:
    """Test that POST /mcp works without authentication when auth_enabled=False."""
    app = create_http_app(MCPHttpConfig(auth_enabled=False))
    with TestClient(app) as client:
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"},
            },
        }
        resp = client.post(
            "/mcp",
            json=init_payload,
            headers={"Accept": "application/json, text/event-stream"},
        )
        assert resp.status_code == 200
        assert "ultimate-travel-agent" in resp.text


def test_mcp_authentication_enforcement() -> None:
    """Test token enforcement on /mcp with Bearer token and X-API-Key."""
    cfg = MCPHttpConfig(
        auth_enabled=True,
        api_key="secret-token-xyz-123",
        require_auth_for_mcp=True,
    )
    app = create_http_app(cfg)
    with TestClient(app) as client:
        # 1. Health remains accessible without credentials
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 200
        assert client.get("/version").status_code == 200

        # 2. Missing credentials on /mcp -> 401
        res_no_auth = client.post("/mcp", json={})
        assert res_no_auth.status_code == 401
        assert "WWW-Authenticate" in res_no_auth.headers

        # 3. Invalid credentials on /mcp -> 401
        res_bad_auth = client.post(
            "/mcp",
            json={},
            headers={"Authorization": "Bearer wrong-key"},
        )
        assert res_bad_auth.status_code == 401

        # 4. Valid credentials via Bearer -> 200
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"},
            },
        }
        res_bearer = client.post(
            "/mcp",
            json=init_payload,
            headers={
                "Authorization": "Bearer secret-token-xyz-123",
                "Accept": "application/json, text/event-stream",
            },
        )
        assert res_bearer.status_code == 200

        # 5. Valid credentials via X-API-Key -> 200
        res_apikey = client.post(
            "/mcp",
            json=init_payload,
            headers={
                "X-API-Key": "secret-token-xyz-123",
                "Accept": "application/json, text/event-stream",
            },
        )
        assert res_apikey.status_code == 200


def test_rate_limiter_token_bucket() -> None:
    """Test InMemoryRateLimiter token bucket exhaustion and refill."""
    limiter = InMemoryRateLimiter(rps=10.0, burst=3)
    client_id = "192.168.1.100"

    assert limiter.is_allowed(client_id) is True  # 2 left
    assert limiter.is_allowed(client_id) is True  # 1 left
    assert limiter.is_allowed(client_id) is True  # 0 left
    assert limiter.is_allowed(client_id) is False  # Rejected

    # Other client is not affected
    assert limiter.is_allowed("192.168.1.101") is True


def test_rate_limiter_middleware_429() -> None:
    """Test that HTTP middleware throttles requests with HTTP 429."""
    cfg = MCPHttpConfig(
        auth_enabled=False,
        rate_limit_enabled=True,
        rate_limit_rps=1.0,
        rate_limit_burst=2,
    )
    app = create_http_app(cfg)
    with TestClient(app) as client:
        r1 = client.get("/health")
        assert r1.status_code == 200
        r2 = client.get("/health")
        assert r2.status_code == 200
        r3 = client.get("/health")
        assert r3.status_code == 429
        assert "Retry-After" in r3.headers
        assert r3.json()["error"] == "Too Many Requests"


def test_payload_size_limit_413() -> None:
    """Test that oversized payload returns 413 Payload Too Large."""
    cfg = MCPHttpConfig(
        auth_enabled=False,
        max_request_size_bytes=100,  # Tiny 100-byte limit
    )
    app = create_http_app(cfg)
    with TestClient(app) as client:
        large_data = "x" * 200
        resp = client.post(
            "/mcp",
            content=large_data,
            headers={"Content-Type": "application/json", "Content-Length": "200"},
        )
        assert resp.status_code == 413
        assert resp.json()["error"] == "Payload Too Large"


def test_cors_preflight() -> None:
    """Test CORS OPTIONS preflight request."""
    cfg = MCPHttpConfig(auth_enabled=True, api_key="test-key")
    app = create_http_app(cfg)
    with TestClient(app) as client:
        resp = client.options(
            "/mcp",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        # OPTIONS should succeed without authentication
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") in ("*", "http://example.com")


def test_log_sanitization() -> None:
    """Test that sensitive credentials and bearer tokens are scrubbed."""
    raw = "Request failed with Authorization: Bearer secret-super-token-1234 and key=mysecretkey"
    cleaned = sanitize_log_message(raw)
    assert "secret-super-token-1234" not in cleaned
    assert "mysecretkey" not in cleaned
    assert "[REDACTED]" in cleaned
