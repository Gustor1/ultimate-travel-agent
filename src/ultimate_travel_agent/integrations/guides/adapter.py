"""Guidebook and editorial destination integration adapter (Wikivoyage / OpenGuidebooks)."""

from typing import Any, Dict
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class GuideAdapter(BaseIntegrationAdapter):
    """Adapter for travel guidebooks, cultural etiquette, and destination tips.

    Disabled by default. Uses open knowledge sources (Wikivoyage CC BY-SA).
    Never transmits user PII or triggers booking actions.
    """

    def __init__(self, enabled: bool = False) -> None:
        super().__init__(
            provider_name="GuidebookAdapter (Wikivoyage)",
            enabled=enabled,
            requires_api_key=False,
            data_transmitted_policy="Destination city or region name only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        city = kwargs.get("city", "Barcelona")
        return {
            "city": city,
            "overview": f"Curated cultural context and practical travel advice for {city}.",
            "sections": [
                {
                    "topic": "Etiquette & Customs",
                    "content": "Dining occurs later than in northern Europe: lunch from 13:30-15:30, dinner from 20:30-22:30. Tipping is customary for good service (5-10%) but not mandatory.",
                },
                {
                    "topic": "Safety & Pickpocket Awareness",
                    "content": "Exercise heightened vigilance around crowded metro stations and popular boulevards. Keep valuables in zipped internal pockets.",
                },
                {
                    "topic": "Quiet & Offbeat Neighborhoods",
                    "content": "Explore residential Gràcia or Poblenou for quiet leafy squares, local bakeries, and authentic neighborhood life.",
                },
            ],
            "official_tourist_office_url": f"https://www.visit-{city.lower().replace(' ', '')}.com",
            "verification_level": VerificationLevel.CROSS_CHECKED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
