"""Deterministic offline weather outlook and indoor contingency provider."""

from datetime import datetime, timezone
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
from ultimate_travel_agent.models import VerificationLevel


class MockWeatherProvider(Provider):
    """Deterministic weather outlook and rainy-day indoor alternative suggester."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_weather",
            category=ProviderCategory.WEATHER,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "forecast_outlook",
                "historical_climate_profile",
                "precipitation_risk",
                "indoor_plan_b_trigger",
            ],
        )

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://open-meteo.com",
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=None,
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.LIVE.value,
            requires_booking_verification=False,
            title=f"Weather for {raw.get('city')}: {raw.get('summary')}",
            description=(
                f"High: {raw.get('temp_high_c')}°C, Low: {raw.get('temp_low_c')}°C, "
                f"Rain Risk: {raw.get('rain_probability_pct')}%. "
                f"Contingency: {raw.get('indoor_plan_b')}"
            ),
            price=None,
            details=raw,
        )

    def get_outlook(self, city: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Generate weather outlook with plan B suggestions."""
        import unicodedata
        city_lower = unicodedata.normalize('NFKD', city.strip()).encode('ASCII', 'ignore').decode('utf-8').lower()

        if "reykjavik" in city_lower or "iceland" in city_lower or "vik" in city_lower:
            return {
                "city": city,
                "date": date or "2026-10-15",
                "outlook_type": "historical_climate",
                "summary": "Subpolar oceanic: brisk winds and intermittent coastal rain",
                "temp_high_c": 7,
                "temp_low_c": 2,
                "rain_probability_pct": 65,
                "wind_speed_kmh": 35,
                "indoor_plan_b_needed": True,
                "indoor_plan_b": "Perlan Museum Wonders of Iceland, Laugardalslaug thermal pool, or Harpa concert hall.",
                "clothing_advice": "Waterproof windbreaker shell, thermal underlayers, and sturdy waterproof hiking boots.",
            }
        elif "barcelona" in city_lower or "spain" in city_lower:
            return {
                "city": city,
                "date": date or "2026-10-15",
                "outlook_type": "seasonal_forecast",
                "summary": "Mild Mediterranean autumn: pleasant sunshine and low cloud cover",
                "temp_high_c": 22,
                "temp_low_c": 15,
                "rain_probability_pct": 20,
                "wind_speed_kmh": 12,
                "indoor_plan_b_needed": False,
                "indoor_plan_b": "MNAC (Museu Nacional d'Art de Catalunya) or Picasso Museum in El Born.",
                "clothing_advice": "Breathable layers, comfortable walking sneakers, sunglasses, light evening jacket.",
            }
        else:
            return {
                "city": city,
                "date": date or "2026-10-15",
                "outlook_type": "seasonal_estimate",
                "summary": "Typical temperate seasonal conditions",
                "temp_high_c": 18,
                "temp_low_c": 10,
                "rain_probability_pct": 35,
                "wind_speed_kmh": 15,
                "indoor_plan_b_needed": False,
                "indoor_plan_b": "Municipal museum, historic library, or covered food market.",
                "clothing_advice": "Comfortable layers and compact travel umbrella.",
            }

    def search(
        self,
        city: str = "Barcelona",
        date: Optional[str] = None,
        **kwargs: Any,
    ) -> ProviderSearchResult:
        data = self.get_outlook(city, date)
        item = self.normalize_result(data)

        warnings = []
        if data.get("indoor_plan_b_needed"):
            warnings.append(f"Weather alert for {city}: {data['rain_probability_pct']}% rain risk. Indoor Plan B recommended.")

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={"city": city, "date": date},
            total_results=1,
            items=[item],
            source_metadata=self.get_source_metadata(),
            warnings=warnings,
            requires_booking_verification=False,
        )
