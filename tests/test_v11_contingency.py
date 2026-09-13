"""Tests for contingency planning, Plan B, and preparation generators."""

import json
from pathlib import Path
from ultimate_travel_agent.engine.contingency import generate_contingency_dossier
from ultimate_travel_agent.models import Trip


def test_generate_contingency_dossier_city_trip() -> None:
    """Verify contingency dossier generated for reference city-trip."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    trip = Trip.model_validate(data)

    contingency = generate_contingency_dossier(trip)
    assert contingency.trip_id == trip.id

    # 1. Pre-departure checklist
    assert len(contingency.pre_departure_checklist) >= 6
    titles = [item["title"] for item in contingency.pre_departure_checklist]
    assert any("passeport" in t.lower() for t in titles)
    assert any("assurance" in t.lower() for t in titles)

    # 2. Booking checklist
    assert len(contingency.booking_checklist) >= 4
    for b in contingency.booking_checklist:
        assert "mandatory" in b
        assert "timing_advice" in b

    # 3. Document verification list
    assert len(contingency.document_verification_list) >= 4
    for doc in contingency.document_verification_list:
        assert doc["status"] == "Requires official source verification."

    # 4. Weather contingency plan
    assert len(contingency.weather_contingency_plan) == trip.total_days
    for w in contingency.weather_contingency_plan:
        assert "general_contingency_notes" in w

    # 5. Activity closure plan
    assert len(contingency.activity_closure_plan) == len(trip.activities)
    for cl in contingency.activity_closure_plan:
        assert "recommended_alternative" in cl
        assert len(cl["recommended_alternative"]) > 0

    # 6. Pre-booking confirmation items
    assert len(contingency.pre_booking_confirmation_items) >= 3
    for conf in contingency.pre_booking_confirmation_items:
        assert "risk_if_unconfirmed" in conf

    # 7. Generic emergency summary
    em = contingency.generic_emergency_summary
    assert "Requires official source verification." in em["emergency_dispatch_reminder"]
    assert "Requires official source verification." in em["consular_support_reminder"]
    assert "Requires official source verification." in em["medical_assistance_reminder"]
    assert "zero_fabrication_guarantee" in em
    assert len(em["incident_procedure"]) >= 4
