"""Flight integrations package."""

from ultimate_travel_agent.integrations.flights.adapter import FlightAdapter
from ultimate_travel_agent.integrations.flights.amadeus import AmadeusFlightProvider
from ultimate_travel_agent.integrations.flights.aviation_edge import AviationEdgeFlightProvider
from ultimate_travel_agent.integrations.flights.mock import MockFlightProvider

__all__ = [
    "AmadeusFlightProvider",
    "AviationEdgeFlightProvider",
    "FlightAdapter",
    "MockFlightProvider",
]
