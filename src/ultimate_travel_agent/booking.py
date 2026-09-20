"""Controlled booking handoffs with explicit price confirmation and no payment handling."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class BookingIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    item_type: Literal["flight", "hotel", "rail", "activity", "other"]
    provider: str = Field(min_length=1)
    booking_url: HttpUrl
    description: str = Field(min_length=1)
    total: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    observed_at: datetime
    expires_at: datetime | None = None
    source_ids: list[str] = Field(min_length=1)
    cancellation_summary: str = Field(min_length=1)

    @field_validator("total", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("booking totals must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def valid_times_and_url(self) -> "BookingIntent":
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.expires_at is not None:
            if self.expires_at.tzinfo is None:
                raise ValueError("expires_at must be timezone-aware")
            if self.expires_at <= self.observed_at:
                raise ValueError("expires_at must follow observed_at")
        parsed = urlparse(str(self.booking_url))
        if parsed.scheme != "https" or not parsed.path.rstrip("/"):
            raise ValueError("booking_url must be an HTTPS item-specific URL")
        if parsed.username or parsed.password:
            raise ValueError("booking_url cannot contain credentials")
        return self


class BookingHandoff(BaseModel):
    booking_id: str
    status: Literal["ready_for_confirmation", "blocked", "user_checkout_required"]
    booking_url: HttpUrl
    confirmed_total: Decimal | None = None
    currency: str
    checklist: list[str]
    blockers: list[str]
    user_action_required: bool = True


class BookingConfirmation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_id: str
    accepted_total: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    confirmation_text: Literal["CONFIRM"]
    confirmed_at: datetime

    @field_validator("accepted_total", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("confirmed totals must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def timezone_is_required(self) -> "BookingConfirmation":
        if self.confirmed_at.tzinfo is None:
            raise ValueError("confirmed_at must be timezone-aware")
        return self


def prepare_booking_handoff(
    intent: BookingIntent, *, now: datetime
) -> BookingHandoff:
    """Prepare a safe checkout handoff without storing traveler or payment data."""

    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    blockers: list[str] = []
    if intent.expires_at is not None and now >= intent.expires_at:
        blockers.append("booking quote has expired")
    checklist = [
        f"Recheck final total: {intent.total.quantize(Decimal('0.01'))} {intent.currency}",
        f"Review cancellation terms: {intent.cancellation_summary}",
        "Verify names, dates, occupancy, baggage, and included services on provider page",
        "Enter traveler and payment data only on the provider's secure website",
    ]
    return BookingHandoff(
        booking_id=intent.booking_id,
        status="blocked" if blockers else "ready_for_confirmation",
        booking_url=intent.booking_url,
        currency=intent.currency,
        checklist=checklist,
        blockers=blockers,
    )


def confirm_booking_handoff(
    intent: BookingIntent,
    confirmation: BookingConfirmation,
    *,
    now: datetime,
) -> BookingHandoff:
    """Confirm the exact quoted amount, then hand control to the user for checkout."""

    prepared = prepare_booking_handoff(intent, now=now)
    blockers = list(prepared.blockers)
    if confirmation.booking_id != intent.booking_id:
        blockers.append("confirmation does not match booking_id")
    if confirmation.currency != intent.currency:
        blockers.append("confirmation currency does not match quote")
    if confirmation.accepted_total != intent.total:
        blockers.append("confirmed total does not match quote")
    if confirmation.confirmed_at > now:
        blockers.append("confirmation cannot be in the future")
    return prepared.model_copy(
        update={
            "status": "blocked" if blockers else "user_checkout_required",
            "confirmed_total": confirmation.accepted_total if not blockers else None,
            "blockers": blockers,
            "user_action_required": True,
        }
    )
