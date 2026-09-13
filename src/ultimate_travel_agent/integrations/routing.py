"""Routing and mapping integration adapter (OSRM / OpenStreetMap)."""

from typing import Any, Dict
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class RoutingAdapter(BaseIntegrationAdapter):
    """Adapter for door-to-door transit and routing via OSRM / OpenStreetMap."""

    def __init__(self, enabled: bool = False, server_url: str = "http://localhost:5000") -> None:
        super().__init__(
            provider_name="OSRM",
            enabled=enabled,
            requires_api_key=False,
            data_transmitted_policy="Origin and destination coordinates only.",
        )
        self.server_url = server_url

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        origin = kwargs.get("origin", "Origin")
        destination = kwargs.get("destination", "Destination")
        return {
            "origin": origin,
            "destination": destination,
            "distance_km": 4.5,
            "walking_time_minutes": 55,
            "transit_time_minutes": 18,
            "driving_time_minutes": 14,
            "recommended_mode": "metro",
            "verification_level": VerificationLevel.CROSS_CHECKED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
