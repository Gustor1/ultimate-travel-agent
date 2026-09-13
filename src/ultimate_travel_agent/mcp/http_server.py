"""Streamable HTTP Server for Remote MCP Architecture.

Exposes:
- GET /health: Liveness probe (unauthenticated)
- GET /ready: Readiness probe (unauthenticated)
- GET /version: Version & capabilities metadata (unauthenticated)
- POST /mcp (and GET /mcp for SSE): Streamable HTTP MCP transport (secured)

Enforces zero data leakage, in-memory rate limiting, request size bounds,
request ID tracing, and constant-time token validation.
"""

import sys
from typing import Optional
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from mcp.server.transport_security import TransportSecuritySettings

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from ultimate_travel_agent.mcp.config import MCPHttpConfig, load_mcp_config
from ultimate_travel_agent.mcp.health import health_endpoint, ready_endpoint, version_endpoint
from ultimate_travel_agent.mcp.security import RemoteMCPSecurityMiddleware
from ultimate_travel_agent.mcp.server import server


def create_http_app(config: Optional[MCPHttpConfig] = None) -> Starlette:
    """Build and configure the Streamable HTTP Starlette application."""
    cfg = config or load_mcp_config()

    # Configure transport security settings
    if cfg.enable_dns_rebinding_protection:
        transport_sec = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=cfg.allowed_hosts,
            allowed_origins=cfg.allowed_origins,
        )
    else:
        # Permissive transport security when deployed behind reverse proxy/load balancer
        transport_sec = TransportSecuritySettings(enable_dns_rebinding_protection=False)

    # Initialize the Starlette app with MCP streamable HTTP transport
    app = server.streamable_http_app(
        streamable_http_path=cfg.mcp_path,
        stateless_http=True,
        transport_security=transport_sec,
        max_request_body_size=cfg.max_request_size_bytes,
        host=cfg.host,
    )

    # Add unauthenticated health, readiness, and version routes
    app.add_route("/health", health_endpoint, methods=["GET"])
    app.add_route("/ready", ready_endpoint, methods=["GET"])
    app.add_route("/version", version_endpoint, methods=["GET"])

    # Add security middleware (rate limiting, payload sizing, request ID, token auth)
    app.add_middleware(RemoteMCPSecurityMiddleware, config=cfg)

    # Add CORS middleware with configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
        allow_headers=["*"],
    )

    return app


def run_http_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    config: Optional[MCPHttpConfig] = None,
) -> None:
    """Start uvicorn server serving Streamable HTTP MCP transport."""
    cfg = config or load_mcp_config()
    target_host = host or cfg.host
    target_port = port if port is not None else cfg.port

    app = create_http_app(cfg)

    print(f"🌍 Ultimate Travel Remote MCP Server starting on http://{target_host}:{target_port}")
    print(f"📡 MCP Endpoint: http://{target_host}:{target_port}{cfg.mcp_path}")
    print(f"🩺 Health Probe: http://{target_host}:{target_port}/health")
    print(f"🔒 Auth Enabled: {'Yes (Token/API-Key required)' if cfg.auth_enabled else 'No (Local/Development mode)'}")

    uvicorn.run(
        app,
        host=target_host,
        port=target_port,
        log_level=cfg.log_level.lower(),
        access_log=False,  # Handled by RemoteMCPSecurityMiddleware with secret redaction
    )


if __name__ == "__main__":
    run_http_server()
