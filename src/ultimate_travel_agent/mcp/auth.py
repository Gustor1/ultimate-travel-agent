"""Authentication and authorization utilities for Remote MCP Server.

Provides constant-time token comparison, Bearer and X-API-Key header parsing,
and extensible hooks for future OAuth 2.1 / OIDC token validation.
"""

import abc
import secrets
from typing import Dict, Mapping, Optional, Tuple
from starlette.responses import JSONResponse, Response


class TokenValidator(abc.ABC):
    """Abstract base class for token validation strategies."""

    @abc.abstractmethod
    def validate(self, token: str) -> Tuple[bool, Optional[str]]:
        """Validate token and return (is_valid, error_message)."""
        pass


class StaticApiKeyValidator(TokenValidator):
    """Validates tokens against an environment-configured static API key."""

    def __init__(self, expected_api_key: str) -> None:
        self.expected_api_key = expected_api_key

    def validate(self, token: str) -> Tuple[bool, Optional[str]]:
        if not self.expected_api_key:
            return False, "Server API key is not configured."
        if secrets.compare_digest(token.strip(), self.expected_api_key.strip()):
            return True, None
        return False, "Invalid API key or bearer token."


class OAuthTokenValidator(TokenValidator):
    """Extensible validator stub for future OAuth 2.1 / OIDC JWT validation."""

    def __init__(self, issuer_url: Optional[str] = None, audience: Optional[str] = None) -> None:
        self.issuer_url = issuer_url
        self.audience = audience

    def validate(self, token: str) -> Tuple[bool, Optional[str]]:
        if not self.issuer_url:
            return False, "OAuth issuer URL is not configured on the server."
        # Stub for future external OIDC token decoding and signature checking
        if token.startswith("oauth-mock-valid-token"):
            return True, None
        return False, "OAuth token signature verification failed."


def extract_token_from_headers(headers: Mapping[str, str]) -> Optional[str]:
    """Extract authentication token from Authorization or X-API-Key header."""
    auth_header = headers.get("authorization") or headers.get("Authorization")
    if auth_header:
        parts = auth_header.strip().split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1].strip()
        elif len(parts) == 1:
            return parts[0].strip()

    api_key_header = headers.get("x-api-key") or headers.get("X-API-Key")
    if api_key_header:
        return api_key_header.strip()

    return None


def verify_request_auth(
    headers: Mapping[str, str],
    expected_api_key: Optional[str] = None,
    auth_enabled: bool = False,
    validator: Optional[TokenValidator] = None,
) -> Tuple[bool, Optional[str]]:
    """Verify incoming request credentials.

    Returns:
        (is_authenticated, error_reason)
    """
    if not auth_enabled:
        return True, None

    token = extract_token_from_headers(headers)
    if not token:
        return False, "Missing credentials. Provide 'Authorization: Bearer <token>' or 'X-API-Key' header."

    if validator:
        return validator.validate(token)

    if expected_api_key:
        static_val = StaticApiKeyValidator(expected_api_key)
        return static_val.validate(token)

    return False, "Server authentication is required but no validator or key is set."


def make_unauthorized_response(message: str = "Unauthorized") -> JSONResponse:
    """Create a standardized 401 Unauthorized response without leaking server secrets."""
    return JSONResponse(
        content={
            "error": "Unauthorized",
            "message": message,
            "status_code": 401,
        },
        status_code=401,
        headers={"WWW-Authenticate": "Bearer realm=\"ultimate-travel-mcp\""},
    )
