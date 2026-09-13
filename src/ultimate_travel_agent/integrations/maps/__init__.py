"""Maps and routing integrations package."""

from ultimate_travel_agent.integrations.maps.adapter import RoutingAdapter
from ultimate_travel_agent.integrations.maps.google_maps import GoogleMapsRoutesProvider
from ultimate_travel_agent.integrations.maps.mock import MockMapsProvider
from ultimate_travel_agent.integrations.maps.nominatim import NominatimProvider
from ultimate_travel_agent.integrations.maps.openroute import OpenRouteServiceProvider
from ultimate_travel_agent.integrations.maps.osrm import OSRMProvider

__all__ = [
    "GoogleMapsRoutesProvider",
    "MockMapsProvider",
    "NominatimProvider",
    "OpenRouteServiceProvider",
    "OSRMProvider",
    "RoutingAdapter",
]
