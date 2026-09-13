"""Reviews and guidebooks integration adapter."""

from typing import Any, Dict, Optional
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class ReviewAdapter(BaseIntegrationAdapter):
    """Adapter for community ratings and guidebooks (TripAdvisor via Composio / Guidebooks).

    Disabled by default. Read-only sentiment and rating lookup.
    """

    def __init__(self, enabled: bool = False, api_key: Optional[str] = None) -> None:
        super().__init__(
            provider_name="CommunityReviewsAdapter",
            enabled=enabled,
            requires_api_key=False,
            api_key=api_key,
            data_transmitted_policy="Venue name and city only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        venue = kwargs.get("venue", "Venue")
        return {
            "venue": venue,
            "aggregate_rating": 4.6,
            "total_reviews": 1280,
            "consensus_sentiment": "Highly recommended for peaceful ambiance and local authenticity.",
            "verification_level": VerificationLevel.COMMUNITY_RECOMMENDED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
