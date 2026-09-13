"""Deterministic offline activity and POI provider."""

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


class MockActivityProvider(Provider):
    """Deterministic activities and attractions curator with crowd and weather modeling."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_activity",
            category=ProviderCategory.ACTIVITY,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "category_filtering",
                "indoor_outdoor_flagging",
                "weather_backup",
                "closure_backup",
                "crowd_avoidance",
                "official_ticketing_link",
            ],
        )

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url=raw.get("official_booking_url", "https://www.example.org"),
            verification_level=raw.get("verification_level", VerificationLevel.OFFICIAL_VERIFIED.value),
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.CONFIRMED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=raw.get("booking_required", True),
            title=raw.get("title", "Activity"),
            description=(
                f"Category: {raw.get('category')}. Duration: {raw.get('duration_minutes')} min. "
                f"Setting: {'Indoor' if raw.get('is_indoor') else 'Outdoor'}. "
                f"Crowd: {raw.get('crowd_level', 'moderate')}."
            ),
            price=raw.get("cost_per_person"),
            rating=raw.get("rating", 4.7),
            details=raw,
        )

    def search(
        self,
        city: str = "Barcelona",
        category: Optional[str] = None,
        indoor_only: Optional[bool] = None,
        max_price: Optional[float] = None,
        currency: str = "EUR",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        """Search activities with multi-criteria filtering."""
        catalog = [
            {
                "id": "sagrada_familia",
                "title": "Basílica de la Sagrada Família",
                "city": "Barcelona",
                "category": "culture",
                "duration_minutes": 120,
                "cost_per_person": 26.0,
                "currency": currency,
                "is_indoor": True,
                "booking_required": True,
                "crowd_level": "very_high",
                "anti_crowd_strategy": "First morning slot at 09:00 with pre-booked timed ticket.",
                "weather_alternative": "Perfect indoor shelter during rain.",
                "closure_alternative": "Sant Pau Art Nouveau Site (15 min walk).",
                "official_booking_url": "https://sagradafamilia.org",
                "verification_level": VerificationLevel.OFFICIAL_VERIFIED.value,
            },
            {
                "id": "park_guell",
                "title": "Park Güell Monumental Zone",
                "city": "Barcelona",
                "category": "scenery",
                "duration_minutes": 90,
                "cost_per_person": 10.0,
                "currency": currency,
                "is_indoor": False,
                "booking_required": True,
                "crowd_level": "high",
                "anti_crowd_strategy": "Late afternoon entry at 17:00 when tour buses depart.",
                "weather_alternative": "Casa Museu Gaudí inside the park or Casa Batlló downtown.",
                "closure_alternative": "Bunkers del Carmel viewpoint nearby.",
                "official_booking_url": "https://parkguell.barcelona",
                "verification_level": VerificationLevel.OFFICIAL_VERIFIED.value,
            },
            {
                "id": "tapas_gracia",
                "title": "Authentic Tapas Tasting in Gràcia",
                "city": "Barcelona",
                "category": "gastronomy",
                "duration_minutes": 75,
                "cost_per_person": 22.0,
                "currency": currency,
                "is_indoor": True,
                "booking_required": False,
                "crowd_level": "low",
                "anti_crowd_strategy": "Arrive at 13:00 or 20:00 before peak local rush.",
                "weather_alternative": "Mercat de la Llibertat covered market hall.",
                "closure_alternative": "Bar Mut or Bodega Quimet.",
                "official_booking_url": "https://www.barcelona.cat/en/eat",
                "verification_level": VerificationLevel.COMMUNITY_RECOMMENDED.value,
            },
            {
                "id": "skogafoss",
                "title": "Skógafoss Waterfall Trail",
                "city": "Skógar",
                "category": "nature",
                "duration_minutes": 90,
                "cost_per_person": 0.0,
                "currency": currency,
                "is_indoor": False,
                "booking_required": False,
                "crowd_level": "moderate",
                "anti_crowd_strategy": "Early morning visit before 09:30.",
                "weather_alternative": "Skógar Folk Museum (indoor covered cultural exhibit).",
                "closure_alternative": "Kvernufoss canyon walk (hidden nearby gorge).",
                "official_booking_url": "https://www.south.is/en/place/skogafoss",
                "verification_level": VerificationLevel.OFFICIAL_VERIFIED.value,
            },
        ]

        # Filter by city
        city_lower = city.lower().strip()
        filtered = [a for a in catalog if city_lower in a["city"].lower()]
        if not filtered:
            filtered = [
                {
                    "id": f"{city_lower}_historic_center",
                    "title": f"Historic Old Town Walking Tour ({city})",
                    "city": city,
                    "category": category or "culture",
                    "duration_minutes": 120,
                    "cost_per_person": 15.0,
                    "currency": currency,
                    "is_indoor": False,
                    "booking_required": False,
                    "crowd_level": "moderate",
                    "anti_crowd_strategy": "Morning walk prior to midday crowds.",
                    "weather_alternative": "Municipal art and history museum.",
                    "closure_alternative": "Public library and covered arcades.",
                    "official_booking_url": f"https://www.google.com/search?q={city}+tourism",
                    "verification_level": VerificationLevel.CROSS_CHECKED.value,
                }
            ]

        if category:
            cat_match = [a for a in filtered if a["category"].lower() == category.lower()]
            if cat_match:
                filtered = cat_match

        if indoor_only is not None:
            filtered = [a for a in filtered if a["is_indoor"] == indoor_only]

        if max_price is not None:
            filtered = [a for a in filtered if a["cost_per_person"] <= max_price]

        items = [self.normalize_result(a) for a in filtered]

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={
                "city": city,
                "category": category,
                "indoor_only": indoor_only,
                "max_price": max_price,
            },
            total_results=len(items),
            items=items,
            source_metadata=self.get_source_metadata(),
            warnings=["No automated purchases allowed. Check official tickets directly via official URLs."],
            requires_booking_verification=True,
        )
