"""Open-Meteo open weather and geocoding API provider (keyless, CC BY 4.0)."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.http_client import KeylessHttpClient
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    CacheStatus,
    PriceStatus,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
    ResultStatus,
)
from ultimate_travel_agent.integrations.weather.mock import MockWeatherProvider
from ultimate_travel_agent.models import VerificationLevel

OPEN_METEO_ATTRIBUTION = "Weather data by Open-Meteo.com under CC BY 4.0 (https://open-meteo.com/)"
OPEN_METEO_SOURCE_URL = "https://open-meteo.com/"

# WMO Weather interpretation codes (WW)
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    62: "Rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def interpret_weather_code(code: Optional[int]) -> str:
    """Return descriptive text for a WMO weather interpretation code."""
    if code is None:
        return "Unknown weather condition"
    return WMO_WEATHER_CODES.get(int(code), f"Weather code {code}")


class OpenMeteoProvider(Provider):
    """Open-Meteo weather and geocoding provider (free, open data, zero API key)."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        geocoding_url: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
        http_client: Optional[KeylessHttpClient] = None,
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
            capabilities=[
                "geocoding",
                "current_weather",
                "forecast_7day",
                "rain_probability",
                "outdoor_activity_advice",
                "indoor_plan_b",
            ],
        )
        self.endpoint_url = endpoint_url or os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast")
        self.geocoding_url = geocoding_url or os.getenv(
            "OPEN_METEO_GEOCODING_URL", "https://geocoding-api.open-meteo.com/v1/search"
        )
        self.http_client = http_client or KeylessHttpClient.get_instance()
        self._mock_delegate = MockWeatherProvider(mode=mode)

    def is_configured(self) -> bool:
        """Verify if keyless live access is activated via environment flags."""
        keyless_active = os.getenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "").lower() in ("true", "1", "yes") or \
                         os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")
        enabled = os.getenv("TRAVEL_MCP_ENABLE_OPEN_METEO", "true").lower() in ("true", "1", "yes")
        return keyless_active and enabled

    def geocode_destination(self, name: str) -> Optional[Dict[str, Any]]:
        """Geocode a city or destination name to latitude, longitude, and timezone."""
        if not name or not name.strip():
            return None

        clean_name = name.strip()
        data, _ = self.http_client.get(
            self.geocoding_url,
            params={"name": clean_name, "count": 1, "language": "en", "format": "json"},
            ttl_seconds=604800,  # 7 days cache for geocoding
            service_name="open_meteo",
            min_interval_seconds=0.2,
        )

        if isinstance(data, dict) and "results" in data and isinstance(data["results"], list) and data["results"]:
            top = data["results"][0]
            return {
                "name": top.get("name", clean_name),
                "latitude": float(top["latitude"]),
                "longitude": float(top["longitude"]),
                "country": top.get("country"),
                "country_code": top.get("country_code"),
                "timezone": top.get("timezone", "UTC"),
                "admin1": top.get("admin1"),
            }
        return None

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        """Execute weather query. In LIVE mode calls Open-Meteo; in OFFLINE/MOCK delegates to mock."""
        city = kwargs.get("city") or kwargs.get("destination") or kwargs.get("query") or "Paris"
        date_str = kwargs.get("date")
        days = int(kwargs.get("days") or 7)

        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "Open-Meteo live weather feed is disabled or unconfigured. "
                    "Set TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_OPEN_METEO=true in environment."
                )

            return self._fetch_live_forecast(city=city, date_str=date_str, days=days)

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        res.attribution = OPEN_METEO_ATTRIBUTION
        res.source_url = OPEN_METEO_SOURCE_URL
        res.cache_status = CacheStatus.HIT.value
        res.result_status = ResultStatus.NEEDS_VERIFICATION.value
        for it in res.items:
            it.provider = self.name
            it.attribution = OPEN_METEO_ATTRIBUTION
            it.source_url = OPEN_METEO_SOURCE_URL
        return res

    def _fetch_live_forecast(self, city: str, date_str: Optional[str] = None, days: int = 7) -> ProviderSearchResult:
        """Query live Open-Meteo APIs for geocoding, current conditions, and daily forecast."""
        geo = self.geocode_destination(city)
        if not geo:
            # Destination not found in geocoding; provide clear error-wrapped result
            return ProviderSearchResult(
                provider=self.name,
                category=self.category.value,
                mode=self.mode.value,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                query={"city": city, "date": date_str, "days": days},
                total_results=0,
                items=[],
                warnings=[f"Destination '{city}' could not be resolved by Open-Meteo geocoding."],
                attribution=OPEN_METEO_ATTRIBUTION,
                source_url=OPEN_METEO_SOURCE_URL,
                cache_status=CacheStatus.MISS.value,
                result_status=ResultStatus.UNAVAILABLE.value,
            )

        lat = geo["latitude"]
        lon = geo["longitude"]
        tz = geo.get("timezone", "auto")

        forecast_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": tz,
        }

        data, cache_status = self.http_client.get(
            self.endpoint_url,
            params=forecast_params,
            ttl_seconds=1800,  # 30 min cache
            service_name="open_meteo",
            min_interval_seconds=0.2,
        )

        items: List[ProviderResultItem] = []
        warnings: List[str] = []

        if not isinstance(data, dict):
            raise ProviderConfigurationError("Unexpected response structure received from Open-Meteo.")

        current = data.get("current", {})
        daily = data.get("daily", {})

        current_code = current.get("weather_code")
        current_temp = current.get("temperature_2m")
        current_precip = current.get("precipitation", 0.0)
        current_wind = current.get("wind_speed_10m", 0.0)
        current_desc = interpret_weather_code(current_code)

        # Current weather item
        curr_item = ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url=OPEN_METEO_SOURCE_URL,
            verification_level=VerificationLevel.OFFICIAL_VERIFIED.value,
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.LIVE.value,
            title=f"Current weather in {geo['name']} ({geo.get('country', '')})",
            description=f"{current_desc}, {current_temp}°C, Precipitation: {current_precip}mm, Wind: {current_wind} km/h",
            details={
                "type": "current",
                "city": geo["name"],
                "country": geo.get("country"),
                "latitude": lat,
                "longitude": lon,
                "timezone": tz,
                "temperature": current_temp,
                "weather_code": current_code,
                "condition": current_desc,
                "precipitation": current_precip,
                "wind_speed": current_wind,
            },
            attribution=OPEN_METEO_ATTRIBUTION,
            cache_status=cache_status,
            result_status=ResultStatus.LIVE.value,
        )
        items.append(curr_item)

        # Daily forecast items
        dates = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        precip_sum = daily.get("precipitation_sum", [])
        precip_prob = daily.get("precipitation_probability_max", [])
        w_codes = daily.get("weather_code", [])

        limit = min(days, len(dates))
        for i in range(limit):
            d_str = dates[i]
            code_i = w_codes[i] if i < len(w_codes) else None
            cond_i = interpret_weather_code(code_i)
            high_i = t_max[i] if i < len(t_max) else None
            low_i = t_min[i] if i < len(t_min) else None
            p_sum = precip_sum[i] if i < len(precip_sum) else 0.0
            p_prob = precip_prob[i] if i < len(precip_prob) else 0

            rain_risk = (p_prob is not None and p_prob >= 40) or (p_sum is not None and p_sum >= 2.0)
            if rain_risk:
                activity_advice = (
                    f"Rain risk detected ({p_prob}% probability, {p_sum}mm). "
                    "Indoor contingency Plan B (museums, indoor markets, cultural galleries) recommended."
                )
            else:
                activity_advice = (
                    f"Pleasant outdoor conditions expected ({cond_i}, {low_i}°C to {high_i}°C). "
                    "Outdoor sightseeing and walking tours recommended."
                )

            daily_item = ProviderResultItem(
                provider=self.name,
                category=self.category.value,
                mode=self.mode.value,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                source_url=OPEN_METEO_SOURCE_URL,
                verification_level=VerificationLevel.OFFICIAL_VERIFIED.value,
                title=f"Forecast for {d_str} in {geo['name']}",
                description=f"{cond_i} ({low_i}°C / {high_i}°C). {activity_advice}",
                details={
                    "type": "daily_forecast",
                    "date": d_str,
                    "city": geo["name"],
                    "weather_code": code_i,
                    "condition": cond_i,
                    "temp_min": low_i,
                    "temp_max": high_i,
                    "precipitation_sum_mm": p_sum,
                    "precipitation_probability_pct": p_prob,
                    "rain_risk": rain_risk,
                    "activity_advice": activity_advice,
                    "indoor_plan_b_recommended": rain_risk,
                },
                attribution=OPEN_METEO_ATTRIBUTION,
                cache_status=cache_status,
                result_status=ResultStatus.LIVE.value,
            )
            items.append(daily_item)

        if days > 7:
            warnings.append(
                "Forecasts beyond 7 days are subject to significant meteorological uncertainty; treat as estimates."
            )

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={"city": city, "date": date_str, "days": days},
            total_results=len(items),
            items=items,
            source_metadata={
                "provider": self.name,
                "category": self.category.value,
                "geocoding": geo,
                "attribution": OPEN_METEO_ATTRIBUTION,
                "source_url": OPEN_METEO_SOURCE_URL,
                "cache_status": cache_status,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            },
            warnings=warnings,
            requires_booking_verification=False,
            attribution=OPEN_METEO_ATTRIBUTION,
            cache_status=cache_status,
            result_status=ResultStatus.LIVE.value,
            source_url=OPEN_METEO_SOURCE_URL,
        )
