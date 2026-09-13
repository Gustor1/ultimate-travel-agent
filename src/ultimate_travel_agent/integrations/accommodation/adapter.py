"""Accommodation and lodging search integration adapter."""

from typing import Any, Dict, Optional
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class HotelAdapter(BaseIntegrationAdapter):
    """Adapter for lodging search and neighborhood pricing.

    Disabled by default. Read-only search; automated booking strictly disallowed.
    """

    def __init__(self, enabled: bool = False, api_key: Optional[str] = None) -> None:
        super().__init__(
            provider_name="HotelSearchAdapter",
            enabled=enabled,
            requires_api_key=False,
            api_key=api_key,
            data_transmitted_policy="City, neighborhood, dates, room count only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        city = kwargs.get("city", "Barcelona")
        neighborhood = kwargs.get("neighborhood", "Gràcia")
        return {
            "city": city,
            "neighborhood": neighborhood,
            "curated_lodgings": [
                {
                    "name": "Casa Bella Gràcia Boutique Hotel",
                    "type": "hotel",
                    "nightly_rate_eur": 115.0,
                    "quietness_rating": "high",
                    "official_booking_url": "https://casabellagracia.com",
                }
            ],
            "official_booking_notice": "Book directly on hotel website. No payment handled by travel agent.",
            "verification_level": VerificationLevel.CROSS_CHECKED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
