"""Experimental social discovery provider (RedNote, Douyin, TikTok, local travel blogs).

STRICT SAFETY PROTOCOL:
- Never confirms prices, timetables, safety, visa, or availability.
- Every result MUST be strictly marked 'social_discovery_only' with price_status 'needs_verification'.
- No unauthorized scraping or automated user-session hijacking.
"""

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


class SocialDiscoveryProvider(Provider):
    """Experimental social trend and viral discovery provider with strict unverified tagging."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="social_discovery",
            category=ProviderCategory.SOCIAL,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["viral_spots", "hidden_gems", "trending_cafes"],
        )

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url=raw.get("source_url", "https://www.xiaohongshu.com"),
            verification_level=VerificationLevel.SOCIAL_DISCOVERY_ONLY.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.NEEDS_VERIFICATION.value,
            availability_status=AvailabilityStatus.UNKNOWN.value,
            requires_booking_verification=True,
            title=raw.get("title", "Viral Discovery"),
            description=(
                f"Platform: {raw.get('platform', 'Social Media')}. "
                f"Trend note: {raw.get('trend_note')}. "
                f"Requires manual verification before visit."
            ),
            price=raw.get("estimated_price"),
            rating=raw.get("popularity_score", 4.8),
            details=raw,
        )

    def search(
        self,
        city: str = "Barcelona",
        keyword: Optional[str] = None,
        **kwargs: Any,
    ) -> ProviderSearchResult:
        trends = [
            {
                "platform": "RedNote (Xiaohongshu)",
                "title": f"Charming Hidden Patio Cafe ({city})",
                "trend_note": "Aesthetic courtyard viral for cold brew and traditional pastries",
                "estimated_price": 8.0,
                "currency": "EUR",
                "popularity_score": 4.9,
                "source_url": "https://www.xiaohongshu.com/discovery",
            },
            {
                "platform": "TikTok / Douyin",
                "title": f"Sunset Rooftop Panorama ({city})",
                "trend_note": "Golden hour viewpoint popular among independent backpackers",
                "estimated_price": 0.0,
                "currency": "EUR",
                "popularity_score": 4.7,
                "source_url": "https://www.tiktok.com/tag/travel",
            },
        ]

        items = [self.normalize_result(t) for t in trends]

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={"city": city, "keyword": keyword},
            total_results=len(items),
            items=items,
            source_metadata=self.get_source_metadata(),
            warnings=[
                "SOCIAL DISCOVERY WARNING: All findings are unverified community trends. "
                "Never rely on social posts for confirmed prices, operating hours, visas, or safety conditions."
            ],
            requires_booking_verification=True,
        )
