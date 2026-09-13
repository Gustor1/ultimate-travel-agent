"""Local MCP (Model Context Protocol) Server for ultimate-travel-agent.

Exposes read-only and calculation tools for local travel planning and inspection.
Strictly prohibits automated bookings, payments, or destructive operations.
"""

import sys
from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from ultimate_travel_agent.mcp import tools

# Initialize MCP Server
server = MCPServer(
    name="ultimate-travel-agent",
    version="1.0.0",
    description="Offline-first, privacy-respecting travel planning tools."
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


def main() -> None:
    """Run the MCP server over stdio transport."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
