"""StayAPI provider for Trip.com hotel reviews only.

IMPORTANT NOTICE:
StayAPI Trip.com is strictly utilized as a source of verified traveler reviews and ratings.
It is NOT an availability, pricing, or automated booking engine.
"""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    PriceStatus,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
)
from ultimate_travel_agent.integrations.reviews.mock import MockReviewProvider
from ultimate_travel_agent.models import VerificationLevel


class StayAPIReviewProvider(Provider):
    """StayAPI provider for Trip.com customer reviews.

    Does NOT provide room inventory, live pricing, or reservation capabilities.
    Requires STAYAPI_API_KEY for live queries.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="stayapi_review",
            category=ProviderCategory.REVIEW,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["hotel_reviews", "trip_dot_com_ratings"],
        )
        self.api_key = api_key or os.getenv("STAYAPI_API_KEY", "")
        self._mock_delegate = MockReviewProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://stayapi.com",
            verification_level=VerificationLevel.COMMUNITY_RECOMMENDED.value,
            currency=None,
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.UNKNOWN.value,
            requires_booking_verification=False,
            title=f"Trip.com Reviews: {raw.get('venue', 'Hotel')}",
            description=f"Trip.com traveler reviews aggregated via StayAPI (reviews only, not live inventory)",
            price=None,
            rating=raw.get("aggregate_rating", 4.4),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError("StayAPI key not configured. Set STAYAPI_API_KEY in .env.")
            raise ProviderConfigurationError("Live API calls to StayAPI disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
            it.title = f"Trip.com Review via StayAPI: {it.details.get('venue', 'Hotel')}"
        return res
