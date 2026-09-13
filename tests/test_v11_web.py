"""Tests for the local FastAPI web interface and REST API endpoints."""

import json
from pathlib import Path
from starlette.testclient import TestClient
from ultimate_travel_agent.web.app import app

client = TestClient(app)


def test_web_health_endpoint() -> None:
    """Verify health endpoint confirms offline-first policy."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.1.0"
    assert data["mode"] == "offline-first-local"
    assert data["auto_booking_capability"] is False
    assert "Offline local planning mode" in data["disclaimer"]


def test_web_root_serves_html() -> None:
    """Verify root GET serves the single-page HTML interface."""
    res = client.get("/")
    assert res.status_code == 200
    assert "<!DOCTYPE html>" in res.text
    assert "Ultimate Travel Agent" in res.text
    assert "tab-overview" in res.text


def test_web_list_trips() -> None:
    """Verify listing available reference trips."""
    res = client.get("/api/trips")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    ids = {t["id"] for t in data}
    assert "trip-city-barcelona-001" in ids
    assert "trip-roadtrip-iceland-002" in ids


def test_web_get_example() -> None:
    """Verify retrieving example trips."""
    res_city = client.get("/api/examples/city-trip")
    assert res_city.status_code == 200
    assert res_city.json()["id"] == "trip-city-barcelona-001"

    res_road = client.get("/api/examples/road-trip")
    assert res_road.status_code == 200
    assert res_road.json()["id"] == "trip-roadtrip-iceland-002"


def test_web_create_trip_endpoint() -> None:
    """Verify local trip creation endpoint with custom form inputs."""
    payload = {
        "destination": "Rome",
        "country": "Italie",
        "start_date": "2026-10-01",
        "end_date": "2026-10-04",
        "travelers_count": 2,
        "traveler_profile": "couple",
        "budget_cap": 1400.0,
        "currency": "EUR",
        "interests": ["culture", "gastronomy", "history"],
        "accommodation_style": "hotel",
        "pacing": "balanced",
        "crowd_preference": "low-crowd",
        "constraints": "Végétarien",
    }
    res = client.post("/api/trips/create", json=payload)
    assert res.status_code == 200
    trip = res.json()
    assert trip["id"].startswith("trip-rome-")
    assert len(trip["travelers"]) == 2
    assert len(trip["destinations"]) == 1
    assert trip["destinations"][0]["name"] == "Rome"
    assert len(trip["activities"]) >= 3
    assert len(trip["transports"]) == 2
    assert len(trip["inter_city_routes"]) == 1


def test_web_validate_trip_endpoint() -> None:
    """Verify validation endpoint on city-trip example."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = client.post("/api/trips/validate", json=data)
    assert res.status_code == 200
    val = res.json()
    assert val["valid"] is True
    assert val["errors"] == []
    assert len(val["confirmed_data"]) >= 1
    assert "summary_stats" in val
    assert val["summary_stats"]["days"] == 3


def test_web_budget_endpoint() -> None:
    """Verify budget calculation endpoint."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = client.post("/api/trips/budget", json={"trip": data, "safety_buffer_pct": 15.0})
    assert res.status_code == 200
    b = res.json()
    assert b["safety_buffer_percentage"] == 15.0
    assert b["grand_total"] > b["total_estimated_cost"]


def test_web_plan_endpoint_nine_stages() -> None:
    """Verify multi-agent plan endpoint returning 9 stages and offline notice."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = client.post("/api/trips/plan", json=data)
    assert res.status_code == 200
    plan = res.json()
    assert plan["offline_banner"]["active"] is True
    assert plan["stages_count"] == 9
    assert len(plan["stages"]) == 9
    assert plan["stages"][0]["step_number"] == 1
    assert plan["stages"][0]["name"] == "Destination research"
    assert plan["stages"][8]["step_number"] == 9
    assert plan["stages"][8]["name"] == "Quality control"


def test_web_contingency_endpoint() -> None:
    """Verify contingency endpoint."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = client.post("/api/trips/contingency", json=data)
    assert res.status_code == 200
    c = res.json()
    assert len(c["pre_departure_checklist"]) >= 6
    assert len(c["document_verification_list"]) >= 4
    assert len(c["weather_contingency_plan"]) == 3


def test_web_export_endpoint() -> None:
    """Verify markdown export endpoint."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = client.post("/api/trips/export", json=data)
    assert res.status_code == 200
    text = res.text
    assert "# Dossier de Voyage" in text
    assert "Mode Planification Locale Hors-Ligne" in text
    assert "Offline local planning mode" in text
    assert "Plans B et Trousse de Préparation" in text


def test_web_route_evaluate_endpoint() -> None:
    """Verify evaluating route options via POST /api/trips/routes/evaluate."""
    route_payload = {
        "id": "route-test",
        "origin": "Paris",
        "destination": "Lyon",
        "options": [
            {
                "id": "opt-tgv",
                "origin": "Paris Gare de Lyon",
                "destination": "Lyon Part-Dieu",
                "mode": "train",
                "estimated_duration_minutes": 120,
                "transfers_count": 0,
                "estimated_cost": 45.0,
                "currency": "EUR",
                "comfort_level": 4,
                "carbon_footprint_kg": 5.0,
                "booking_required": True,
                "confidence_level": "official_verified",
                "status": "confirmed",
            },
            {
                "id": "opt-bus",
                "origin": "Paris Bercy",
                "destination": "Lyon Perrache",
                "mode": "bus",
                "estimated_duration_minutes": 330,
                "transfers_count": 0,
                "estimated_cost": 15.0,
                "currency": "EUR",
                "comfort_level": 2,
                "carbon_footprint_kg": 18.0,
                "booking_required": True,
                "confidence_level": "cross_checked",
                "status": "estimated",
            },
        ],
    }
    res = client.post("/api/trips/routes/evaluate", json=route_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["route_id"] == "route-test"
    assert "preferences_evaluations" in data
    evals = data["preferences_evaluations"]
    assert evals["cheapest"]["option_id"] == "opt-bus"
    assert evals["fastest"]["option_id"] == "opt-tgv"
    assert evals["most_eco_friendly"]["option_id"] == "opt-tgv"


def test_web_validation_six_categories() -> None:
    """Verify that validation endpoint returns all 6 required categories."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = client.post("/api/trips/validate", json=data)
    assert res.status_code == 200
    val = res.json()
    # 6 required categories: errors, warnings, missing_data, unverified_data, estimated_recommendations, confirmed_data
    assert "errors" in val
    assert "warnings" in val
    assert "missing_data" in val
    assert "unverified_data" in val
    assert "estimated_recommendations" in val
    assert "confirmed_data" in val
    assert len(val["confirmed_data"]) >= 1
    assert len(val["estimated_recommendations"]) >= 1


def test_web_integrations_endpoints() -> None:
    """Verify Provider Hub REST API endpoints in the web application."""
    # 1. List providers
    res = client.get("/api/integrations/providers")
    assert res.status_code == 200
    providers = res.json()
    assert len(providers) >= 15
    provider_names = {p["name"] for p in providers}
    assert "mock_flight" in provider_names
    assert "amadeus_flight" in provider_names

    # 2. Filter by category
    res_fl = client.get("/api/integrations/providers?category=flight")
    assert res_fl.status_code == 200
    assert all(p["category"] == "flight" for p in res_fl.json())

    # 3. Provider status - existing
    res_stat = client.get("/api/integrations/status/mock_flight")
    assert res_stat.status_code == 200
    status_data = res_stat.json()
    assert status_data["provider"] == "mock_flight"
    assert status_data["status"] == "healthy"

    # 4. Provider status - 404 for unknown provider
    res_404 = client.get("/api/integrations/status/nonexistent_provider_123")
    assert res_404.status_code == 404


