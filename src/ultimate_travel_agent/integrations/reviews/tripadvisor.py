"""TripAdvisor Content API provider for venue and hotel reviews."""

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


class TripadvisorReviewProvider(Provider):
    """TripAdvisor official Content API provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="tripadvisor_review",
            category=ProviderCategory.REVIEW,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["venue_reviews", "bubble_rating", "subratings"],
        )
        self.api_key = api_key or os.getenv("TRIPADVISOR_API_KEY", "")
        self._mock_delegate = MockReviewProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://api.content.tripadvisor.com",
            verification_level=VerificationLevel.COMMUNITY_RECOMMENDED.value,
            currency=None,
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.UNKNOWN.value,
            requires_booking_verification=False,
            title=f"TripAdvisor: {raw.get('venue', 'Venue')}",
            description=raw.get("sentiment", "Aggregated traveler feedback"),
            price=None,
            rating=raw.get("aggregate_rating", 4.5),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError("TripAdvisor API key not configured. Set TRIPADVISOR_API_KEY in .env.")
            raise ProviderConfigurationError("Live API calls to TripAdvisor disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
