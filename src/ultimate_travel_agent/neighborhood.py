"""Evidence-backed neighborhood quality scoring for accommodation decisions."""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

NeighborhoodMetric = Literal[
    "night_safety",
    "noise_comfort",
    "metro_tram_access",
    "late_service",
    "dining",
    "groceries",
    "pharmacy",
    "tourist_balance",
    "accessibility",
]

_WEIGHTS: dict[NeighborhoodMetric, Decimal] = {
    "night_safety": Decimal("0.25"),
    "noise_comfort": Decimal("0.10"),
    "metro_tram_access": Decimal("0.20"),
    "late_service": Decimal("0.10"),
    "dining": Decimal("0.10"),
    "groceries": Decimal("0.07"),
    "pharmacy": Decimal("0.07"),
    "tourist_balance": Decimal("0.04"),
    "accessibility": Decimal("0.07"),
}


class NeighborhoodEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric: NeighborhoodMetric
    score: int = Field(ge=0, le=100, description="100 is always best for the traveler")
    summary: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    verified_at: date


class NeighborhoodProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    neighborhood_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    name: str = Field(min_length=1)
    city: str = Field(min_length=1)
    evidence: list[NeighborhoodEvidence]


class NeighborhoodRequirements(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minimum_night_safety: int = Field(default=60, ge=0, le=100)
    minimum_metro_tram_access: int = Field(default=60, ge=0, le=100)
    minimum_accessibility: int | None = Field(default=None, ge=0, le=100)
    maximum_evidence_age_days: int = Field(default=180, ge=1, le=730)


class NeighborhoodAssessment(BaseModel):
    neighborhood_id: str
    score: Decimal
    breakdown: dict[NeighborhoodMetric, Decimal]
    issues: list[str]
    warnings: list[str]
    complete: bool


def assess_neighborhood(
    profile: NeighborhoodProfile,
    requirements: NeighborhoodRequirements | None = None,
    *,
    as_of: date | None = None,
) -> NeighborhoodAssessment:
    """Score a neighborhood only when every required evidence dimension exists."""

    active = requirements or NeighborhoodRequirements()
    current = as_of or date.today()
    evidence_map = {item.metric: item for item in profile.evidence}
    if len(evidence_map) != len(profile.evidence):
        raise ValueError("neighborhood metrics must be unique")
    missing = [metric for metric in _WEIGHTS if metric not in evidence_map]
    issues = [f"missing neighborhood metric: {metric}" for metric in missing]
    warnings: list[str] = []
    breakdown: dict[NeighborhoodMetric, Decimal] = {}
    for metric, weight in _WEIGHTS.items():
        item = evidence_map.get(metric)
        if item is None:
            continue
        age = (current - item.verified_at).days
        if age < 0:
            issues.append(f"neighborhood metric {metric} is dated in the future")
        elif age > active.maximum_evidence_age_days:
            warnings.append(f"neighborhood metric {metric} is stale ({age} days)")
        breakdown[metric] = (Decimal(item.score) * weight).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    safety = evidence_map.get("night_safety")
    if safety is not None and safety.score < active.minimum_night_safety:
        issues.append("night safety is below the traveler minimum")
    transit = evidence_map.get("metro_tram_access")
    if transit is not None and transit.score < active.minimum_metro_tram_access:
        issues.append("metro/tram access is below the traveler minimum")
    accessibility = evidence_map.get("accessibility")
    if (
        active.minimum_accessibility is not None
        and accessibility is not None
        and accessibility.score < active.minimum_accessibility
    ):
        issues.append("neighborhood accessibility is below the traveler minimum")
    total = sum(breakdown.values(), Decimal("0")).quantize(Decimal("0.01"))
    return NeighborhoodAssessment(
        neighborhood_id=profile.neighborhood_id,
        score=total,
        breakdown=breakdown,
        issues=issues,
        warnings=warnings,
        complete=not issues and not missing,
    )
