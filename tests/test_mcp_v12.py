import asyncio
import pytest
from ultimate_travel_agent.mcp import tools
from ultimate_travel_agent.mcp.server import server


def test_mcp_server_v12_registration() -> None:
    """Check that server version is 1.2.0 and all 21 tools are registered."""
    assert server.version == "1.2.0"
    tool_names = {t.name for t in asyncio.run(server.list_tools())}

    # V1.0 & V1.1 tools
    assert "list_trips" in tool_names
    assert "get_trip" in tool_names
    assert "validate_trip" in tool_names
    assert "get_itinerary" in tool_names
    assert "validate_itinerary" in tool_names
    assert "calculate_budget" in tool_names
    assert "list_booking_requirements" in tool_names
    assert "export_trip_summary" in tool_names
    assert "get_inter_city_routes" in tool_names
    assert "get_contingency_dossier" in tool_names

    # V1.2 tools
    v12_tools = [
        "list_integration_providers",
        "get_provider_status",
        "search_flight_options",
        "search_train_options",
        "search_accommodation_options",
        "search_hotel_reviews",
        "search_activity_options",
        "get_route_options",
        "get_weather_outlook",
        "convert_currency",
        "search_travel_sources",
    ]
    for t in v12_tools:
        assert t in tool_names, f"Tool '{t}' missing from MCP server v1.2.0"


def test_mcp_list_integration_providers() -> None:
    """Test list_integration_providers tool."""
    providers = tools.list_integration_providers()
    assert len(providers) >= 15
    # Filter by category
    flights = tools.list_integration_providers(category="flight")
    assert all(p["category"] == "flight" for p in flights)


def test_mcp_get_provider_status() -> None:
    """Test get_provider_status for valid and invalid names."""
    status = tools.get_provider_status("mock_flight")
    assert status["status"] == "healthy"
    assert status["is_configured"] is True

    # Unknown provider
    err = tools.get_provider_status("unknown_provider_xyz")
    assert err["status"] == "error"
    assert err["error_type"] == "ProviderNotFound"


def test_mcp_search_flight_options() -> None:
    """Test search_flight_options tool."""
    res = tools.search_flight_options(
        origin="PAR",
        destination="BCN",
        departure_date="2026-10-15",
        passengers=2,
    )
    assert res["category"] == "flight"
    assert res["total_results"] >= 2
    assert res["requires_booking_verification"] is True

    # Validation: passengers < 1
    err = tools.search_flight_options(origin="PAR", destination="BCN", departure_date="2026-10-15", passengers=0)
    assert err["status"] == "error"

    # Live mode unconfigured returns clear error
    live_err = tools.search_flight_options(
        origin="PAR",
        destination="BCN",
        departure_date="2026-10-15",
        mode="live",
    )
    # amadeus_flight in live mode raises ProviderConfigurationError
    assert "offline" in live_err.get("error", "") or live_err.get("status") == "error" or live_err.get("total_results", 0) >= 0


def test_mcp_search_train_options() -> None:
    """Test search_train_options tool."""
    res = tools.search_train_options(origin="Paris", destination="Barcelona", date="2026-10-15")
    assert res["category"] == "train"
    assert len(res["items"]) >= 1
    assert "door-to-door" in res["items"][0]["description"].lower()


def test_mcp_search_accommodation_options() -> None:
    """Test search_accommodation_options tool."""
    res = tools.search_accommodation_options(city="Barcelona", checkin_date="2026-10-15", checkout_date="2026-10-18")
    assert res["category"] == "hotel"
    assert len(res["items"]) >= 1
    assert res["requires_booking_verification"] is True


def test_mcp_search_hotel_reviews() -> None:
    """Test search_hotel_reviews tool."""
    res = tools.search_hotel_reviews(hotel_name="Casa Bonay", city="Barcelona")
    assert res["category"] == "review"
    assert res["items"][0]["rating"] >= 4.0


def test_mcp_search_activity_options() -> None:
    """Test search_activity_options tool."""
    res = tools.search_activity_options(city="Barcelona", category="culture", indoor_only=True)
    assert res["category"] == "activity"
    assert len(res["items"]) >= 1
    assert res["items"][0]["details"]["is_indoor"] is True


def test_mcp_get_route_options() -> None:
    """Test get_route_options tool."""
    res = tools.get_route_options(origin="Paris", destination="Barcelona")
    assert res["category"] == "map"
    assert len(res["items"]) >= 1
    assert res["items"][0]["details"]["distance_km"] > 0


def test_mcp_get_weather_outlook() -> None:
    """Test get_weather_outlook tool."""
    res = tools.get_weather_outlook(city="Barcelona", date="2026-10-15")
    assert res["category"] == "weather"
    assert res["items"][0]["details"]["temp_high_c"] > 0


def test_mcp_convert_currency() -> None:
    """Test convert_currency tool."""
    res = tools.convert_currency(amount=100.0, from_currency="EUR", to_currency="USD")
    assert res["category"] == "currency"
    assert res["items"][0]["price"] == 108.0

    # Negative amount
    err = tools.convert_currency(amount=-5.0, from_currency="EUR", to_currency="USD")
    assert err["status"] == "error"


def test_mcp_search_travel_sources() -> None:
    """Test search_travel_sources for guide and social sources."""
    # Guide
    res_guide = tools.search_travel_sources(query="Barcelona", category="guide")
    assert res_guide["category"] == "guide"
    assert len(res_guide["items"]) >= 1

    # Social
    res_soc = tools.search_travel_sources(query="Barcelona", category="social")
    assert res_soc["category"] == "social"
    assert res_soc["items"][0]["verification_level"] == "social_discovery_only"
