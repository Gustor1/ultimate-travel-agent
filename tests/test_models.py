"""Tests for Pydantic domain models and validation rules."""

import pytest
from pydantic import ValidationError

from ultimate_travel_agent.models import (
    Accommodation,
    AccommodationType,
    Activity,
    ActivityCategory,
    AgentResult,
    AgentStatus,
    Budget,
    ChecklistCategory,
    ChecklistItem,
    CrowdSensitivity,
    Destination,
    DaySchedule,
    ItineraryItem,
    PacingPreference,
    SourceReference,
    TransportMode,
    TransportSegment,
    Traveler,
    TravelerProfile,
    Trip,
    TripType,
    VerificationLevel,
)


def test_verification_levels() -> None:
    """Check all 6 required verification levels are defined."""
    levels = {
        VerificationLevel.OFFICIAL_VERIFIED,
        VerificationLevel.CROSS_CHECKED,
        VerificationLevel.COMMUNITY_RECOMMENDED,
        VerificationLevel.SOCIAL_DISCOVERY_ONLY,
        VerificationLevel.UNVERIFIED,
        VerificationLevel.OUTDATED,
    }
    assert len(levels) == 6
    assert VerificationLevel("official_verified") == VerificationLevel.OFFICIAL_VERIFIED


def test_traveler_creation() -> None:
    """Check traveler defaults and constraints."""
    traveler = Traveler(
        id="t-1",
        name="Marie Curie",
        profile=TravelerProfile.SOLO,
        pacing_preference=PacingPreference.PACKED,
        crowd_sensitivity=CrowdSensitivity.AVOID_CROWDS,
        dietary_restrictions=["vegetarian"],
    )
    assert traveler.id == "t-1"
    assert traveler.dietary_restrictions == ["vegetarian"]


def test_budget_calculation_and_buffer() -> None:
    """Check budget calculation with safety buffer."""
    dest = Destination(id="dest-1", name="Rome", country="Italy")
    traveler = Traveler(id="t-1", name="Paul")
    trans = TransportSegment(
        id="tr-1",
        origin="Paris",
        destination="Rome",
        mode=TransportMode.TRAIN,
        duration_minutes=600,
        estimated_cost=100.0,
    )
    acc = Accommodation(
        id="acc-1",
        name="Hotel Roma",
        destination_id="dest-1",
        neighborhood="Monti",
        cost_per_night=80.0,
        total_nights=2,
    )
    trip = Trip(
        id="trip-test-1",
        title="Rome Test",
        start_date="2026-05-10",
        end_date="2026-05-12",
        currency="EUR",
        travelers=[traveler],
        destinations=[dest],
        transports=[trans],
        accommodations=[acc],
    )

    budget = trip.calculate_budget(safety_buffer_pct=10.0)
    assert budget.currency == "EUR"
    # Transports = 100, Accommodations = 160, Activities = 0, Meals = 40*3 = 120, Misc = 15*3 = 45
    # Total = 100 + 160 + 0 + 120 + 45 = 425.0
    assert budget.total_estimated_cost == 425.0
    assert budget.safety_buffer_amount == 42.5
    assert budget.grand_total == 467.5


def test_trip_coherence_detection() -> None:
    """Check that incoherences in nights and dates are properly identified."""
    dest = Destination(id="dest-paris", name="Paris", country="France")
    traveler = Traveler(id="t-1", name="Sophie")
    acc = Accommodation(
        id="acc-1",
        name="Hotel Paris",
        destination_id="unknown-destination",  # Unknown destination!
        neighborhood="Marais",
        cost_per_night=100.0,
        total_nights=1,  # Only 1 night booked for a 3-night trip!
    )

    trip = Trip(
        id="trip-incoherent",
        title="Incoherent Trip",
        start_date="2026-06-01",
        end_date="2026-06-04",  # 3 nights
        currency="EUR",
        travelers=[traveler],
        destinations=[dest],
        accommodations=[acc],
    )

    issues = trip.validate_trip_coherence()
    assert len(issues) >= 2
    assert any("Nights mismatch" in issue for issue in issues)
    assert any("unknown destination 'unknown-destination'" in issue for issue in issues)


def test_agent_result_envelope() -> None:
    """Check AgentResult structure matches Phase 0 / Phase 1 contract."""
    result = AgentResult(
        agent="activity-curator",
        status=AgentStatus.COMPLETE,
        summary="3 cultural activities selected with crowd management advice.",
        findings=[{"activity_id": "act-1", "title": "Louvre Museum"}],
        assumptions=["Visitor prefers morning entries"],
        missing_information=["Temporary exhibition tickets not confirmed"],
        risks=["High summer heat inside glass pyramid"],
        sources=[
            SourceReference(
                title="Louvre Official",
                url="https://www.louvre.fr",
                source_type="official",
                verification_level=VerificationLevel.OFFICIAL_VERIFIED,
            )
        ],
        verification_level=VerificationLevel.OFFICIAL_VERIFIED,
    )
    assert result.agent == "activity-curator"
    assert result.status == AgentStatus.COMPLETE
    assert result.verification_level == VerificationLevel.OFFICIAL_VERIFIED
    assert len(result.sources) == 1


def test_stage_and_booking_models() -> None:
    """Test TripStage (étape) and BookingRequirement (réservation) models."""
    from ultimate_travel_agent.models import BookingRequirement, TripStage

    stage = TripStage(
        id="stage-1",
        destination_id="dest-bcn",
        order=1,
        title="Barcelona City Break",
        arrival_date="2026-10-15",
        departure_date="2026-10-17",
        nights=2,
    )
    assert stage.id == "stage-1"
    assert stage.nights == 2
    assert stage.order == 1

    booking = BookingRequirement(
        id="res-1",
        category="accommodation",
        title="Hotel Stay",
        status="needed",
        mandatory=True,
        reference_id="acc-1",
        estimated_cost=200.0,
        currency="EUR",
        official_booking_url="https://example.com/hotel",
        action_required="Book on hotel portal",
    )
    assert booking.id == "res-1"
    assert booking.mandatory is True
    assert booking.estimated_cost == 200.0


def test_transport_group_vs_passenger_pricing() -> None:
    """Test that car rental scales as a group/vehicle while train scales per passenger."""
    travelers = [Traveler(id="t1", name="Alice"), Traveler(id="t2", name="Bob")]
    dest = Destination(id="d1", name="Nice", country="France")

    train = TransportSegment(
        id="tr-train",
        origin="Paris",
        destination="Nice",
        mode=TransportMode.TRAIN,
        duration_minutes=340,
        estimated_cost=80.0,  # 80 * 2 = 160
    )
    assert train.effective_is_per_person is True

    car = TransportSegment(
        id="tr-car",
        origin="Nice Airport",
        destination="Nice Airport",
        mode=TransportMode.CAR_RENTAL,
        duration_minutes=1440,
        estimated_cost=250.0,  # 250 flat for the car
    )
    assert car.effective_is_per_person is False

    trip = Trip(
        id="trip-trans-test",
        title="Transport Test",
        start_date="2026-07-01",
        end_date="2026-07-03",
        currency="EUR",
        travelers=travelers,
        destinations=[dest],
        transports=[train, car],
    )

    budget = trip.calculate_budget()
    # train (80 * 2 = 160) + car (250 flat) = 410.0
    assert budget.categories["transport"].amount == 410.0


def test_edge_case_incoherent_dates_and_zero_nights() -> None:
    """Test date boundary edge cases (end before start, 0-night day trip with accommodation)."""
    traveler = Traveler(id="t1", name="Eve")
    dest = Destination(id="d1", name="Lyon", country="France")

    # Inverted dates: end_date precedes start_date
    inverted_trip = Trip(
        id="trip-inv",
        title="Inverted",
        start_date="2026-10-20",
        end_date="2026-10-15",
        travelers=[traveler],
        destinations=[dest],
    )
    assert inverted_trip.total_days == 0
    assert inverted_trip.total_nights == 0
    issues = inverted_trip.validate_trip_coherence()
    assert any("precedes start_date" in issue for issue in issues)

    # 0-night day trip with accommodations booked
    day_trip = Trip(
        id="trip-day",
        title="Day Trip",
        start_date="2026-10-15",
        end_date="2026-10-15",
        travelers=[traveler],
        destinations=[dest],
        accommodations=[
            Accommodation(
                id="acc-err",
                name="Hotel",
                destination_id="d1",
                neighborhood="Downtown",
                cost_per_night=120.0,
                total_nights=2,  # 2 nights booked for 0-night trip!
            )
        ],
    )
    assert day_trip.total_nights == 0
    assert day_trip.total_days == 1
    issues_day = day_trip.validate_trip_coherence()
    assert any("Nights mismatch" in issue for issue in issues_day)


def test_itinerary_coherence_checks() -> None:
    """Test itinerary destination, sequence, and item reference integrity checks."""
    traveler = Traveler(id="t1", name="Eve")
    dest = Destination(id="d1", name="Bordeaux", country="France")

    trip = Trip(
        id="trip-itin-test",
        title="Itin Test",
        start_date="2026-08-01",
        end_date="2026-08-02",  # 1 night, 2 days
        travelers=[traveler],
        destinations=[dest],
        itinerary=[
            DaySchedule(
                day_number=1,
                destination_id="unknown-dest",  # unknown destination!
                theme="Day 1",
                items=[
                    ItineraryItem(
                        time="10:00",
                        item_type="activity",
                        title="Wine Tour",
                        reference_id="act-nonexistent",  # unknown reference!
                    )
                ],
            ),
            DaySchedule(
                day_number=3,  # sequence error: expected 2!
                destination_id="d1",
                theme="Day 2",
                date="2026-09-01",  # out of date range!
            ),
        ],
    )

    issues = trip.validate_trip_coherence()
    assert any("unknown destination 'unknown-dest'" in issue for issue in issues)
    assert any("references unknown entity 'act-nonexistent'" in issue for issue in issues)
    assert any("sequence error" in issue for issue in issues)
    assert any("falls outside trip dates" in issue for issue in issues)
