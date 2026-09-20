"""Explicit, signed HTTPS webhook delivery for travel alert events."""

from __future__ import annotations

import hashlib
import hmac
import os
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from typing import Literal, Protocol, cast
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class WebhookNotificationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    notification_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    endpoint: HttpUrl
    signing_secret_env: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    timeout_seconds: int = Field(default=15, ge=1, le=30)
    maximum_response_bytes: int = Field(default=65_536, ge=0, le=1_000_000)

    @model_validator(mode="after")
    def secure_endpoint(self) -> "WebhookNotificationConfig":
        parsed = urlparse(str(self.endpoint))
        if parsed.scheme != "https" or not parsed.path.rstrip("/"):
            raise ValueError("webhook endpoint must be a specific HTTPS URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("webhook endpoint cannot contain credentials, query, or fragment")
        return self


class NotificationMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    subject: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=2000)
    severity: Literal["info", "warning", "critical"] = "info"
    created_at: datetime

    @model_validator(mode="after")
    def timezone_is_required(self) -> "NotificationMessage":
        if self.created_at.tzinfo is None:
            raise ValueError("notification created_at must be timezone-aware")
        return self


class NotificationReceipt(BaseModel):
    notification_id: str
    event_id: str
    endpoint: HttpUrl
    status_code: int
    delivered_at: datetime


class HttpResponse(Protocol):
    status: int

    def read(self, amount: int = -1) -> bytes: ...

    def geturl(self) -> str: ...

    def __enter__(self) -> "HttpResponse": ...

    def __exit__(self, *args: object) -> None: ...


OpenUrl = Callable[[Request, int], HttpResponse]


def dispatch_webhook_notification(
    config: WebhookNotificationConfig,
    message: NotificationMessage,
    *,
    environment: Mapping[str, str] | None = None,
    open_url: OpenUrl | None = None,
) -> NotificationReceipt:
    """Deliver one explicit alert event without returning secrets or response content."""

    env = environment if environment is not None else os.environ
    secret = env.get(config.signing_secret_env, "") if config.signing_secret_env else None
    if config.signing_secret_env and not secret:
        raise ValueError(
            f"missing webhook signing environment variable: {config.signing_secret_env}"
        )
    body = message.model_dump_json().encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ultimate-travel-agent/1",
        "X-Travel-Event-ID": message.event_id,
    }
    if secret is not None:
        digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        headers["X-Travel-Signature"] = f"sha256={digest}"
    request = Request(str(config.endpoint), data=body, headers=headers, method="POST")
    opener = open_url or cast(OpenUrl, urlopen)
    with opener(request, config.timeout_seconds) as response:
        if (urlparse(response.geturl()).hostname or "").lower() != (
            urlparse(str(config.endpoint)).hostname or ""
        ).lower():
            raise ValueError("webhook redirect changed host")
        if not 200 <= response.status < 300:
            raise ValueError(f"webhook returned HTTP status {response.status}")
        raw = response.read(config.maximum_response_bytes + 1)
        if len(raw) > config.maximum_response_bytes:
            raise ValueError("webhook response exceeds maximum_response_bytes")
        return NotificationReceipt(
            notification_id=config.notification_id,
            event_id=message.event_id,
            endpoint=config.endpoint,
            status_code=response.status,
            delivered_at=datetime.now(timezone.utc),
        )
