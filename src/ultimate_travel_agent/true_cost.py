"""Exact door-to-door travel cost comparison with completeness checks."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CostCategory = Literal[
    "airfare",
    "rail_or_bus_fare",
    "baggage",
    "seat_selection",
    "airport_transfer",
    "lodging",
    "taxes_and_fees",
    "breakfast",
    "local_transport",
    "extra_night",
    "insurance",
    "visa",
    "activities",
    "meals",
    "parking",
    "other",
]


class CostComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    category: CostCategory
    description: str = Field(min_length=1)
    unit_amount: Decimal = Field(ge=0)
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    verified: bool = False
    source_id: str | None = None

    @field_validator("unit_amount", "quantity", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("cost values must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def verified_cost_has_source(self) -> "CostComponent":
        if self.verified and not self.source_id:
            raise ValueError("verified cost components require source_id")
        return self

    @property
    def total(self) -> Decimal:
        return (self.unit_amount * self.quantity).quantize(Decimal("0.01"))


class DoorToDoorOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    label: str = Field(min_length=1)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    travelers: int = Field(default=1, ge=1, le=30)
    door_to_door_minutes: int = Field(gt=0, le=10080)
    components: list[CostComponent] = Field(min_length=1)
    separate_tickets: bool = False
    self_transfer: bool = False

    @model_validator(mode="after")
    def unique_components(self) -> "DoorToDoorOption":
        identifiers = [component.component_id for component in self.components]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("component_id values must be unique within an option")
        if self.self_transfer and not self.separate_tickets:
            raise ValueError("self-transfer must declare separate_tickets")
        return self


class TrueCostResult(BaseModel):
    option_id: str
    direct_cost: Decimal
    time_cost: Decimal
    risk_reserve: Decimal
    true_cost: Decimal
    missing_categories: list[CostCategory]
    unverified_components: list[str]
    complete: bool


class TrueCostComparison(BaseModel):
    currency: str
    preferred_option_id: str | None
    results: list[TrueCostResult]
    issues: list[str]


def compare_door_to_door_costs(
    options: list[DoorToDoorOption],
    *,
    required_categories: list[CostCategory],
    value_of_time_per_hour: Decimal = Decimal("0"),
    separate_ticket_reserve_percent: Decimal = Decimal("10"),
) -> TrueCostComparison:
    """Compare complete options without hiding time or self-transfer exposure."""

    if not options:
        raise ValueError("at least one option is required")
    if value_of_time_per_hour < 0 or separate_ticket_reserve_percent < 0:
        raise ValueError("time value and reserve percent cannot be negative")
    if len({option.option_id for option in options}) != len(options):
        raise ValueError("option_id values must be unique")
    currencies = {option.currency for option in options}
    if len(currencies) != 1:
        raise ValueError("all options must use the same comparison currency")

    results: list[TrueCostResult] = []
    issues: list[str] = []
    for option in options:
        categories = {component.category for component in option.components}
        missing = [category for category in required_categories if category not in categories]
        direct = sum((component.total for component in option.components), Decimal("0"))
        time_cost = (
            Decimal(option.door_to_door_minutes)
            / Decimal("60")
            * value_of_time_per_hour
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        risk_percent = (
            separate_ticket_reserve_percent
            if option.separate_tickets or option.self_transfer
            else Decimal("0")
        )
        risk = (direct * risk_percent / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        unverified = [
            component.component_id for component in option.components if not component.verified
        ]
        complete = not missing
        if missing:
            issues.append(f"{option.option_id} is missing categories: {', '.join(missing)}")
        results.append(
            TrueCostResult(
                option_id=option.option_id,
                direct_cost=direct.quantize(Decimal("0.01")),
                time_cost=time_cost,
                risk_reserve=risk,
                true_cost=(direct + time_cost + risk).quantize(Decimal("0.01")),
                missing_categories=missing,
                unverified_components=unverified,
                complete=complete,
            )
        )
    results.sort(key=lambda result: (not result.complete, result.true_cost, result.option_id))
    preferred = next((result.option_id for result in results if result.complete), None)
    if preferred is None:
        issues.append("no option has complete cost coverage")
    return TrueCostComparison(
        currency=options[0].currency,
        preferred_option_id=preferred,
        results=results,
        issues=issues,
    )
