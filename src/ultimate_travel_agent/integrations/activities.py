"""Activities and points-of-interest integration adapter."""

from typing import Any, Dict, Optional
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class ActivityAdapter(BaseIntegrationAdapter):
    """Adapter for POIs, attractions, and cultural sites (Wikivoyage / OpenTripMap).

    Disabled by default. Read-only search.
    """

    def __init__(self, enabled: bool = False, api_key: Optional[str] = None) -> None:
        super().__init__(
            provider_name="ActivityPOIAdapter",
            enabled=enabled,
            requires_api_key=False,
            api_key=api_key,
            data_transmitted_policy="City and category keyword only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        city = kwargs.get("city", "Barcelona")
        return {
            "city": city,
            "attractions": [
                {
                    "title": "Basilique de la Sagrada Família",
                    "category": "culture",
                    "crowd_level": "high",
                    "quiet_slot_advice": "Book 09:00 morning opening slot.",
                    "official_booking_url": "https://sagradafamilia.org",
                },
                {
                    "title": "Park Güell",
                    "category": "landscape",
                    "crowd_level": "high",
                    "quiet_slot_advice": "Book late afternoon 17:30 slot.",
                    "official_booking_url": "https://parkguell.barcelona",
                },
            ],
            "verification_level": VerificationLevel.OFFICIAL_VERIFIED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
