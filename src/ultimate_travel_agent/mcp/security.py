"""Security middleware, rate limiting, and request sanitization for Remote MCP Server."""

import logging
import re
import time
import uuid
from collections import defaultdict
from typing import Callable, Dict, Optional, Tuple
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from ultimate_travel_agent.mcp.auth import make_unauthorized_response, verify_request_auth
from ultimate_travel_agent.mcp.config import MCPHttpConfig

logger = logging.getLogger("ultimate_travel_agent.mcp.security")

# Sensitive tokens to redact in log messages
SECRET_PATTERN = re.compile(
    r"(bearer\s+[\w\-\.]+)|(key=[\w\-]+)|(token=[\w\-]+)|(password=[\w\-]+)|(secret=[\w\-]+)",
    re.IGNORECASE,
)


def sanitize_log_message(msg: str) -> str:
    """Redact sensitive credentials, bearer tokens, or query strings from log message."""
    return SECRET_PATTERN.sub("[REDACTED]", msg)


class InMemoryRateLimiter:
    """Thread-safe token bucket rate limiter for per-client IP throttling."""

    def __init__(self, rps: float = 20.0, burst: int = 50) -> None:
        self.rps = rps
        self.burst = burst
        # Stores (tokens, last_update_time) per client key
        self._clients: Dict[str, Tuple[float, float]] = defaultdict(lambda: (float(burst), time.monotonic()))

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is permitted under token bucket algorithm."""
        now = time.monotonic()
        tokens, last_time = self._clients[client_id]

        # Replenish tokens based on elapsed time
        elapsed = now - last_time
        tokens = min(float(self.burst), tokens + elapsed * self.rps)

        if tokens >= 1.0:
            self._clients[client_id] = (tokens - 1.0, now)
            return True
        else:
            self._clients[client_id] = (tokens, now)
            return False

    def reset(self) -> None:
        """Clear limiter memory (useful for testing)."""
        self._clients.clear()


class RemoteMCPSecurityMiddleware(BaseHTTPMiddleware):
    """Unified security middleware enforcing rate limiting, size limits, auth, and request IDs."""

    def __init__(
        self,
        app: Callable,
        config: MCPHttpConfig,
        rate_limiter: Optional[InMemoryRateLimiter] = None,
    ) -> None:
        super().__init__(app)
        self.config = config
        self.rate_limiter = rate_limiter or InMemoryRateLimiter(
            rps=config.rate_limit_rps,
            burst=config.rate_limit_burst,
        )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 1. Request ID tracking
        request_id = request.headers.get("x-request-id") or f"req-{uuid.uuid4().hex[:12]}"
        start_time = time.monotonic()

        client_host = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else client_host

        # 2. Skip security/auth checks on CORS preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response

        # 3. Payload size check
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length_int = int(content_length)
                if length_int > self.config.max_request_size_bytes:
                    logger.warning(
                        sanitize_log_message(
                            f"[{request_id}] Payload too large: {length_int} > {self.config.max_request_size_bytes}"
                        )
                    )
                    return JSONResponse(
                        {"error": "Payload Too Large", "max_bytes": self.config.max_request_size_bytes},
                        status_code=413,
                        headers={"x-request-id": request_id},
                    )
            except ValueError:
                pass

        # 4. Rate limiting check
        if self.config.rate_limit_enabled:
            if not self.rate_limiter.is_allowed(client_ip):
                logger.warning(
                    sanitize_log_message(
                        f"[{request_id}] Rate limit exceeded for client IP: {client_ip}"
                    )
                )
                return JSONResponse(
                    {
                        "error": "Too Many Requests",
                        "message": "Rate limit exceeded. Please throttle your requests.",
                        "status_code": 429,
                    },
                    status_code=429,
                    headers={"x-request-id": request_id, "Retry-After": "1"},
                )

        # 5. Authentication check on protected routes (exempting /health, /ready, /version)
        path = request.url.path
        is_health_probe = path in ("/health", "/ready", "/version", "/health/", "/ready/", "/version/")

        if not is_health_probe and self.config.auth_enabled:
            is_authed, error_msg = verify_request_auth(
                headers=dict(request.headers),
                expected_api_key=self.config.api_key,
                auth_enabled=True,
            )
            if not is_authed:
                logger.warning(
                    sanitize_log_message(
                        f"[{request_id}] Unauthorized access attempt to {path} from {client_ip}: {error_msg}"
                    )
                )
                resp = make_unauthorized_response(error_msg or "Unauthorized")
                resp.headers["x-request-id"] = request_id
                return resp

        # 6. Execute inner request
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.monotonic() - start_time) * 1000
            logger.error(
                sanitize_log_message(
                    f"[{request_id}] Internal server error on {request.method} {path} ({duration_ms:.1f}ms): {exc}"
                )
            )
            raise exc

        duration_ms = (time.monotonic() - start_time) * 1000
        logger.info(
            sanitize_log_message(
                f"[{request_id}] {request.method} {path} -> {response.status_code} ({duration_ms:.1f}ms)"
            )
        )

        response.headers["x-request-id"] = request_id
        return response
