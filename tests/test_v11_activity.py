"""Tests for V1.1 enriched Activity model."""

from ultimate_travel_agent.models import (
    Activity,
    ActivityCategory,
    DifficultyLevel,
    EnvironmentType,
    SourceReference,
    VerificationLevel,
)


def test_activity_full_v11_fields() -> None:
    """Test Activity model with all 26 specified dimensions."""
    act = Activity(
        id="act-test-monument-01",
        title="Musée d'Art Moderne et Contemporain",
        destination_id="dest-nice",
        category=ActivityCategory.CULTURE,
        description="Collection permanente et expositions temporaires.",
        country="France",
        region="Provence-Alpes-Côte d'Azur",
        city="Nice",
        neighborhood="Vieux-Nice",
        anecdote="Installé au cœur de la ville avec des terrasses surplombant la baie.",
        environment=EnvironmentType.INDOOR,
        difficulty_level=DifficultyLevel.EASY,
        accessibility="Totalement accessible PMR avec ascenseurs et rampes d'accès",
        duration_minutes=120,
        best_time_slot="10:00 - 12:00",
        opening_hours="10:00 - 18:00 tous les jours sauf le lundi",
        estimated_cost=15.0,
        currency="EUR",
        access_method="Tramway Ligne 1 arrêt Garibaldi puis 3 min de marche",
        transit_duration_minutes=12,
        transit_cost=1.70,
        advance_booking_required=True,
        official_booking_url="https://www.mamac-nice.org",
        crowd_level="medium",
        quiet_slot_advice="Venir dès l'ouverture à 10h00",
        crowd_avoidance_strategy="Entrée réservée aux détenteurs de e-billet horodaté",
        indoor_contingency=True,
        weather_alternative="Visite de l'auditorium et des galeries abritées",
        closure_alternative="Galerie des Ponchettes à 400 mètres",
        verification_level=VerificationLevel.OFFICIAL_VERIFIED,
        sources=[
            SourceReference(
                title="Billetterie Officielle MAMAC",
                url="https://www.mamac-nice.org",
                source_type="official",
                verification_level=VerificationLevel.OFFICIAL_VERIFIED,
            )
        ],
    )

    assert act.id == "act-test-monument-01"
    assert act.country == "France"
    assert act.region == "Provence-Alpes-Côte d'Azur"
    assert act.city == "Nice"
    assert act.neighborhood == "Vieux-Nice"
    assert act.anecdote is not None
    assert act.environment == EnvironmentType.INDOOR
    assert act.difficulty_level == DifficultyLevel.EASY
    assert "PMR" in act.accessibility
    assert act.duration_minutes == 120
    assert act.best_time_slot == "10:00 - 12:00"
    assert act.opening_hours is not None
    assert act.estimated_cost == 15.0
    assert act.transit_duration_minutes == 12
    assert act.transit_cost == 1.70
    assert act.advance_booking_required is True
    assert act.official_booking_url == "https://www.mamac-nice.org"
    assert act.crowd_level == "medium"
    assert act.effective_crowd_strategy == "Entrée réservée aux détenteurs de e-billet horodaté"
    assert act.indoor_contingency is True
    assert act.weather_alternative is not None
    assert act.closure_alternative is not None
    assert act.verification_level == VerificationLevel.OFFICIAL_VERIFIED
    assert len(act.sources) == 1


def test_activity_minimal_backwards_compatibility() -> None:
    """Test that Activity initializes with only minimal v1.0 required fields."""
    act = Activity(
        id="act-minimal",
        title="Tour Guidé",
        destination_id="dest-01",
        description="Visite classique.",
    )
    assert act.id == "act-minimal"
    assert act.category == ActivityCategory.CULTURE
    assert act.duration_minutes == 90
    assert act.estimated_cost == 0.0
    assert act.currency == "EUR"
    assert act.country is None
    assert act.environment == EnvironmentType.INDOOR
    assert act.difficulty_level == DifficultyLevel.EASY
    assert act.advance_booking_required is False
    assert act.indoor_contingency is False
    assert act.verification_level == VerificationLevel.UNVERIFIED
    assert act.sources == []


def test_activity_effective_crowd_strategy_fallback() -> None:
    """Test effective_crowd_strategy property fallback to quiet_slot_advice."""
    act = Activity(
        id="act-strategy-fallback",
        title="Parc Floral",
        destination_id="dest-01",
        description="Jardin public.",
        quiet_slot_advice="Matin avant 10h",
        crowd_avoidance_strategy=None,
    )
    assert act.effective_crowd_strategy == "Matin avant 10h"


def test_activity_french_aliases_normalization() -> None:
    """Test that French category, environment, and difficulty names normalize smoothly."""
    act1 = Activity(
        id="act-fr-1",
        title="Château Médiéval",
        destination_id="dest-01",
        description="Visite historique.",
        category="histoire",
        environment="extérieur",
        difficulty_level="facile",
    )
    assert act1.category == ActivityCategory.HISTORY
    assert act1.environment == EnvironmentType.OUTDOOR
    assert act1.difficulty_level == DifficultyLevel.EASY

    act2 = Activity(
        id="act-fr-2",
        title="Spa & Thalasso",
        destination_id="dest-01",
        description="Bains chauds relaxants.",
        category="détente",
        environment="intérieur",
        difficulty_level="moyen",
    )
    assert act2.category == ActivityCategory.RELAXATION
    assert act2.environment == EnvironmentType.INDOOR
    assert act2.difficulty_level == DifficultyLevel.MODERATE
