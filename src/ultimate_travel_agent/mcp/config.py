"""Configuration management for Remote MCP HTTP Server.

Supports 100% environment-driven configuration with safe defaults,
ensuring no credentials or secrets are hardcoded in the codebase.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MCPHttpConfig:
    """Server configuration parameters for Streamable HTTP MCP server."""

    host: str = "0.0.0.0"
    port: int = 8001
    mcp_path: str = "/mcp"

    # Authentication
    auth_enabled: bool = False
    api_key: Optional[str] = None
    require_auth_for_mcp: bool = True

    # Security & Protection
    max_request_size_bytes: int = 1_048_576  # 1 MB
    rate_limit_enabled: bool = True
    rate_limit_rps: float = 20.0
    rate_limit_burst: int = 50
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    allowed_hosts: List[str] = field(default_factory=lambda: ["*"])
    enable_dns_rebinding_protection: bool = False

    # Extensible OAuth 2.1 / OIDC (future hooks)
    oauth_enabled: bool = False
    oauth_issuer_url: Optional[str] = None
    oauth_audience: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    debug: bool = False

    @classmethod
    def from_env(cls) -> "MCPHttpConfig":
        """Construct configuration from environment variables."""
        api_key = (
            os.environ.get("TRAVEL_MCP_API_KEY")
            or os.environ.get("MCP_AUTH_TOKEN")
            or os.environ.get("API_KEY")
        )

        auth_req_env = os.environ.get("TRAVEL_MCP_AUTH_REQUIRED")
        if auth_req_env is not None:
            auth_enabled = auth_req_env.lower() in ("1", "true", "yes", "on")
        else:
            auth_enabled = bool(api_key)

        host = (
            os.environ.get("HOST")
            or os.environ.get("TRAVEL_MCP_HOST")
            or "0.0.0.0"
        )

        port_str = (
            os.environ.get("PORT")
            or os.environ.get("TRAVEL_MCP_PORT")
            or "8001"
        )
        try:
            port = int(port_str)
        except ValueError:
            port = 8001

        mcp_path = os.environ.get("TRAVEL_MCP_PATH", "/mcp")
        if not mcp_path.startswith("/"):
            mcp_path = "/" + mcp_path

        # Allowed origins
        origins_str = os.environ.get("TRAVEL_MCP_ALLOWED_ORIGINS", "*")
        origins = [o.strip() for o in origins_str.split(",") if o.strip()]

        # Allowed hosts
        hosts_str = os.environ.get("TRAVEL_MCP_ALLOWED_HOSTS", "*")
        hosts = [h.strip() for h in hosts_str.split(",") if h.strip()]

        # Request size limit
        try:
            max_size = int(os.environ.get("TRAVEL_MCP_MAX_REQUEST_SIZE", "1048576"))
        except ValueError:
            max_size = 1_048_576

        # Rate limiting
        rate_limit_enabled = os.environ.get("TRAVEL_MCP_RATE_LIMIT_ENABLED", "true").lower() in (
            "1", "true", "yes", "on"
        )
        try:
            rate_limit_rps = float(os.environ.get("TRAVEL_MCP_RATE_LIMIT_RPS", "20.0"))
        except ValueError:
            rate_limit_rps = 20.0

        try:
            rate_limit_burst = int(os.environ.get("TRAVEL_MCP_RATE_LIMIT_BURST", "50"))
        except ValueError:
            rate_limit_burst = 50

        dns_protection = os.environ.get("TRAVEL_MCP_DNS_PROTECTION", "false").lower() in (
            "1", "true", "yes", "on"
        )

        oauth_enabled = os.environ.get("TRAVEL_MCP_OAUTH_ENABLED", "false").lower() in (
            "1", "true", "yes", "on"
        )
        oauth_issuer = os.environ.get("TRAVEL_MCP_OAUTH_ISSUER")
        oauth_audience = os.environ.get("TRAVEL_MCP_OAUTH_AUDIENCE")

        log_level = os.environ.get("TRAVEL_MCP_LOG_LEVEL", "INFO").upper()
        debug = os.environ.get("TRAVEL_MCP_DEBUG", "false").lower() in ("1", "true", "yes", "on")

        return cls(
            host=host,
            port=port,
            mcp_path=mcp_path,
            auth_enabled=auth_enabled,
            api_key=api_key,
            require_auth_for_mcp=auth_enabled,
            max_request_size_bytes=max_size,
            rate_limit_enabled=rate_limit_enabled,
            rate_limit_rps=rate_limit_rps,
            rate_limit_burst=rate_limit_burst,
            allowed_origins=origins,
            allowed_hosts=hosts,
            enable_dns_rebinding_protection=dns_protection,
            oauth_enabled=oauth_enabled,
            oauth_issuer_url=oauth_issuer,
            oauth_audience=oauth_audience,
            log_level=log_level,
            debug=debug,
        )


def load_mcp_config() -> MCPHttpConfig:
    """Load configuration singleton from environment."""
    return MCPHttpConfig.from_env()
