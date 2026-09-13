"""AviationEdge schedule and route lookup provider."""

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


class AviationEdgeFlightProvider(Provider):
    """AviationEdge flight schedule and airline tracker provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="aviation_edge",
            category=ProviderCategory.FLIGHT,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["search_schedules", "tracker", "route_verification"],
        )
        self.api_key = api_key or os.getenv("AVIATION_EDGE_API_KEY", "")
        self._mock_delegate = MockFlightProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://aviation-edge.com",
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=f"Flight {raw.get('flight_number', '')}: {raw.get('origin')} -> {raw.get('destination')}",
            description=f"Scheduled route via AviationEdge",
            price=raw.get("price_per_person"),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "AviationEdge API key not configured. Set AVIATION_EDGE_API_KEY in .env."
                )
            raise ProviderConfigurationError("Live API calls to AviationEdge disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
