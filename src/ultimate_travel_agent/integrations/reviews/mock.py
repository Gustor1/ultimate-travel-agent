"""Deterministic offline review provider."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    PriceStatus,
    ProviderCategory,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
)
from ultimate_travel_agent.models import VerificationLevel


class MockReviewProvider(Provider):
    """Deterministic community reviews and satisfaction sentiment provider."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_review",
            category=ProviderCategory.REVIEW,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["hotel_reviews", "venue_ratings", "sentiment_summary"],
        )

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url=raw.get("source_url", "https://tripadvisor.com"),
            verification_level=VerificationLevel.COMMUNITY_RECOMMENDED.value,
            currency=None,
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=False,
            title=f"Review for {raw.get('venue', 'Venue')}",
            description=raw.get("summary", "Positive reviews from verified travelers."),
            price=None,
            rating=raw.get("aggregate_rating", 4.5),
            details=raw,
        )

    def search(
        self,
        hotel_name: str = "Casa Bonay",
        city: str = "Barcelona",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        review_data = {
            "venue": hotel_name,
            "city": city,
            "aggregate_rating": 4.6,
            "review_count": 890,
            "sentiment": "Excellent quietness and authentic local character; central yet calm.",
            "source_url": "https://www.tripadvisor.com",
            "highlights": ["Peaceful courtyards", "Helpful local staff", "Walkable neighborhood"],
        }
        item = self.normalize_result(review_data)
        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={"hotel_name": hotel_name, "city": city},
            total_results=1,
            items=[item],
            source_metadata=self.get_source_metadata(),
            warnings=[],
            requires_booking_verification=False,
        )
