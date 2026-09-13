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
