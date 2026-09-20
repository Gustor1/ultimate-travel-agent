from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ultimate_travel_agent.booking import (
    BookingConfirmation,
    BookingIntent,
    confirm_booking_handoff,
    prepare_booking_handoff,
)


def _intent() -> BookingIntent:
    return BookingIntent(
        booking_id="hotel-paris",
        item_type="hotel",
        provider="Example Hotel",
        booking_url="https://hotel.example/book/room-42",
        description="Refundable double room",
        total="450.00",
        currency="EUR",
        observed_at="2026-09-20T08:00:00Z",
        expires_at="2026-09-20T12:00:00Z",
        source_ids=["hotel-official"],
        cancellation_summary="Free cancellation until 2027-05-08 18:00 Europe/Paris",
    )


def test_booking_requires_exact_explicit_confirmation_then_user_checkout() -> None:
    now = datetime(2026, 9, 20, 9, tzinfo=timezone.utc)
    prepared = prepare_booking_handoff(_intent(), now=now)
    assert prepared.status == "ready_for_confirmation"
    confirmation = BookingConfirmation(
        booking_id="hotel-paris",
        accepted_total="450.00",
        currency="EUR",
        confirmation_text="CONFIRM",
        confirmed_at=now,
    )
    result = confirm_booking_handoff(_intent(), confirmation, now=now)
    assert result.status == "user_checkout_required"
    assert result.confirmed_total == Decimal("450.00")
    assert result.user_action_required


def test_booking_blocks_expired_or_changed_price() -> None:
    expired = prepare_booking_handoff(
        _intent(), now=datetime(2026, 9, 20, 13, tzinfo=timezone.utc)
    )
    assert expired.status == "blocked"
    confirmation = BookingConfirmation(
        booking_id="hotel-paris",
        accepted_total="449.00",
        currency="EUR",
        confirmation_text="CONFIRM",
        confirmed_at="2026-09-20T09:00:00Z",
    )
    mismatch = confirm_booking_handoff(
        _intent(), confirmation, now=datetime(2026, 9, 20, 9, tzinfo=timezone.utc)
    )
    assert mismatch.status == "blocked"
    assert "confirmed total does not match quote" in mismatch.blockers


def test_booking_url_must_be_specific_and_confirmation_literal() -> None:
    with pytest.raises(ValidationError, match="item-specific"):
        BookingIntent.model_validate(
            {**_intent().model_dump(), "booking_url": "https://hotel.example"}
        )
    with pytest.raises(ValidationError):
        BookingConfirmation(
            booking_id="hotel-paris",
            accepted_total="450",
            currency="EUR",
            confirmation_text="yes",  # type: ignore[arg-type]
            confirmed_at="2026-09-20T09:00:00Z",
        )
