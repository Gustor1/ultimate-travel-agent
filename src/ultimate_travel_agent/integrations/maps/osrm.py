"""OSRM (Open Source Routing Machine) local or remote provider."""

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


class OSRMProvider(Provider):
    """OSRM provider for offline or self-hosted road route calculations (BSD 2-Clause)."""

    def __init__(
        self,
        backend_url: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="osrm",
            category=ProviderCategory.MAP,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["routing", "distance_matrix", "table", "offline_capable"],
        )
        self.backend_url = backend_url or os.getenv("OSRM_BACKEND_URL", "http://localhost:5000")
        self._mock_delegate = MockMapsProvider(mode=mode)

    def is_configured(self) -> bool:
        return os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "OSRM backend routing service is not activated. Set ENABLE_LIVE_KEYLESS_APIS=true in .env or run in offline/mock mode."
                )
            raise ProviderConfigurationError("Live API calls to OSRM disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
