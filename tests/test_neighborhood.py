from datetime import date
from decimal import Decimal

from ultimate_travel_agent.neighborhood import (
    NeighborhoodEvidence,
    NeighborhoodProfile,
    NeighborhoodRequirements,
    assess_neighborhood,
)


def _profile(**score_updates: int) -> NeighborhoodProfile:
    defaults = {
        "night_safety": 80,
        "noise_comfort": 70,
        "metro_tram_access": 90,
        "late_service": 75,
        "dining": 85,
        "groceries": 80,
        "pharmacy": 80,
        "tourist_balance": 60,
        "accessibility": 70,
    }
    defaults.update(score_updates)
    return NeighborhoodProfile(
        neighborhood_id="bastille",
        name="Bastille",
        city="Paris",
        evidence=[
            NeighborhoodEvidence(
                metric=metric,
                score=score,
                summary=metric,
                source_ids=[f"source-{metric}"],
                verified_at="2026-09-01",
            )
            for metric, score in defaults.items()
        ],
    )


def test_neighborhood_score_uses_all_evidence_dimensions() -> None:
    result = assess_neighborhood(_profile(), as_of=date(2026, 9, 20))
    assert result.complete
    assert result.score == Decimal("79.50")
    assert set(result.breakdown) == {
        "night_safety",
        "noise_comfort",
        "metro_tram_access",
        "late_service",
        "dining",
        "groceries",
        "pharmacy",
        "tourist_balance",
        "accessibility",
    }


def test_neighborhood_hard_minimums_block_hotel_recommendation() -> None:
    result = assess_neighborhood(
        _profile(night_safety=40, metro_tram_access=50, accessibility=30),
        NeighborhoodRequirements(minimum_accessibility=60),
        as_of=date(2026, 9, 20),
    )
    assert not result.complete
    assert len(result.issues) == 3


def test_neighborhood_missing_and_stale_evidence_is_visible() -> None:
    profile = _profile()
    profile.evidence = [
        item.model_copy(update={"verified_at": date(2025, 1, 1)})
        for item in profile.evidence
        if item.metric != "pharmacy"
    ]
    result = assess_neighborhood(profile, as_of=date(2026, 9, 20))
    assert not result.complete
    assert "missing neighborhood metric: pharmacy" in result.issues
    assert len(result.warnings) == 8
