"""Deterministic offline accommodation provider focusing on quiet neighborhoods."""

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


class MockAccommodationProvider(Provider):
    """Curates accommodations in quiet strategic neighborhoods with zero automated booking."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_hotel",
            category=ProviderCategory.HOTEL,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "neighborhood_curation",
                "quiet_areas",
                "price_estimation",
                "amenity_filter",
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
            source_url=raw.get("official_booking_url", "https://www.example.com"),
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=raw.get("name", "Hotel"),
            description=(
                f"Neighborhood: {raw.get('neighborhood', 'Central')}. "
                f"Quietness: {raw.get('quietness_rating', 'High')}. Type: {raw.get('type', 'Boutique Hotel')}."
            ),
            price=raw.get("price_per_night"),
            rating=raw.get("rating", 4.5),
            details=raw,
        )

    def search(
        self,
        city: str = "Barcelona",
        checkin_date: str = "2026-10-15",
        checkout_date: str = "2026-10-18",
        neighborhood: Optional[str] = None,
        guests: int = 2,
        max_price_per_night: Optional[float] = None,
        currency: str = "EUR",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        """Search curated lodging options."""
        catalog = {
            "barcelona": [
                {
                    "name": "Casa Bonay & Quiet Suites Gràcia",
                    "neighborhood": "Gràcia",
                    "type": "Boutique Hotel",
                    "price_per_night": 140.0,
                    "currency": currency,
                    "quietness_rating": "High (pedestrian residential area)",
                    "rating": 4.6,
                    "review_count": 520,
                    "official_booking_url": "https://casabonay.com",
                },
                {
                    "name": "Hotel Brummell Poble Sec",
                    "neighborhood": "Poble Sec",
                    "type": "Design Hotel",
                    "price_per_night": 125.0,
                    "currency": currency,
                    "quietness_rating": "Medium-High",
                    "rating": 4.5,
                    "review_count": 310,
                    "official_booking_url": "https://hotelbrummell.com",
                },
            ],
            "reykjavik": [
                {
                    "name": "Eyja Guldsmeden Eco Hotel",
                    "neighborhood": "Hlíðar",
                    "type": "Eco Boutique Hotel",
                    "price_per_night": 210.0,
                    "currency": currency,
                    "quietness_rating": "High (peaceful district near downtown)",
                    "rating": 4.7,
                    "review_count": 480,
                    "official_booking_url": "https://guldsmedenhotels.com/eyja",
                }
            ],
        }

        city_key = city.lower().strip()
        lodgings = catalog.get(city_key, [
            {
                "name": f"Hotel Curated Suites ({city})",
                "neighborhood": neighborhood or "Quiet Historic Quarter",
                "type": "Boutique Hotel",
                "price_per_night": 135.0,
                "currency": currency,
                "quietness_rating": "High",
                "rating": 4.5,
                "review_count": 250,
                "official_booking_url": f"https://www.google.com/travel/hotels/{city}",
            }
        ])

        if neighborhood:
            filtered = [l for l in lodgings if neighborhood.lower() in l["neighborhood"].lower()]
            if filtered:
                lodgings = filtered

        if max_price_per_night is not None:
            lodgings = [l for l in lodgings if l["price_per_night"] <= max_price_per_night]

        items = [self.normalize_result(l) for l in lodgings]

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={
                "city": city,
                "checkin_date": checkin_date,
                "checkout_date": checkout_date,
                "neighborhood": neighborhood,
                "guests": guests,
            },
            total_results=len(items),
            items=items,
            source_metadata=self.get_source_metadata(),
            warnings=["Offline estimate: confirm room availability, local taxes, and cancellation policies directly with lodging."],
            requires_booking_verification=True,
        )
