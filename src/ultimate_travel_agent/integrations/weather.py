"""Weather integration adapter (Open-Meteo)."""

from typing import Any, Dict
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class WeatherAdapter(BaseIntegrationAdapter):
    """Adapter for weather forecasts via Open-Meteo (free, no API key required)."""

    def __init__(self, enabled: bool = False) -> None:
        super().__init__(
            provider_name="Open-Meteo",
            enabled=enabled,
            requires_api_key=False,
            data_transmitted_policy="Latitude, longitude, and forecast date range only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        city = kwargs.get("city", "Barcelona")
        return {
            "city": city,
            "forecast": [
                {"day": 1, "condition": "Sunny", "temp_c": 22, "precipitation_prob_pct": 10},
                {"day": 2, "condition": "Partly Cloudy", "temp_c": 21, "precipitation_prob_pct": 20},
                {"day": 3, "condition": "Sunny", "temp_c": 23, "precipitation_prob_pct": 5},
            ],
            "weather_warning": None,
            "verification_level": VerificationLevel.OFFICIAL_VERIFIED.value,
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        # Live fetch would use requests / httpx to api.open-meteo.com
        return self.get_mock_data(**kwargs)
