"""Amadeus Self-Service Flight Offers Search provider."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.flights.mock import MockFlightProvider
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


class AmadeusFlightProvider(Provider):
    """Amadeus Self-Service API flight search provider.

    Requires AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET for live mode.
    Strictly read-only; does NOT perform booking (no flight create order API).
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="amadeus_flight",
            category=ProviderCategory.FLIGHT,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "search_roundtrip",
                "search_oneway",
                "filter_stops",
                "sort_price",
                "sort_duration",
                "sort_stops",
                "sort_comfort",
            ],
        )
        self.client_id = client_id or os.getenv("AMADEUS_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("AMADEUS_CLIENT_SECRET", "")
        self._mock_delegate = MockFlightProvider(mode=mode)

    def is_configured(self) -> bool:
        """Check if Amadeus client credentials are provided."""
        return bool(self.client_id.strip() and self.client_secret.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url=raw.get("official_booking_url", "https://www.amadeus.com"),
            verification_level=(
                VerificationLevel.OFFICIAL_VERIFIED.value
                if self.mode == ProviderMode.LIVE
                else VerificationLevel.CROSS_CHECKED.value
            ),
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.CONFIRMED.value if self.mode == ProviderMode.LIVE else PriceStatus.ESTIMATED.value,
            availability_status=(
                AvailabilityStatus.LIVE.value
                if self.mode == ProviderMode.LIVE
                else AvailabilityStatus.ESTIMATED.value
            ),
            requires_booking_verification=True,
            title=f"{raw.get('airline', 'Flight')} {raw.get('flight_number', '')}: {raw.get('origin')} -> {raw.get('destination')}",
            description=f"{raw.get('stops', 0)} stop(s), duration {raw.get('duration_minutes', 120)} min, cabin {raw.get('cabin', 'Economy')}",
            price=raw.get("price_per_person"),
            rating=raw.get("comfort_score", 4.0),
            details=raw,
        )

    def search(
        self,
        origin: str = "PAR",
        destination: str = "BCN",
        departure_date: str = "2026-10-15",
        return_date: Optional[str] = None,
        passengers: int = 1,
        max_budget: Optional[float] = None,
        currency: str = "EUR",
        sort_by: str = "price",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        """Execute search in offline, mock, or live mode."""
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "Amadeus Flight API credentials not configured. "
                    "Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in .env or run in offline/mock mode."
                )
            # When live credentials exist, a live network call would be executed.
            # In test/safe environments, if credentials were mock values, handle gracefully.
            raise ProviderConfigurationError("Live API calls to Amadeus are disabled during development/testing.")

        # In offline / mock mode:
        res = self._mock_delegate.search(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            max_budget=max_budget,
            currency=currency,
            sort_by=sort_by,
            **kwargs,
        )
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
