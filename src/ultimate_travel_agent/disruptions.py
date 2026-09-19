"""Deterministic, local replanning for explicitly affected itinerary items."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ItineraryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    title: str = Field(min_length=1)
    category: Literal["transport", "lodging", "activity", "meal", "other"]
    start: datetime
    end: datetime
    fixed: bool = False

    @model_validator(mode="after")
    def valid_window(self) -> "ItineraryItem":
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("itinerary timestamps must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("itinerary item must end after it starts")
        return self


class Disruption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    disruption_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    kind: Literal["delay", "cancellation", "closure", "strike", "weather", "other"]
    affected_item_ids: list[str] = Field(min_length=1)
    summary: str = Field(min_length=1)
    observed_at: datetime
    source_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def valid_observation(self) -> "Disruption":
        if self.observed_at.tzinfo is None:
            raise ValueError("disruption observed_at must be timezone-aware")
        if len(self.affected_item_ids) != len(set(self.affected_item_ids)):
            raise ValueError("affected_item_ids must be unique")
        return self


class RecoveryOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    replaces_item_id: str
    title: str = Field(min_length=1)
    start: datetime
    end: datetime
    extra_cost: Decimal = Field(default=Decimal("0"), ge=0)
    available: bool = True
    verified: bool = False
    source_id: str | None = None

    @field_validator("extra_cost", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("recovery costs must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def valid_replacement(self) -> "RecoveryOption":
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("recovery timestamps must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("recovery option must end after it starts")
        if self.verified and not self.source_id:
            raise ValueError("verified recovery options require source_id")
        return self


class RecoverySelection(BaseModel):
    replaced_item_id: str
    option: RecoveryOption


class RecoveryPlan(BaseModel):
    disruption_id: str
    unchanged_item_ids: list[str]
    replacements: list[RecoverySelection]
    blockers: list[str]
    complete: bool


def _overlaps(first_start: datetime, first_end: datetime, second: ItineraryItem) -> bool:
    return first_start < second.end and first_end > second.start


def build_recovery_plan(
    itinerary: list[ItineraryItem],
    disruption: Disruption,
    options: list[RecoveryOption],
) -> RecoveryPlan:
    """Replace only affected items and preserve the rest of the itinerary."""

    item_map = {item.item_id: item for item in itinerary}
    if len(item_map) != len(itinerary):
        raise ValueError("itinerary item_id values must be unique")
    affected = set(disruption.affected_item_ids)
    unknown = sorted(affected - item_map.keys())
    blockers = [f"disruption references unknown item: {item_id}" for item_id in unknown]
    unaffected = [item for item in itinerary if item.item_id not in affected]
    selections: list[RecoverySelection] = []
    for item_id in disruption.affected_item_ids:
        if item_id not in item_map:
            continue
        candidates = [
            option
            for option in options
            if option.replaces_item_id == item_id
            and option.available
            and option.verified
            and not any(
                other.fixed and _overlaps(option.start, option.end, other)
                for other in unaffected
            )
        ]
        if not candidates:
            blockers.append(f"no verified conflict-free recovery for {item_id}")
            continue
        chosen = min(candidates, key=lambda option: (option.extra_cost, option.start, option.option_id))
        selections.append(RecoverySelection(replaced_item_id=item_id, option=chosen))
    return RecoveryPlan(
        disruption_id=disruption.disruption_id,
        unchanged_item_ids=[item.item_id for item in unaffected],
        replacements=selections,
        blockers=blockers,
        complete=not blockers and len(selections) == len(affected),
    )
