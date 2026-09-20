from decimal import Decimal

import pytest

from ultimate_travel_agent.adaptive import (
    ActivityCandidate,
    AdaptiveDayRequest,
    build_adaptive_day,
)


def _activity(
    activity_id: str,
    priority: str,
    environment: str,
    energy: str,
    minutes: int,
    walking: str,
) -> ActivityCandidate:
    return ActivityCandidate.model_validate(
        {
            "activity_id": activity_id,
            "title": activity_id,
            "priority": priority,
            "environment": environment,
            "energy": energy,
            "duration_minutes": minutes,
            "walking_km": walking,
            "source_ids": [f"source-{activity_id}"],
        }
    )


def test_adaptive_day_builds_four_distinct_variants() -> None:
    activities = [
        _activity("museum", "essential", "indoor", "low", 120, "1"),
        _activity("park", "preferred", "outdoor", "medium", 120, "3"),
        _activity("tower", "preferred", "indoor", "high", 90, "1"),
        _activity("cafe", "optional", "indoor", "low", 60, "0.5"),
    ]
    plan = build_adaptive_day(
        AdaptiveDayRequest(day="2027-05-10", maximum_activity_minutes=360), activities
    )
    variants = {variant.kind: variant for variant in plan.variants}
    assert plan.complete
    assert variants["essential"].activity_ids == ["museum"]
    assert "park" not in variants["rain"].activity_ids
    assert "tower" not in variants["low_energy"].activity_ids
    assert variants["balanced"].walking_km == Decimal("5.00")


def test_adaptive_day_never_silently_drops_essential_constraint_conflict() -> None:
    plan = build_adaptive_day(
        AdaptiveDayRequest(day="2027-05-10", maximum_activity_minutes=60),
        [_activity("hike", "essential", "outdoor", "high", 180, "12")],
    )
    assert not plan.complete
    assert all("hike" in variant.activity_ids for variant in plan.variants)
    assert any("conflicts with rain" in issue for issue in plan.issues)


def test_adaptive_day_requires_unique_ids_and_an_essential_activity() -> None:
    optional = _activity("cafe", "optional", "indoor", "low", 60, "0")
    request = AdaptiveDayRequest(day="2027-05-10")
    with pytest.raises(ValueError, match="essential"):
        build_adaptive_day(request, [optional])
    essential = optional.model_copy(update={"priority": "essential"})
    with pytest.raises(ValueError, match="unique"):
        build_adaptive_day(request, [essential, essential])
