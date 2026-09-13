"""Google Maps Platform Routes API provider."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.maps.mock import MockMapsProvider
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


class GoogleMapsRoutesProvider(Provider):
    """Google Maps Platform Routes API provider (requires GOOGLE_MAPS_API_KEY)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="google_maps",
            category=ProviderCategory.MAP,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=True,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["routes", "distance_matrix", "places_geocode"],
        )
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
        self._mock_delegate = MockMapsProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError("Google Maps API key not configured. Set GOOGLE_MAPS_API_KEY in .env.")
            raise ProviderConfigurationError("Live API calls to Google Maps disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
