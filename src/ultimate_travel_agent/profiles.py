"""Privacy-minimal persistent traveler profiles."""

from __future__ import annotations

import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class TravelerProfile(BaseModel):
    """Reusable planning preferences without identity or travel-document data."""

    model_config = ConfigDict(extra="forbid")

    profile_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    travelers: int = Field(default=1, ge=1, le=30)
    pacing: Literal["relaxed", "balanced", "packed"] = "balanced"
    mobility: Literal["standard", "limited", "wheelchair"] = "standard"
    daily_walking_km: Decimal = Field(default=Decimal("8"), ge=0, le=50)
    max_daily_activity_hours: Decimal = Field(default=Decimal("8"), gt=0, le=18)
    max_layover_minutes: int = Field(default=240, ge=30, le=1440)
    crowd_tolerance: int = Field(default=50, ge=0, le=100)
    heat_tolerance: int = Field(default=50, ge=0, le=100)
    interests: list[str] = Field(default_factory=list)
    dietary_requirements: list[str] = Field(default_factory=list)
    accessibility_requirements: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    budget_currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    category_budgets: dict[str, Decimal] = Field(default_factory=dict)

    @field_validator(
        "daily_walking_km", "max_daily_activity_hours", "category_budgets", mode="before"
    )
    @classmethod
    def reject_binary_float(cls, value: Any) -> Any:
        if isinstance(value, float):
            raise ValueError("decimal profile values must use strings or integers")
        if isinstance(value, dict) and any(isinstance(item, float) for item in value.values()):
            raise ValueError("category budgets must use decimal strings or integers")
        return value


class ProfileStoreError(ValueError):
    """Raised when a profile file is missing, malformed, or unsafe to overwrite."""


def load_profile(path: Path) -> TravelerProfile:
    """Load one local profile from JSON."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ProfileStoreError("profile must contain a JSON object")
        return TravelerProfile.model_validate(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
        raise ProfileStoreError(f"invalid traveler profile: {exc}") from exc


def save_profile(profile: TravelerProfile, path: Path) -> Path:
    """Atomically persist validated non-sensitive preferences."""

    destination = path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=destination.parent, delete=False, suffix=".tmp"
        ) as handle:
            handle.write(profile.model_dump_json(indent=2))
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        os.replace(temporary_name, destination)
    finally:
        if temporary_name is not None:
            temporary = Path(temporary_name)
            if temporary.exists():
                temporary.unlink()
    return destination


def merge_profile(profile: TravelerProfile, overrides: dict[str, Any]) -> TravelerProfile:
    """Return a validated copy with trip-specific overrides; original stays unchanged."""

    merged = profile.model_dump(mode="json")
    merged.update(overrides)
    return TravelerProfile.model_validate(merged)
