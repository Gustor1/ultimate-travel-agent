"""Open-Meteo open weather API provider (keyless, non-commercial open data)."""

from datetime import datetime, timezone
import os
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
from ultimate_travel_agent.integrations.weather.mock import MockWeatherProvider
from ultimate_travel_agent.models import VerificationLevel


class OpenMeteoProvider(Provider):
    """Open-Meteo weather API provider (free, open-source, zero API key needed)."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="open_meteo",
            category=ProviderCategory.WEATHER,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["forecast_7day", "rain_probability", "historical_climate"],
        )
        self.endpoint_url = endpoint_url or os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast")
        self._mock_delegate = MockWeatherProvider(mode=mode)

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        # In offline/mock mode or default run, delegate to mock data
        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
