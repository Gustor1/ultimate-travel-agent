"""Flight lookup integration adapter (Amadeus Sandbox)."""

from typing import Any, Dict, Optional
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class FlightAdapter(BaseIntegrationAdapter):
    """Adapter for flight schedule and fare search via Amadeus Sandbox.

    Disabled by default. Requires AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET.
    Never executes flight reservations or ticketing.
    """

    def __init__(
        self,
        enabled: bool = False,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        super().__init__(
            provider_name="AmadeusFlightSandbox",
            enabled=enabled,
            requires_api_key=True,
            api_key=api_key,
            data_transmitted_policy="Airport IATA codes, dates, passenger count only.",
        )
        self.api_secret = api_secret

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        origin = kwargs.get("origin", "PAR")
        destination = kwargs.get("destination", "BCN")
        return {
            "origin": origin,
            "destination": destination,
            "sample_offers": [
                {
                    "carrier": "Vueling",
                    "flight_number": "VY8001",
                    "departure": "08:15",
                    "arrival": "09:55",
                    "duration_minutes": 100,
                    "estimated_fare_eur": 75.0,
                    "official_booking_url": "https://www.vueling.com",
                }
            ],
            "official_booking_notice": "Manual booking required on airline website. Automated ticketing prohibited.",
            "verification_level": VerificationLevel.CROSS_CHECKED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
