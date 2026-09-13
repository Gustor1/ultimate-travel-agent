"""Tests for external service adapters and graceful mock fallback."""

import pytest
from ultimate_travel_agent.integrations import (
    ActivityAdapter,
    CurrencyAdapter,
    FlightAdapter,
    GuideAdapter,
    HotelAdapter,
    ReviewAdapter,
    RoutingAdapter,
    SocialDiscoveryAdapter,
    TrainAdapter,
    WeatherAdapter,
)
from ultimate_travel_agent.models import VerificationLevel


def test_weather_adapter_mock_fallback() -> None:
    """Test weather adapter fallback returns expected mock structure."""
    adapter = WeatherAdapter(enabled=False)
    data = adapter.execute(city="Barcelona")
    assert data["city"] == "Barcelona"
    assert len(data["forecast"]) == 3
    assert "mock fallback" in data["_source"]


def test_routing_adapter_mock_fallback() -> None:
    """Test routing adapter fallback calculation."""
    adapter = RoutingAdapter(enabled=False)
    data = adapter.execute(origin="Station A", destination="Station B")
    assert data["distance_km"] > 0
    assert data["walking_time_minutes"] > 0
    assert data["transit_time_minutes"] > 0


def test_currency_adapter_conversion() -> None:
    """Test static currency conversion rates."""
    adapter = CurrencyAdapter(enabled=False)
    res = adapter.execute(from_currency="EUR", to_currency="USD")
    assert res["from_currency"] == "EUR"
    assert res["to_currency"] == "USD"
    assert res["rate"] == 1.08
    assert res["verification_level"] == VerificationLevel.OFFICIAL_VERIFIED.value
    assert res["warning"] is None


def test_currency_adapter_unknown_currency() -> None:
    """Test that exotic/unknown currency falls back to 1.0 with unverified level and warning."""
    adapter = CurrencyAdapter(enabled=False)
    res = adapter.execute(from_currency="XYZ", to_currency="EUR")
    assert res["from_currency"] == "XYZ"
    assert res["to_currency"] == "EUR"
    assert res["rate"] == 1.0
    assert res["verification_level"] == VerificationLevel.UNVERIFIED.value
    assert "XYZ" in str(res["warning"])


def test_guide_adapter_mock_fallback() -> None:
    """Test guidebook editorial mock adapter."""
    adapter = GuideAdapter(enabled=False)
    data = adapter.execute(city="Barcelona")
    assert data["city"] == "Barcelona"
    assert len(data["sections"]) >= 2
    assert any("Etiquette" in s["topic"] for s in data["sections"])
    assert data["verification_level"] == VerificationLevel.CROSS_CHECKED.value


def test_flight_adapter_disabled_and_missing_key() -> None:
    """Test flight adapter handles disabled state and missing keys gracefully."""
    adapter = FlightAdapter(enabled=False)
    data = adapter.execute(origin="PAR", destination="BCN")
    assert "mock fallback" in data["_source"]
    assert "sample_offers" in data
    assert "Manual booking required" in data["official_booking_notice"]

    # When enabled but missing key
    adapter_no_key = FlightAdapter(enabled=True, api_key=None)
    data2 = adapter_no_key.execute(origin="PAR", destination="BCN")
    assert "missing API key fallback" in data2["_source"]


def test_train_adapter_mock_fallback() -> None:
    """Test rail schedule mock adapter."""
    adapter = TrainAdapter(enabled=False)
    data = adapter.execute(origin="Paris", destination="Barcelona")
    assert len(data["train_options"]) >= 1
    assert "official_booking_url" in data["train_options"][0]


def test_hotel_adapter_mock_fallback() -> None:
    """Test hotel lookup mock adapter."""
    adapter = HotelAdapter(enabled=False)
    data = adapter.execute(city="Barcelona", neighborhood="Gràcia")
    assert len(data["curated_lodgings"]) >= 1
    assert "quietness_rating" in data["curated_lodgings"][0]


def test_activity_adapter_mock_fallback() -> None:
    """Test POI and activity mock adapter."""
    adapter = ActivityAdapter(enabled=False)
    data = adapter.execute(city="Barcelona")
    assert len(data["attractions"]) >= 2
    assert any(a["category"] == "culture" for a in data["attractions"])


def test_reviews_adapter_mock_fallback() -> None:
    """Test community review mock adapter."""
    adapter = ReviewAdapter(enabled=False)
    data = adapter.execute(venue="Sagrada Família")
    assert data["aggregate_rating"] >= 4.0
    assert data["verification_level"] == VerificationLevel.COMMUNITY_RECOMMENDED.value


def test_social_discovery_adapter_strict_verification_level() -> None:
    """Test that social discovery is strictly tagged as social_discovery_only."""
    adapter = SocialDiscoveryAdapter(enabled=False)
    data = adapter.execute(city="Barcelona")
    assert data["verification_level"] == VerificationLevel.SOCIAL_DISCOVERY_ONLY.value
    assert "social_trends" in data
