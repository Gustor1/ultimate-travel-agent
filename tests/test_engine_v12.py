"""Tests for multi-agent engine with Provider Hub integration and quality gates."""

import json
from ultimate_travel_agent.engine.orchestrator import TravelOrchestrationEngine
from ultimate_travel_agent.models import (
    Activity,
    AgentStatus,
    Destination,
    TransportMode,
    TransportSegment,
    Traveler,
    Trip,
    VerificationLevel,
)


def test_engine_v12_on_city_trip() -> None:
    """Test full multi-agent pipeline on city-trip example with Provider Hub."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    trip = Trip.model_validate(data)
    engine = TravelOrchestrationEngine(mode="offline")
    results = engine.execute_full_pipeline(trip)

    # 1. destination-researcher includes guide source and climate profile
    assert len(results["destination-researcher"].sources) >= 1
    assert "Provider Hub" in results["destination-researcher"].summary

    # 2. transport-planner mentions door-to-door buffers and provider mode
    assert any("Door-to-door" in a for a in results["transport-planner"].assumptions)

    # 3. accommodation-researcher isolates reviews from booking
    assert any("Review sentiment isolated" in a for a in results["accommodation-researcher"].assumptions)

    # 4. activity-curator models rain alternatives and crowd avoidance
    assert any("Indoor rain alternatives" in a for a in results["activity-curator"].assumptions)

    # 5. local-discovery-agent tags social discovery as social_discovery_only
    assert results["local-discovery-agent"].verification_level == VerificationLevel.SOCIAL_DISCOVERY_ONLY

    # 6. budget-analyst validates currency reference date
    findings = results["budget-analyst"].findings
    assert any("currency_reference_date" in str(f) for f in findings)

    # 7. quality-controller passes for valid trip
    assert results["quality-controller"].status == AgentStatus.COMPLETE


def test_quality_controller_blocks_fake_confirmed_social_items() -> None:
    """Test that QC blocks recommendations falsely marked confirmed when from social discovery."""
    trip = Trip(
        id="trip-fake-confirmed",
        title="Fake Confirmed Social Trip",
        start_date="2026-09-01",
        end_date="2026-09-02",
        currency="EUR",
        travelers=[Traveler(id="t1", name="Alice")],
        destinations=[Destination(id="d1", name="Rome", country="Italy")],
        activities=[
            Activity(
                id="act-social-fake",
                title="Viral Rooftop",
                destination_id="d1",
                description="Social spot",
                verification_level=VerificationLevel.SOCIAL_DISCOVERY_ONLY,
                price_status="confirmed",  # INVALID: social discovery cannot be confirmed!
            )
        ],
    )

    engine = TravelOrchestrationEngine(mode="offline")
    results = engine.execute_full_pipeline(trip)
    assert results["quality-controller"].status == AgentStatus.BLOCKED
    assert any("social discovery cannot be presented as confirmed" in r for r in results["quality-controller"].risks)
    assert results["travel-orchestrator"].status == AgentStatus.BLOCKED


def test_engine_live_mode_flags_unconfigured_providers() -> None:
    """Test that running orchestrator in live mode flags unconfigured providers."""
    with open("examples/road-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    trip = Trip.model_validate(data)
    engine = TravelOrchestrationEngine(mode="live")
    results = engine.execute_full_pipeline(trip)

    # Quality controller should have an advisory notice about unconfigured providers
    qc_risks = results["quality-controller"].risks
    assert any("Live mode alert" in r for r in qc_risks)
