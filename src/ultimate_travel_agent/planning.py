"""Deterministic scoring, geography, time, budget, scenario, and decision helpers."""

from __future__ import annotations

import math
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ultimate_travel_agent.profiles import TravelerProfile


class ScoreWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cost: Decimal = Decimal("0.20")
    duration: Decimal = Decimal("0.15")
    fatigue: Decimal = Decimal("0.15")
    reliability: Decimal = Decimal("0.20")
    flexibility: Decimal = Decimal("0.10")
    safety: Decimal = Decimal("0.15")
    carbon: Decimal = Decimal("0.05")

    @field_validator("*", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("score weights must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def weights_total_one(self) -> "ScoreWeights":
        total = sum(self.model_dump().values(), Decimal("0"))
        if abs(total - Decimal("1")) > Decimal("0.0001"):
            raise ValueError(f"score weights must total 1, got {total}")
        return self


class OptionMetrics(BaseModel):
    """Normalized scores where 100 is always best."""

    model_config = ConfigDict(extra="forbid")

    option_id: str = Field(min_length=1)
    cost: int = Field(ge=0, le=100)
    duration: int = Field(ge=0, le=100)
    fatigue: int = Field(ge=0, le=100)
    reliability: int = Field(ge=0, le=100)
    flexibility: int = Field(ge=0, le=100)
    safety: int = Field(ge=0, le=100)
    carbon: int = Field(ge=0, le=100)


class ScoredOption(BaseModel):
    option_id: str
    total: Decimal
    breakdown: dict[str, Decimal]


def score_options(
    options: list[OptionMetrics], weights: ScoreWeights | None = None
) -> list[ScoredOption]:
    """Score options with a visible per-criterion breakdown."""

    active_weights = weights or ScoreWeights()
    weight_map = active_weights.model_dump()
    results: list[ScoredOption] = []
    for option in options:
        values = option.model_dump(exclude={"option_id"})
        breakdown = {
            name: (Decimal(value) * weight_map[name]).quantize(Decimal("0.01"))
            for name, value in values.items()
        }
        results.append(
            ScoredOption(
                option_id=option.option_id,
                total=sum(breakdown.values(), Decimal("0")).quantize(Decimal("0.01")),
                breakdown=breakdown,
            )
        )
    return sorted(results, key=lambda result: (-result.total, result.option_id))


class Place(BaseModel):
    model_config = ConfigDict(extra="forbid")

    place_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    neighborhood: str | None = None
    timezone: str

    @model_validator(mode="after")
    def valid_timezone(self) -> "Place":
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown IANA timezone: {self.timezone}") from exc
        return self


class PlannedStop(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stop_id: str
    place: Place
    start: datetime
    end: datetime
    walking_km: Decimal = Field(default=Decimal("0"), ge=0)
    transit_minutes: int = Field(default=0, ge=0)
    fixed: bool = False

    @model_validator(mode="after")
    def ends_after_start(self) -> "PlannedStop":
        if self.end <= self.start:
            raise ValueError("stop end must be after start")
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("stop times must be timezone-aware")
        return self


class RouteAnalysis(BaseModel):
    ordered_stop_ids: list[str]
    straight_line_km: Decimal
    walking_km: Decimal
    transit_minutes: int
    issues: list[str]


def haversine_km(first: Place, second: Place) -> Decimal:
    """Return straight-line distance between two WGS84 points."""

    radius_km = 6371.0088
    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [first.latitude, first.longitude, second.latitude, second.longitude],
    )
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    value = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    return Decimal(str(2 * radius_km * math.asin(math.sqrt(value)))).quantize(Decimal("0.01"))


def optimize_stop_order(stops: list[PlannedStop]) -> list[PlannedStop]:
    """Nearest-neighbor order for flexible stops, anchored by first input stop."""

    if len(stops) < 3 or any(stop.fixed for stop in stops[1:]):
        return list(stops)
    ordered = [stops[0]]
    remaining = list(stops[1:])
    while remaining:
        previous = ordered[-1]
        next_stop = min(
            remaining,
            key=lambda candidate: (
                haversine_km(previous.place, candidate.place),
                candidate.stop_id,
            ),
        )
        ordered.append(next_stop)
        remaining.remove(next_stop)
    return ordered


def analyze_route(stops: list[PlannedStop], profile: TravelerProfile) -> RouteAnalysis:
    """Check distance, walking, transit, overlaps, and daily profile limits."""

    issues: list[str] = []
    total_distance = Decimal("0")
    for previous, current in zip(stops, stops[1:], strict=False):
        if current.start < previous.end:
            issues.append(f"{current.stop_id} overlaps {previous.stop_id}")
        leg = haversine_km(previous.place, current.place)
        total_distance += leg
        if leg > Decimal("15") and current.transit_minutes == 0:
            issues.append(f"{current.stop_id} is {leg} km away without transit time")
    walking = sum((stop.walking_km for stop in stops), Decimal("0"))
    transit = sum(stop.transit_minutes for stop in stops)
    active_hours = sum(
        (Decimal(str((stop.end - stop.start).total_seconds())) / Decimal("3600") for stop in stops),
        Decimal("0"),
    )
    if walking > profile.daily_walking_km:
        issues.append(f"walking {walking} km exceeds profile limit {profile.daily_walking_km} km")
    if active_hours > profile.max_daily_activity_hours:
        issues.append(
            f"activity time {active_hours.quantize(Decimal('0.1'))} h exceeds profile limit "
            f"{profile.max_daily_activity_hours} h"
        )
    return RouteAnalysis(
        ordered_stop_ids=[stop.stop_id for stop in stops],
        straight_line_km=total_distance.quantize(Decimal("0.01")),
        walking_km=walking,
        transit_minutes=transit,
        issues=issues,
    )


def connection_is_safe(arrival: datetime, departure: datetime, minimum_minutes: int) -> bool:
    """Evaluate a connection after normalizing both timestamps to UTC."""

    if arrival.tzinfo is None or departure.tzinfo is None:
        raise ValueError("connection timestamps must be timezone-aware")
    available = (departure - arrival).total_seconds() / 60
    return available >= minimum_minutes


def jet_lag_recovery_days(
    origin_timezone: str, destination_timezone: str, on_date: date | None = None
) -> int:
    """Conservative recovery estimate using offsets on the travel date."""

    now = datetime.combine(on_date or date.today(), datetime.min.time(), tzinfo=ZoneInfo("UTC"))
    origin_offset = now.astimezone(ZoneInfo(origin_timezone)).utcoffset()
    destination_offset = now.astimezone(ZoneInfo(destination_timezone)).utcoffset()
    if origin_offset is None or destination_offset is None:
        return 0
    hours = abs((destination_offset - origin_offset).total_seconds()) / 3600
    return min(3, math.ceil(hours / 3))


class CostEstimate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    category: str
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    low: Decimal = Field(ge=0)
    likely: Decimal = Field(ge=0)
    high: Decimal = Field(ge=0)

    @field_validator("low", "likely", "high", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("costs must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def ordered_range(self) -> "CostEstimate":
        if not self.low <= self.likely <= self.high:
            raise ValueError("cost range must satisfy low <= likely <= high")
        return self


class ExchangeRate(BaseModel):
    from_currency: str = Field(pattern=r"^[A-Z]{3}$")
    to_currency: str = Field(pattern=r"^[A-Z]{3}$")
    rate: Decimal = Field(gt=0)
    observed_at: datetime
    source: str = Field(min_length=1)

    @field_validator("rate", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("exchange rates must use decimal strings or integers")
        return value


class BudgetSummary(BaseModel):
    currency: str
    low: Decimal
    likely: Decimal
    high: Decimal
    reserve: Decimal
    likely_with_reserve: Decimal
    by_category: dict[str, Decimal]
    issues: list[str]
    complete: bool


def calculate_budget(
    estimates: list[CostEstimate],
    target_currency: str,
    exchange_rates: list[ExchangeRate] | None = None,
    reserve_percent: Decimal = Decimal("15"),
    category_caps: dict[str, Decimal] | None = None,
) -> BudgetSummary:
    """Consolidate low/likely/high costs with dated FX rates and reserve."""

    rate_map = {
        (rate.from_currency, rate.to_currency): rate.rate for rate in exchange_rates or []
    }
    totals = {"low": Decimal("0"), "likely": Decimal("0"), "high": Decimal("0")}
    categories: dict[str, Decimal] = {}
    issues: list[str] = []
    for estimate in estimates:
        if estimate.currency == target_currency:
            rate = Decimal("1")
        else:
            rate = rate_map.get((estimate.currency, target_currency), Decimal("0"))
            if rate == 0:
                issues.append(
                    f"missing exchange rate {estimate.currency}/{target_currency} for {estimate.item_id}"
                )
                continue
        for field in totals:
            totals[field] += getattr(estimate, field) * rate
        converted_likely = estimate.likely * rate
        categories[estimate.category] = categories.get(estimate.category, Decimal("0")) + converted_likely
    for category, cap in (category_caps or {}).items():
        if categories.get(category, Decimal("0")) > cap:
            issues.append(f"category {category} exceeds cap {cap} {target_currency}")
    reserve = totals["likely"] * reserve_percent / Decimal("100")
    return BudgetSummary(
        currency=target_currency,
        low=totals["low"].quantize(Decimal("0.01")),
        likely=totals["likely"].quantize(Decimal("0.01")),
        high=totals["high"].quantize(Decimal("0.01")),
        reserve=reserve.quantize(Decimal("0.01")),
        likely_with_reserve=(totals["likely"] + reserve).quantize(Decimal("0.01")),
        by_category={key: value.quantize(Decimal("0.01")) for key, value in categories.items()},
        issues=issues,
        complete=not issues,
    )


class PlanScenario(BaseModel):
    scenario_id: str
    style: Literal["economy", "balanced", "comfort"]
    option_ids: list[str]
    cost: Decimal = Field(ge=0)
    duration_hours: Decimal = Field(gt=0)
    fatigue: int = Field(ge=0, le=100, description="Higher means more tiring")
    quality: int = Field(ge=0, le=100)


def compare_scenarios(scenarios: list[PlanScenario]) -> list[dict[str, str | int | list[str]]]:
    """Return stable comparison rows without hiding tradeoffs."""

    return [
        {
            "scenario_id": item.scenario_id,
            "style": item.style,
            "option_ids": item.option_ids,
            "cost": str(item.cost.quantize(Decimal("0.01"))),
            "duration_hours": str(item.duration_hours.quantize(Decimal("0.1"))),
            "fatigue": item.fatigue,
            "quality": item.quality,
        }
        for item in sorted(scenarios, key=lambda scenario: (scenario.cost, scenario.scenario_id))
    ]


class DecisionRecord(BaseModel):
    decision_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    topic: str = Field(min_length=1)
    chosen: str = Field(min_length=1)
    rejected: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(min_length=1)
    decided_at: datetime


def upsert_decision(
    decisions: list[DecisionRecord], decision: DecisionRecord
) -> list[DecisionRecord]:
    """Idempotently add or replace one decision while retaining stable order."""

    updated = [item for item in decisions if item.decision_id != decision.decision_id]
    updated.append(decision)
    return sorted(updated, key=lambda item: (item.decided_at, item.decision_id))
