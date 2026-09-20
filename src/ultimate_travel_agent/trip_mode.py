"""Offline-first in-trip state and next-action guidance."""

from __future__ import annotations

from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class TripCompanionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    title: str = Field(min_length=1)
    start: datetime
    end: datetime
    local_address: str = Field(min_length=1)
    navigation_url: HttpUrl | None = None
    travel_buffer_minutes: int = Field(default=30, ge=0, le=360)
    reservation_required: bool = False
    booking_reference: str | None = None
    source_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def valid_item(self) -> "TripCompanionItem":
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("trip companion times must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("trip companion item must end after it starts")
        return self


class EmergencyContact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1)
    phone: str = Field(min_length=3)
    region: str = Field(min_length=1)


class TripModeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    now: datetime
    items: list[TripCompanionItem]
    emergency_contacts: list[EmergencyContact]
    network_available: bool = True
    offline_map_available: bool = False
    offline_documents_available: bool = False

    @model_validator(mode="after")
    def timezone_is_required(self) -> "TripModeRequest":
        if self.now.tzinfo is None:
            raise ValueError("trip mode now must be timezone-aware")
        identifiers = [item.item_id for item in self.items]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("trip companion item_id values must be unique")
        return self


class TripCompanionState(BaseModel):
    current_item_id: str | None
    next_item_id: str | None
    next_action: str
    minutes_until_departure: int | None
    alerts: list[str]
    offline_ready: bool
    emergency_contacts: list[EmergencyContact]


def build_trip_companion(request: TripModeRequest) -> TripCompanionState:
    """Return the current item, next action, and offline-readiness blockers."""

    items = sorted(request.items, key=lambda item: (item.start, item.item_id))
    current = next((item for item in items if item.start <= request.now < item.end), None)
    upcoming = next((item for item in items if item.start > request.now), None)
    alerts: list[str] = []
    for item in items:
        if item.reservation_required and not item.booking_reference:
            alerts.append(f"missing booking reference for {item.item_id}")
    if not request.emergency_contacts:
        alerts.append("no emergency contact is available offline")
    if not request.network_available and not request.offline_map_available:
        alerts.append("offline map is unavailable while network is offline")
    if not request.offline_documents_available:
        alerts.append("offline travel documents are unavailable")

    minutes_until_departure: int | None = None
    if current is not None:
        next_action = f"Continue: {current.title} until {current.end.isoformat()}"
    elif upcoming is not None:
        depart_at = upcoming.start - timedelta(minutes=upcoming.travel_buffer_minutes)
        minutes_until_departure = int((depart_at - request.now).total_seconds() // 60)
        if minutes_until_departure < 0:
            alerts.append(f"departure buffer for {upcoming.item_id} has already started")
            next_action = f"Leave now for {upcoming.title}: {upcoming.local_address}"
        else:
            next_action = (
                f"Leave for {upcoming.title} at {depart_at.isoformat()}: "
                f"{upcoming.local_address}"
            )
    else:
        next_action = "No remaining itinerary item"
    return TripCompanionState(
        current_item_id=current.item_id if current else None,
        next_item_id=upcoming.item_id if upcoming else None,
        next_action=next_action,
        minutes_until_departure=minutes_until_departure,
        alerts=alerts,
        offline_ready=not alerts,
        emergency_contacts=request.emergency_contacts,
    )
