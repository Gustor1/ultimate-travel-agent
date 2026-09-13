"""Nominatim OpenStreetMap geocoding provider (free, rate-limited to 1 req/sec)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import os
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


class NominatimProvider(Provider):
    """Nominatim geocoding provider complying with OSM Usage Policy."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="nominatim",
            category=ProviderCategory.MAP,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["geocoding", "reverse_geocoding", "free_osm"],
        )
        self._mock_delegate = MockMapsProvider(mode=mode)

    def is_configured(self) -> bool:
        return os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "Nominatim live geocoding service is not activated. Set ENABLE_LIVE_KEYLESS_APIS=true in .env or run in offline/mock mode."
                )
            raise ProviderConfigurationError("Live API calls to Nominatim disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
