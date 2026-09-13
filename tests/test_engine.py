"""Tests for the multi-agent orchestration engine and reporting."""

import json
from pathlib import Path
from ultimate_travel_agent.engine.orchestrator import TravelOrchestrationEngine
from ultimate_travel_agent.models import AgentStatus, Trip
from ultimate_travel_agent.reporter import generate_markdown_report


def test_orchestration_engine_full_pipeline() -> None:
    """Test full 5-wave pipeline execution on city-trip example."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    trip = Trip.model_validate(data)
    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)

    # Check that all 11 agents or waves have registered results
    assert "destination-researcher" in results
    assert "transport-planner" in results
    assert "accommodation-researcher" in results
    assert "activity-curator" in results
    assert "local-discovery-agent" in results
    assert "travel-preparation-agent" in results
    assert "budget-analyst" in results
    assert "itinerary-optimizer" in results
    assert "quality-controller" in results
    assert "mcp-skill-auditor" in results
    assert "travel-orchestrator" in results

    # All should be complete for a valid trip
    for name, res in results.items():
        assert res.status == AgentStatus.COMPLETE, f"Agent {name} failed: {res.risks}"

    # Generate report
    report = generate_markdown_report(trip, results)
    assert "# Dossier de Voyage" in report
    assert "Barcelone" in report
    assert "Sagrada Família" in report
    assert "Bilan d'Exécution Multi-Agents" in report

    # Check sources were preserved into agent results
    assert len(results["transport-planner"].sources) >= 1
    assert len(results["activity-curator"].sources) >= 1


def test_orchestrator_verification_level_fidelity() -> None:
    """Check that orchestrator reflects actual unverified items instead of masking them."""
    from ultimate_travel_agent.models import Activity, Destination, Traveler, VerificationLevel

    trip = Trip(
        id="trip-unverified-test",
        title="Unverified Test",
        start_date="2026-09-01",
        end_date="2026-09-02",
        currency="EUR",
        travelers=[Traveler(id="t1", name="Alice")],
        destinations=[Destination(id="d1", name="Rome", country="Italy")],
        activities=[
            Activity(
                id="act-unv",
                title="Rumored Bar",
                destination_id="d1",
                description="Unconfirmed venue",
                verification_level=VerificationLevel.UNVERIFIED,
            )
        ],
    )

    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)
    assert results["activity-curator"].verification_level == VerificationLevel.UNVERIFIED


def test_security_auditor_blocks_dangerous_urls() -> None:
    """Check that mcp-skill-auditor detects and blocks malicious URLs in lodging and activities."""
    from ultimate_travel_agent.models import Accommodation, Destination, Traveler

    trip = Trip(
        id="trip-malicious-url",
        title="Malicious URL Trip",
        start_date="2026-09-01",
        end_date="2026-09-02",
        currency="EUR",
        travelers=[Traveler(id="t1", name="Alice")],
        destinations=[Destination(id="d1", name="Rome", country="Italy")],
        accommodations=[
            Accommodation(
                id="acc-evil",
                name="Phishing Hotel",
                destination_id="d1",
                neighborhood="Center",
                cost_per_night=90.0,
                total_nights=1,
                official_booking_url="javascript:alert(document.cookie)",  # Malicious scheme!
            )
        ],
    )

    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)
    assert results["mcp-skill-auditor"].status == AgentStatus.BLOCKED
    assert any("Suspicious URL" in risk for risk in results["mcp-skill-auditor"].risks)
    assert results["travel-orchestrator"].status == AgentStatus.BLOCKED


def test_budget_overrun_and_qc_warning() -> None:
    """Check that budget cap overruns are recorded by budget-analyst and quality-controller."""
    from ultimate_travel_agent.models import Destination, TransportMode, TransportSegment, Traveler

    trip = Trip(
        id="trip-overbudget",
        title="Over Budget Trip",
        start_date="2026-09-01",
        end_date="2026-09-02",
        currency="EUR",
        budget_cap=50.0,  # Unrealistic low cap
        travelers=[Traveler(id="t1", name="Alice")],
        destinations=[Destination(id="d1", name="Rome", country="Italy")],
        transports=[
            TransportSegment(
                id="tr-1",
                origin="Paris",
                destination="Rome",
                mode=TransportMode.FLIGHT,
                duration_minutes=120,
                estimated_cost=300.0,
            )
        ],
    )

    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)
    assert results["budget-analyst"].status == AgentStatus.PARTIAL
    assert any("Budget cap exceeded" in r for r in results["budget-analyst"].risks)
    assert any("Budget cap exceeded" in r for r in results["quality-controller"].risks)
