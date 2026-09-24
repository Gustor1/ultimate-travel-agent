"""Focused contract checks for an activity-led trip with provisional flights."""

from pathlib import Path

AGENTS = Path(__file__).resolve().parents[1] / ".agents"


def _skill(name: str) -> str:
    return (AGENTS / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def test_full_trip_can_progress_without_live_airfare() -> None:
    orchestrator = _skill("travel-orchestrator")
    workflow = (AGENTS / "workflows" / "plan-complete-trip.md").read_text(
        encoding="utf-8"
    )

    assert "Use `flight-search` when the user requests fares or flight choice controls dates/route" in orchestrator
    assert "keep air costs and schedules unverified" in orchestrator
    assert "candidate dates, which may come from the user's brief without `flight-search`" in workflow
    assert "keep booking readiness false" in workflow


def test_experiences_food_and_photos_are_sourced_and_fit_the_day() -> None:
    activities = _skill("activity-curator")
    local = _skill("local-discovery")
    itinerary = _skill("itinerary-builder")
    quality = _skill("travel-quality-control")

    assert "anchor for each full sightseeing day" in activities
    assert "regional dish" in local
    assert "photo opportunity near the planned route" in local
    assert "photography rules" in local
    assert "source type/authority" in local
    assert "Fit sourced local specialties and photo moments" in itinerary
    assert "Audit food/photo detours" in quality
