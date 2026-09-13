"""Amadeus Hotel Search API provider (read-only, no automated booking)."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.accommodation.mock import MockAccommodationProvider
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
from ultimate_travel_agent.models import VerificationLevel


class AmadeusHotelProvider(Provider):
    """Amadeus Hotel Search API provider for catalog lookups and indicative rates."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="amadeus_hotel",
            category=ProviderCategory.HOTEL,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["hotel_search", "price_ranges", "amenities"],
        )
        self.client_id = client_id or os.getenv("AMADEUS_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("AMADEUS_CLIENT_SECRET", "")
        self._mock_delegate = MockAccommodationProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.client_id.strip() and self.client_secret.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://www.amadeus.com",
            verification_level=(
                VerificationLevel.OFFICIAL_VERIFIED.value
                if self.mode == ProviderMode.LIVE
                else VerificationLevel.CROSS_CHECKED.value
            ),
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=raw.get("name", "Hotel"),
            description=f"Amadeus listed property: {raw.get('neighborhood', 'Center')}",
            price=raw.get("price_per_night"),
            rating=raw.get("rating", 4.0),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError("Amadeus credentials not configured. Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in .env.")
            raise ProviderConfigurationError("Live API calls to Amadeus Hotel disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
