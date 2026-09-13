"""Health, readiness, and version endpoints for Remote MCP Server.

Provides unauthenticated, sanitized status probes for orchestrators (Kubernetes,
Cloud Run, Railway, Render) and MCP clients without leaking server credentials.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from starlette.requests import Request
from starlette.responses import JSONResponse
from ultimate_travel_agent.integrations.registry import default_registry

SERVER_VERSION = "1.2.0"
SERVER_NAME = "ultimate-travel-agent"
MCP_PROTOCOL_VERSION = "2024-11-05"


def get_health_data() -> Dict[str, Any]:
    """Return sanitized liveness data."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
    }


def get_readiness_data() -> Dict[str, Any]:
    """Return sanitized readiness data."""
    providers_info = default_registry.list_providers()
    configured_count = sum(1 for p in providers_info if p.get("is_configured"))
    return {
        "status": "ready",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "mcp_protocol_version": MCP_PROTOCOL_VERSION,
        "providers_registered": len(providers_info),
        "providers_configured": configured_count,
        "default_mode": "offline",
        "live_booking_allowed": False,
    }


def get_version_data() -> Dict[str, Any]:
    """Return version and capability metadata."""
    return {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "mcp_protocol_version": MCP_PROTOCOL_VERSION,
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False,
            "streamable_http": True,
            "stateless_http": True,
        },
        "description": "Offline-first, privacy-respecting travel planning and provider hub MCP server.",
    }


async def health_endpoint(request: Request) -> JSONResponse:
    """GET /health - Liveness check."""
    return JSONResponse(get_health_data(), status_code=200)


async def ready_endpoint(request: Request) -> JSONResponse:
    """GET /ready - Readiness check."""
    return JSONResponse(get_readiness_data(), status_code=200)


async def version_endpoint(request: Request) -> JSONResponse:
    """GET /version - Version and capability specification."""
    return JSONResponse(get_version_data(), status_code=200)
