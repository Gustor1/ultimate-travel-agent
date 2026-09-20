from urllib.request import Request

import pytest
from pydantic import ValidationError

from ultimate_travel_agent.notifications import (
    NotificationMessage,
    WebhookNotificationConfig,
    dispatch_webhook_notification,
)


class FakeResponse:
    def __init__(self, url: str, status: int = 204, body: bytes = b"") -> None:
        self.url = url
        self.status = status
        self.body = body

    def read(self, amount: int = -1) -> bytes:
        return self.body[:amount]

    def geturl(self) -> str:
        return self.url

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def _config() -> WebhookNotificationConfig:
    return WebhookNotificationConfig(
        notification_id="travel-alerts",
        endpoint="https://alerts.example/hooks/travel",
        signing_secret_env="TRAVEL_WEBHOOK_SECRET",
    )


def _message() -> NotificationMessage:
    return NotificationMessage(
        event_id="price-drop-123",
        subject="Flight price target reached",
        body="The verified price is now 480 EUR.",
        severity="warning",
        created_at="2026-09-20T10:00:00Z",
    )


def test_webhook_delivery_is_signed_and_returns_no_response_body() -> None:
    captured: dict[str, str | None] = {}

    def opener(request: Request, timeout: int) -> FakeResponse:
        captured["signature"] = request.get_header("X-travel-signature")
        captured["event"] = request.get_header("X-travel-event-id")
        return FakeResponse(request.full_url)

    receipt = dispatch_webhook_notification(
        _config(),
        _message(),
        environment={"TRAVEL_WEBHOOK_SECRET": "hidden"},
        open_url=opener,
    )
    assert captured["signature"] is not None
    assert str(captured["signature"]).startswith("sha256=")
    assert captured["event"] == "price-drop-123"
    assert receipt.status_code == 204
    assert "hidden" not in receipt.model_dump_json()


def test_webhook_requires_secret_and_blocks_cross_host_redirect() -> None:
    with pytest.raises(ValueError, match="missing webhook signing"):
        dispatch_webhook_notification(_config(), _message(), environment={})

    def redirected(request: Request, timeout: int) -> FakeResponse:
        return FakeResponse("https://evil.example/capture")

    with pytest.raises(ValueError, match="redirect changed host"):
        dispatch_webhook_notification(
            _config(),
            _message(),
            environment={"TRAVEL_WEBHOOK_SECRET": "hidden"},
            open_url=redirected,
        )


def test_webhook_endpoint_cannot_embed_credentials_or_be_generic() -> None:
    with pytest.raises(ValidationError, match="specific HTTPS"):
        WebhookNotificationConfig(
            notification_id="bad", endpoint="https://alerts.example"
        )
