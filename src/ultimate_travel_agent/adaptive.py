"""Deterministic essential, balanced, rain, and low-energy day variants."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActivityCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activity_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    title: str = Field(min_length=1)
    duration_minutes: int = Field(gt=0, le=720)
    walking_km: Decimal = Field(default=Decimal("0"), ge=0)
    environment: Literal["indoor", "outdoor", "mixed"]
    energy: Literal["low", "medium", "high"]
    priority: Literal["essential", "preferred", "optional"]
    source_ids: list[str] = Field(min_length=1)

    @field_validator("walking_km", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("walking distances must use decimal strings or integers")
        return value


class AdaptiveDayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: date
    maximum_activity_minutes: int = Field(default=480, ge=60, le=960)
    maximum_walking_km: Decimal = Field(default=Decimal("10"), gt=0)

    @field_validator("maximum_walking_km", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("walking limits must use decimal strings or integers")
        return value


class DayVariant(BaseModel):
    kind: Literal["essential", "balanced", "rain", "low_energy"]
    activity_ids: list[str]
    total_minutes: int
    walking_km: Decimal
    omitted_activity_ids: list[str]
    issues: list[str]


class AdaptiveDayPlan(BaseModel):
    day: date
    variants: list[DayVariant]
    complete: bool
    issues: list[str]


def _select_variant(
    kind: Literal["essential", "balanced", "rain", "low_energy"],
    activities: list[ActivityCandidate],
    request: AdaptiveDayRequest,
) -> DayVariant:
    limit_minutes = request.maximum_activity_minutes
    if kind == "essential":
        allowed_priorities = {"essential"}
    else:
        allowed_priorities = {"essential", "preferred", "optional"}
    if kind == "low_energy":
        limit_minutes = max(60, request.maximum_activity_minutes * 3 // 5)

    ranked = sorted(
        activities,
        key=lambda item: (
            {"essential": 0, "preferred": 1, "optional": 2}[item.priority],
            item.activity_id,
        ),
    )
    selected: list[ActivityCandidate] = []
    issues: list[str] = []
    total_minutes = 0
    total_walking = Decimal("0")
    for item in ranked:
        if item.priority not in allowed_priorities:
            continue
        unsuitable = (kind == "rain" and item.environment == "outdoor") or (
            kind == "low_energy" and item.energy == "high"
        )
        if unsuitable and item.priority != "essential":
            continue
        if unsuitable:
            issues.append(f"essential activity {item.activity_id} conflicts with {kind} variant")
        would_exceed = (
            total_minutes + item.duration_minutes > limit_minutes
            or total_walking + item.walking_km > request.maximum_walking_km
        )
        if would_exceed and item.priority != "essential":
            continue
        selected.append(item)
        total_minutes += item.duration_minutes
        total_walking += item.walking_km
        if would_exceed:
            issues.append(f"essential activity {item.activity_id} exceeds day limits")
    selected_ids = [item.activity_id for item in selected]
    return DayVariant(
        kind=kind,
        activity_ids=selected_ids,
        total_minutes=total_minutes,
        walking_km=total_walking.quantize(Decimal("0.01")),
        omitted_activity_ids=[
            item.activity_id for item in activities if item.activity_id not in selected_ids
        ],
        issues=issues,
    )


def build_adaptive_day(
    request: AdaptiveDayRequest, activities: list[ActivityCandidate]
) -> AdaptiveDayPlan:
    """Build four explainable variants while preserving essential activities."""

    identifiers = [item.activity_id for item in activities]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("activity_id values must be unique")
    if not any(item.priority == "essential" for item in activities):
        raise ValueError("adaptive day requires at least one essential activity")
    variants = [
        _select_variant(kind, activities, request)
        for kind in ("essential", "balanced", "rain", "low_energy")
    ]
    issues = [f"{variant.kind}: {issue}" for variant in variants for issue in variant.issues]
    return AdaptiveDayPlan(
        day=request.day,
        variants=variants,
        complete=not issues,
        issues=issues,
    )
