"""Deterministic offline editorial guide and cultural context provider."""

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


class MockGuideProvider(Provider):
    """Deterministic editorial guidebook provider with cultural customs and local insights."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_guide",
            category=ProviderCategory.GUIDE,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["editorial_context", "cultural_etiquette", "practical_advice"],
        )

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url=raw.get("source_url", "https://en.wikivoyage.org"),
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=None,
            price_status=PriceStatus.CONFIRMED.value,
            availability_status=AvailabilityStatus.LIVE.value,
            requires_booking_verification=False,
            title=f"Guide: {raw.get('city')} — {raw.get('topic')}",
            description=raw.get("content"),
            price=None,
            details=raw,
        )

    def search(
        self,
        city: str = "Barcelona",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        city_lower = city.lower().strip()
        if "barcelona" in city_lower:
            sections = [
                {
                    "city": "Barcelona",
                    "topic": "Dining Rhythm & Customs",
                    "content": "Lunch is typically 13:30-15:30. Dinner rarely begins before 20:30. Tipping is discretionary (round up 5-10%).",
                    "source_url": "https://en.wikivoyage.org/wiki/Barcelona",
                },
                {
                    "city": "Barcelona",
                    "topic": "Transit Etiquette & Safety",
                    "content": "T-Usual or T-Casual travel cards offer substantial savings on metro and buses. Watch belongings in crowded Las Ramblas corridors.",
                    "source_url": "https://en.wikivoyage.org/wiki/Barcelona",
                },
            ]
        elif "reykjavik" in city_lower or "iceland" in city_lower:
            sections = [
                {
                    "city": "Reykjavík",
                    "topic": "Pool & Thermal Etiquette",
                    "content": "Showering thoroughly with soap without a swimsuit before entering thermal pools is mandatory.",
                    "source_url": "https://en.wikivoyage.org/wiki/Reykjav%C3%ADk",
                },
                {
                    "city": "Reykjavík",
                    "topic": "Driving & Road Safety",
                    "content": "Check road.is and safetravel.is twice daily for wind warnings and road closures. Never stop on the Ring Road shoulder.",
                    "source_url": "https://safetravel.is",
                },
            ]
        else:
            sections = [
                {
                    "city": city,
                    "topic": "General Cultural Overview",
                    "content": f"Familiarize yourself with local greeting customs and municipal recycling rules in {city}.",
                    "source_url": f"https://en.wikivoyage.org/wiki/{city}",
                }
            ]

        items = [self.normalize_result(s) for s in sections]

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={"city": city},
            total_results=len(items),
            items=items,
            source_metadata=self.get_source_metadata(),
            warnings=[],
            requires_booking_verification=False,
        )
