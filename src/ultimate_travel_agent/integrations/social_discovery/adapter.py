"""Social discovery integration adapter (TikTok, RedNote, Instagram trends)."""

from typing import Any, Dict, Optional
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class SocialDiscoveryAdapter(BaseIntegrationAdapter):
    """Adapter for trend and hidden gem discovery from social media.

    Disabled by default.
    CRITICAL: All outputs are strictly tagged as 'social_discovery_only' or 'unverified'.
    """

    def __init__(self, enabled: bool = False) -> None:
        super().__init__(
            provider_name="SocialDiscoveryAdapter",
            enabled=enabled,
            requires_api_key=False,
            data_transmitted_policy="Keyword and city only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        city = kwargs.get("city", "Barcelona")
        return {
            "city": city,
            "social_trends": [
                {
                    "title": "Secret rooftop terrace overlook in Gràcia",
                    "trend_platform": "RedNote",
                    "trend_tags": ["#hiddenbarcelona", "#graciavibes"],
                    "verification_warning": "Unverified opening hours and private property boundaries. Independent verification required.",
                }
            ],
            "verification_level": VerificationLevel.SOCIAL_DISCOVERY_ONLY.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
