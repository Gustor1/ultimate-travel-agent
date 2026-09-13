"""Local MCP (Model Context Protocol) Server for ultimate-travel-agent.

Exposes read-only and calculation tools for local travel planning and inspection.
Strictly prohibits automated bookings, payments, or destructive operations.
"""

import sys
from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from ultimate_travel_agent.mcp import tools

# Initialize MCP Server v1.2.0
server = MCPServer(
    name="ultimate-travel-agent",
    version="1.2.0",
    description="Offline-first, privacy-respecting travel planning and provider hub tools."
)


@server.tool(name="list_trips", description="Scan and list all travel dossiers available in the workspace.")
def list_trips(directory: Optional[str] = None) -> List[Dict[str, Any]]:
    """List trips found in the given directory or default examples."""
    return tools.list_trips(directory=directory)


@server.tool(name="get_trip", description="Retrieve the full structured content of a travel dossier by file path.")
def get_trip(trip_path: str) -> Dict[str, Any]:
    """Get full details of a specific trip."""
    return tools.get_trip(trip_path=trip_path)


@server.tool(name="validate_trip", description="Validate data schema conformance and internal logical coherence of a trip.")
def validate_trip(trip_path: str) -> Dict[str, Any]:
    """Validate a trip's internal consistency and dates."""
    return tools.validate_trip(trip_path=trip_path)


@server.tool(name="get_itinerary", description="Retrieve the day-by-day chronological itinerary of a trip.")
def get_itinerary(trip_path: str) -> List[Dict[str, Any]]:
    """Get the daily scheduled timeline."""
    return tools.get_itinerary(trip_path=trip_path)


@server.tool(name="validate_itinerary", description="Validate schedule continuity, day count, and bad-weather contingencies.")
def validate_itinerary(trip_path: str) -> Dict[str, Any]:
    """Validate itinerary timeline and rainy day alternatives."""
    return tools.validate_itinerary(trip_path=trip_path)


@server.tool(name="calculate_budget", description="Compute the itemized budget breakdown with safety contingency reserve.")
def calculate_budget(trip_path: str, safety_buffer_pct: float = 12.0) -> Dict[str, Any]:
    """Calculate expenses, contingency reserve, and budget warnings."""
    return tools.calculate_budget(trip_path=trip_path, safety_buffer_pct=safety_buffer_pct)


@server.tool(name="list_booking_requirements", description="List all items requiring user action (advance tickets, lodging, transport). Never auto-books.")
def list_booking_requirements(trip_path: str) -> List[Dict[str, Any]]:
    """Extract all booking requirements and official portal URLs for traveler review."""
    return tools.list_booking_requirements(trip_path=trip_path)


@server.tool(name="export_trip_summary", description="Run multi-agent synthesis and export the complete trip dossier in Markdown or JSON format.")
def export_trip_summary(trip_path: str, format: str = "markdown") -> str:
    """Generate the finalized trip report."""
    return tools.export_trip_summary(trip_path=trip_path, format=format)


@server.tool(name="get_inter_city_routes", description="Retrieve multi-option inter-city transit routes and recommendations.")
def get_inter_city_routes(trip_path: str) -> List[Dict[str, Any]]:
    """Get competing inter-city transit options."""
    return tools.get_inter_city_routes(trip_path=trip_path)


@server.tool(name="get_contingency_dossier", description="Generate pre-departure checklists, weather/closure Plan B, and generic emergency summary.")
def get_contingency_dossier(trip_path: str) -> Dict[str, Any]:
    """Get contingency and preparation pack."""
    return tools.get_contingency_dossier(trip_path=trip_path)


# ===========================================================================
# Phase 8: V1.2 Travel Integration & Provider Hub MCP Tools
# ===========================================================================

@server.tool(name="list_integration_providers", description="List available travel integration providers (offline, mock, live) and capabilities.")
def list_integration_providers(category: Optional[str] = None, mode: Optional[str] = None) -> List[Dict[str, Any]]:
    """List registered travel data integration providers."""
    return tools.list_integration_providers(category=category, mode=mode)


@server.tool(name="get_provider_status", description="Inspect configuration, API key presence, and health of a specific integration provider.")
def get_provider_status(provider_name: str) -> Dict[str, Any]:
    """Check status and readiness of an integration provider."""
    return tools.get_provider_status(provider_name=provider_name)


@server.tool(name="search_flight_options", description="Search flight offers with fare estimation, duration, and official ticketing links (never auto-books).")
def search_flight_options(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    max_budget: Optional[float] = None,
    currency: str = "EUR",
    sort_by: str = "price",
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search flight offers in offline, mock, or live mode."""
    return tools.search_flight_options(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        passengers=passengers,
        max_budget=max_budget,
        currency=currency,
        sort_by=sort_by,
        mode=mode,
    )


@server.tool(name="search_train_options", description="Search rail connections with door-to-door transit time, transfers, and official booking URLs.")
def search_train_options(
    origin: str,
    destination: str,
    date: str,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search rail timetables in offline, mock, or live mode."""
    return tools.search_train_options(
        origin=origin,
        destination=destination,
        date=date,
        mode=mode,
    )


@server.tool(name="search_accommodation_options", description="Search curated lodgings in quiet neighborhoods with indicative rates (read-only, no booking).")
def search_accommodation_options(
    city: str,
    checkin_date: str,
    checkout_date: str,
    neighborhood: Optional[str] = None,
    guests: int = 2,
    max_price_per_night: Optional[float] = None,
    currency: str = "EUR",
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search accommodation options in offline, mock, or live mode."""
    return tools.search_accommodation_options(
        city=city,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        neighborhood=neighborhood,
        guests=guests,
        max_price_per_night=max_price_per_night,
        currency=currency,
        mode=mode,
    )


@server.tool(name="search_hotel_reviews", description="Look up community sentiment, ratings, and reviews for a hotel property (reviews only, not booking).")
def search_hotel_reviews(
    hotel_name: str,
    city: str,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search reviews from sources like StayAPI Trip.com or TripAdvisor."""
    return tools.search_hotel_reviews(
        hotel_name=hotel_name,
        city=city,
        mode=mode,
    )


@server.tool(name="search_activity_options", description="Search curated activities with crowd avoidance advice, weather alternatives, and ticket links.")
def search_activity_options(
    city: str,
    category: Optional[str] = None,
    indoor_only: Optional[bool] = None,
    max_price: Optional[float] = None,
    currency: str = "EUR",
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search activities across cultural, nature, and dining dimensions."""
    return tools.search_activity_options(
        city=city,
        category=category,
        indoor_only=indoor_only,
        max_price=max_price,
        currency=currency,
        mode=mode,
    )


@server.tool(name="get_route_options", description="Calculate distance, durations (walking, driving, transit), and detect transit fatigue overload.")
def get_route_options(
    origin: str,
    destination: str,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Calculate route distance and transit durations."""
    return tools.get_route_options(
        origin=origin,
        destination=destination,
        mode=mode,
    )


@server.tool(name="get_weather_outlook", description="Retrieve weather forecast and indoor contingency recommendations for bad weather.")
def get_weather_outlook(
    city: str,
    date: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Get weather outlook with rainy-day Plan B recommendations."""
    return tools.get_weather_outlook(
        city=city,
        date=date,
        mode=mode,
    )


@server.tool(name="convert_currency", description="Convert monetary amounts between currencies with published reference exchange date.")
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    custom_rate: Optional[float] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Convert currency amounts with reference rate tracking."""
    return tools.convert_currency(
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency,
        custom_rate=custom_rate,
        mode=mode,
    )


@server.tool(name="search_travel_sources", description="Search editorial guides or social discovery trends (social results tagged social_discovery_only).")
def search_travel_sources(
    query: str,
    category: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search travel knowledge sources and trends."""
    return tools.search_travel_sources(
        query=query,
        category=category,
        mode=mode,
    )


def main() -> None:
    """Run the MCP server over stdio transport."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
