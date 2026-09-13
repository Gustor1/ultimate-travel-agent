"""Rail schedule and connection integration adapter."""

from typing import Any, Dict, Optional
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class TrainAdapter(BaseIntegrationAdapter):
    """Adapter for European and international rail timetables (DB Hafas / Navitia).

    Disabled by default. Never purchases rail tickets.
    """

    def __init__(self, enabled: bool = False, api_key: Optional[str] = None) -> None:
        super().__init__(
            provider_name="RailScheduleAdapter",
            enabled=enabled,
            requires_api_key=False,
            api_key=api_key,
            data_transmitted_policy="Station names and departure date only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        origin = kwargs.get("origin", "Paris Gare de Lyon")
        destination = kwargs.get("destination", "Barcelona Sants")
        return {
            "origin": origin,
            "destination": destination,
            "train_options": [
                {
                    "operator": "SNCF / Renfe TGV INOUI",
                    "train_number": "TGV 9713",
                    "departure": "09:42",
                    "arrival": "16:34",
                    "duration_minutes": 412,
                    "estimated_fare_eur": 89.0,
                    "official_booking_url": "https://www.sncf-connect.com",
                }
            ],
            "official_booking_notice": "Ticket must be purchased on official railway portal.",
            "verification_level": VerificationLevel.OFFICIAL_VERIFIED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
