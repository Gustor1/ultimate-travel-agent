"""Booking.com partner demand API provider (prepared stub requiring B2B contract)."""

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


class BookingProvider(Provider):
    """Booking.com Affiliate / Demand API provider.

    Requires formal B2B partner approval and BOOKING_API_KEY.
    Strictly read-only; does NOT execute booking transactions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="booking_hotel",
            category=ProviderCategory.HOTEL,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=True,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["hotel_search", "availability_check", "neighborhood_filter"],
        )
        self.api_key = api_key or os.getenv("BOOKING_API_KEY", "")
        self._mock_delegate = MockAccommodationProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://www.booking.com",
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=raw.get("name", "Hotel"),
            description=f"Booking.com partner property",
            price=raw.get("price_per_night"),
            rating=raw.get("rating", 4.2),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "Booking.com Demand API is not configured. Formal B2B partnership and BOOKING_API_KEY required."
                )
            raise ProviderConfigurationError("Live API calls to Booking.com disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
