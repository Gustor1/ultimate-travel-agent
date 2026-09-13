"""Tests for Phase 10 MCP keyless tools, FastAPI endpoints, and subagent orchestration."""

import json
from starlette.testclient import TestClient
import pytest

from ultimate_travel_agent.engine.orchestrator import TravelOrchestrationEngine
from ultimate_travel_agent.mcp import tools
from ultimate_travel_agent.models import Destination, Traveler, Trip, VerificationLevel
from ultimate_travel_agent.web.app import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


# ---------------------------------------------------------------------------
# MCP Tools Tests
# ---------------------------------------------------------------------------

def test_mcp_get_keyless_provider_status() -> None:
    """Test get_keyless_provider_status tool audits all 5 providers."""
    status = tools.get_keyless_provider_status()
    assert status["status"] == "healthy"
    assert status["total_keyless_providers"] == 5
    providers = {p["provider"]: p for p in status["providers"]}
    assert "open_meteo" in providers
    assert "ecb_currency" in providers
    assert "wikivoyage" in providers
    assert "nominatim" in providers
    assert "osrm" in providers

    assert providers["nominatim"]["decision"] == "limited"
    assert providers["osrm"]["decision"] == "experimental"
    assert providers["open_meteo"]["decision"] == "approved"
    assert providers["ecb_currency"]["decision"] == "approved"
    assert providers["wikivoyage"]["decision"] == "approved"


def test_mcp_geocode_destination_offline_and_live(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test geocode_destination tool in offline catalog mode and mocked live mode."""
    # Offline
    res_off = tools.geocode_destination("Paris", mode="offline")
    assert res_off["provider"] == "mock_maps"
    assert res_off["destination"] == "Paris"
    assert "latitude" in res_off
    assert "longitude" in res_off
    assert res_off["requires_booking_verification"] is False

    # Live unconfigured -> returns clean configuration error
    monkeypatch.setenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "false")
    res_live_unconf = tools.geocode_destination("Paris", mode="live")
    assert res_live_unconf["status"] == "error"
    assert "ProviderConfigurationError" in res_live_unconf["error_type"]


def test_mcp_weather_forecast_and_activity_advice() -> None:
    """Test get_weather_forecast and get_weather_activity_advice tools."""
    fc = tools.get_weather_forecast("Paris", days=5, mode="offline")
    assert fc["provider"] == "open_meteo"
    assert "attribution" in fc

    advice = tools.get_weather_activity_advice("Paris", date="2026-10-15", planned_activity="Walking tour", mode="offline")
    assert "rain_risk_detected" in advice
    assert "activity_advice" in advice
    assert "recommended_indoor_backup" in advice
    assert advice["requires_booking_verification"] is False


def test_mcp_currency_tools() -> None:
    """Test get_exchange_rates and convert_currency_live tools."""
    rates = tools.get_exchange_rates(base_currency="EUR", symbols=["USD", "GBP"], mode="offline")
    assert rates["base_currency"] == "EUR"
    assert "rates" in rates
    assert "USD" in rates["rates"]
    assert "advisory" in rates
    assert "1.5%" in rates["advisory"]

    converted = tools.convert_currency_live(amount=150.0, from_currency="EUR", to_currency="USD", mode="offline")
    assert converted["provider"] == "ecb_currency"
    assert len(converted["items"]) == 1
    assert converted["items"][0]["price"] is not None


def test_mcp_wikivoyage_tools() -> None:
    """Test search_wikivoyage_destination and get_wikivoyage_summary tools."""
    search_res = tools.search_wikivoyage_destination("Reykjavik", mode="offline")
    assert search_res["query"] == "Reykjavik"
    assert len(search_res["articles"]) >= 1
    assert "CC BY-SA 4.0" in search_res["attribution"]

    summary = tools.get_wikivoyage_summary("Reykjavik", mode="offline")
    assert summary["provider"] == "wikivoyage"
    assert len(summary["items"]) >= 1


def test_mcp_limited_route_options_tool() -> None:
    """Test get_limited_route_options tool under offline and disabled live modes."""
    # Offline mode succeeds with mock route
    route_off = tools.get_limited_route_options("Paris", "Lyon", mode="offline")
    assert route_off["provider"] == "osrm"
    assert len(route_off["items"]) >= 1

    # Live mode disabled by default returns structured configuration error
    route_live = tools.get_limited_route_options("Paris", "Lyon", mode="live")
    assert route_live["status"] == "error"
    assert "disabled by default" in route_live["advisory"]


# ---------------------------------------------------------------------------
# FastAPI Web UI Endpoints Tests
# ---------------------------------------------------------------------------

def test_web_keyless_status_endpoint(client: TestClient) -> None:
    """Test GET /api/integrations/keyless/status endpoint."""
    res = client.get("/api/integrations/keyless/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["total_keyless_providers"] == 5


def test_web_weather_endpoint(client: TestClient) -> None:
    """Test GET /api/integrations/weather endpoint."""
    res = client.get("/api/integrations/weather?city=Barcelone&days=3")
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "open_meteo"
    assert len(data.get("items", [])) >= 1


def test_web_currency_endpoint(client: TestClient) -> None:
    """Test GET /api/integrations/currency/convert endpoint."""
    res = client.get("/api/integrations/currency/convert?amount=120&from_curr=EUR&to_curr=USD")
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "ecb_currency"
    assert len(data.get("items", [])) == 1


def test_web_guide_endpoint(client: TestClient) -> None:
    """Test GET /api/integrations/guides/destination endpoint."""
    res = client.get("/api/integrations/guides/destination?destination=Barcelone")
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "wikivoyage"
    assert len(data.get("items", [])) >= 1


# ---------------------------------------------------------------------------
# Multi-Agent Subagent Integration Tests
# ---------------------------------------------------------------------------

def test_subagents_phase_10_assumptions_and_sources() -> None:
    """Verify subagents correctly reference open data sources and safe assumptions."""
    with open("examples/city-trip/trip.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    trip = Trip.model_validate(data)
    engine = TravelOrchestrationEngine(mode="offline")
    results = engine.execute_full_pipeline(trip)

    # 1. destination-researcher includes Wikivoyage community source
    dest_res = results["destination-researcher"]
    assert any("wikivoyage" in s.url.lower() for s in dest_res.sources)
    assert any("Wikivoyage" in a for a in dest_res.assumptions)
    assert any("visa" in a.lower() for a in dest_res.assumptions)

    # 2. transport-planner mentions OSRM driving durations as estimates
    trans_res = results["transport-planner"]
    assert any("OSRM" in a for a in trans_res.assumptions)

    # 3. activity-curator incorporates Open-Meteo weather outlook
    act_res = results["activity-curator"]
    assert any("Open-Meteo" in a for a in act_res.assumptions)

    # 4. budget-analyst highlights ECB reference rate and credit card spread
    bud_res = results["budget-analyst"]
    assert any("ECB" in a for a in bud_res.assumptions)
    assert any("1.5%-3.5%" in a for a in bud_res.assumptions)

    # 5. quality-controller verifies coherence
    qc_res = results["quality-controller"]
    assert qc_res.status.value in ("complete", "partial")
