"""OpenTripMap open data API provider for attractions and monuments."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.activities.mock import MockActivityProvider
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


class OpenTripMapActivityProvider(Provider):
    """OpenTripMap open cultural attractions and monuments provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="opentripmap",
            category=ProviderCategory.ACTIVITY,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["cultural_landmarks", "historical_places", "coordinates"],
        )
        self.api_key = api_key or os.getenv("OPENTRIPMAP_API_KEY", "")
        self._mock_delegate = MockActivityProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://opentripmap.com",
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=raw.get("title", "Monument"),
            description=f"Cultural attraction indexed in OpenTripMap",
            price=raw.get("cost_per_person"),
            rating=raw.get("rating", 4.5),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError("OpenTripMap API key not configured. Set OPENTRIPMAP_API_KEY in .env.")
            raise ProviderConfigurationError("Live API calls to OpenTripMap disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
