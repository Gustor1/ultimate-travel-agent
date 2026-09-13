"""Tests for the local MCP tools."""

import pytest
from ultimate_travel_agent.mcp import tools


def test_list_trips() -> None:
    """Test discovering trips from example directories."""
    trips = tools.list_trips()
    assert len(trips) >= 2
    ids = {t["id"] for t in trips}
    assert "trip-city-barcelona-001" in ids
    assert "trip-roadtrip-iceland-002" in ids


def test_get_trip() -> None:
    """Test retrieving full trip data."""
    trip = tools.get_trip("examples/city-trip/trip.json")
    assert trip["id"] == "trip-city-barcelona-001"
    assert "Sagrada Família" in str(trip)


def test_get_trip_not_found() -> None:
    """Test error handling when trip file does not exist."""
    with pytest.raises(FileNotFoundError):
        tools.get_trip("examples/non_existent_trip.json")


def test_validate_trip() -> None:
    """Test trip validation endpoint."""
    res = tools.validate_trip("examples/city-trip/trip.json")
    assert res["valid"] is True
    assert res["coherence_issues"] == []
    assert res["total_days"] == 3
    assert res["total_nights"] == 2


def test_get_itinerary() -> None:
    """Test itinerary retrieval."""
    itinerary = tools.get_itinerary("examples/city-trip/trip.json")
    assert len(itinerary) == 3
    assert itinerary[0]["day_number"] == 1
    assert "Gràcia" in itinerary[0]["theme"]


def test_validate_itinerary() -> None:
    """Test itinerary validation."""
    res = tools.validate_itinerary("examples/city-trip/trip.json")
    assert res["valid"] is True
    assert res["total_days_scheduled"] == 3
    assert res["days_without_weather_backup"] == []


def test_calculate_budget() -> None:
    """Test budget calculation tool."""
    budget = tools.calculate_budget("examples/city-trip/trip.json", safety_buffer_pct=10.0)
    assert budget["currency"] == "EUR"
    assert budget["total_estimated_cost"] > 0
    assert budget["safety_buffer_amount"] > 0
    assert budget["grand_total"] > budget["total_estimated_cost"]


def test_list_booking_requirements() -> None:
    """Test listing user booking requirements with strict zero-auto-booking policy."""
    reqs = tools.list_booking_requirements("examples/city-trip/trip.json")
    assert len(reqs) >= 4
    types = {r["type"] for r in reqs}
    assert "accommodation" in types
    assert "transport" in types
    assert "activity_advance_ticket" in types
    assert "checklist_item" in types
    for r in reqs:
        assert r["mandatory"] is True
        assert "Manual" in r["action"] or "Purchase" in r["action"] or "Book" in r["action"] or len(r["action"]) > 0


def test_export_trip_summary() -> None:
    """Test exporting trip summary in markdown and json formats."""
    md_output = tools.export_trip_summary("examples/city-trip/trip.json", format="markdown")
    assert "# Dossier de Voyage" in md_output
    assert "Casa Bella Gràcia" in md_output

    json_output = tools.export_trip_summary("examples/city-trip/trip.json", format="json")
    assert '"trip"' in json_output
    assert '"agent_results"' in json_output


def test_validate_trip_enhanced_fields() -> None:
    """Test that validate_trip returns budget warnings and entity counts."""
    res = tools.validate_trip("examples/city-trip/trip.json")
    assert "stages_count" in res
    assert res["stages_count"] >= 1
    assert "reservations_count" in res
    assert res["reservations_count"] >= 1
    assert "unverified_items_count" in res


def test_mcp_server_protocol_interface() -> None:
    """Test the MCPServer instance directly via its list_tools and call_tool async methods."""
    import asyncio
    from ultimate_travel_agent.mcp.server import server

    tools_list = asyncio.run(server.list_tools())
    tool_names = {t.name for t in tools_list}
    expected_tools = {
        "list_trips",
        "get_trip",
        "validate_trip",
        "get_itinerary",
        "validate_itinerary",
        "calculate_budget",
        "list_booking_requirements",
        "export_trip_summary",
    }
    assert expected_tools.issubset(tool_names)

    # Call all 8 MCP tools through MCPServer interface to ensure protocol compliance
    trip = "examples/city-trip/trip.json"
    assert not asyncio.run(server.call_tool("list_trips", {})).is_error
    assert not asyncio.run(server.call_tool("get_trip", {"trip_path": trip})).is_error
    call_result = asyncio.run(
        server.call_tool("validate_trip", {"trip_path": trip})
    )
    assert not call_result.is_error
    assert "trip-city-barcelona-001" in str(call_result.content)
    assert not asyncio.run(server.call_tool("get_itinerary", {"trip_path": trip})).is_error
    assert not asyncio.run(server.call_tool("validate_itinerary", {"trip_path": trip})).is_error
    assert not asyncio.run(server.call_tool("calculate_budget", {"trip_path": trip, "safety_buffer_pct": 12.0})).is_error
    assert not asyncio.run(server.call_tool("list_booking_requirements", {"trip_path": trip})).is_error
    assert not asyncio.run(server.call_tool("export_trip_summary", {"trip_path": trip, "format": "markdown"})).is_error
