"""Tests for Provider Hub, ProviderRegistry, and modular travel providers."""

import pytest
from ultimate_travel_agent.integrations import (
    AmadeusFlightProvider,
    AmadeusHotelProvider,
    AvailabilityStatus,
    GetYourGuideActivityProvider,
    MockAccommodationProvider,
    MockActivityProvider,
    MockCurrencyProvider,
    MockFlightProvider,
    MockGuideProvider,
    MockMapsProvider,
    MockReviewProvider,
    MockTrainProvider,
    MockWeatherProvider,
    PriceStatus,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    ProviderRegistry,
    SocialDiscoveryProvider,
    StayAPIReviewProvider,
    default_registry,
)
from ultimate_travel_agent.models import VerificationLevel


def test_provider_registry_registration_and_listing() -> None:
    """Test registry contains default providers for all 10 categories."""
    categories = [
        "flight",
        "train",
        "hotel",
        "review",
        "activity",
        "map",
        "weather",
        "currency",
        "guide",
        "social",
    ]
    providers = default_registry.list_providers()
    assert len(providers) >= 15

    for cat in categories:
        provider = default_registry.get_default_provider(cat)
        assert provider is not None, f"Missing default provider for {cat}"
        assert provider.category.value == cat


def test_provider_health_check() -> None:
    """Test non-intrusive health inspection of providers."""
    mock_weather = default_registry.get_provider("mock_weather")
    assert mock_weather is not None
    health = mock_weather.health_check()
    assert health.status.value == "healthy"
    assert health.is_configured is True
    assert health.category == "weather"


def test_missing_credentials_in_live_mode_raises_clear_error() -> None:
    """Test that requesting live mode on an unconfigured provider raises ProviderConfigurationError."""
    amadeus = AmadeusFlightProvider(client_id="", client_secret="", mode=ProviderMode.OFFLINE)
    assert amadeus.is_configured() is False

    with pytest.raises(ProviderConfigurationError) as exc_info:
        amadeus.execute_query(mode="live", origin="PAR", destination="BCN")
    assert "not configured for live queries" in str(exc_info.value) or "credentials" in str(exc_info.value).lower()


def test_mock_flight_search_and_sorting() -> None:
    """Test mock flight provider sorting and parameters."""
    provider = MockFlightProvider()
    res = provider.search(
        origin="PAR",
        destination="BCN",
        departure_date="2026-10-15",
        return_date="2026-10-22",
        passengers=2,
        sort_by="price",
    )
    assert res.total_results >= 2
    assert res.items[0].price <= res.items[-1].price
    assert res.items[0].requires_booking_verification is True
    assert "airfrance" in res.items[0].source_url or "vueling" in res.items[0].source_url or "iberia" in res.items[0].source_url

    # Sort by comfort
    res_comfort = provider.search(origin="PAR", destination="BCN", sort_by="comfort")
    assert res_comfort.items[0].rating >= res_comfort.items[-1].rating


def test_mock_train_door_to_door() -> None:
    """Test mock train provider includes door-to-door transit modeling."""
    provider = MockTrainProvider()
    res = provider.search(origin="Paris", destination="Barcelona")
    assert res.total_results >= 1
    item = res.items[0]
    assert "door-to-door" in item.description.lower()
    assert item.details["door_to_door_minutes"] > item.details["duration_minutes"]
    assert item.source_url == "https://www.sncf-connect.com"
    assert item.requires_booking_verification is True


def test_mock_accommodation_quiet_neighborhood_and_no_booking() -> None:
    """Test accommodation provider curates quiet areas and forbids booking."""
    provider = MockAccommodationProvider()
    res = provider.search(city="Barcelona", neighborhood="Gràcia")
    assert res.total_results >= 1
    assert "Gràcia" in res.items[0].title or "Gràcia" in res.items[0].description
    assert res.items[0].requires_booking_verification is True
    # Ensure no booking method exists
    assert not hasattr(provider, "book")
    assert not hasattr(provider, "reserve")


def test_stayapi_review_only_contract() -> None:
    """Test StayAPI is documented and configured strictly for reviews, not booking."""
    provider = StayAPIReviewProvider()
    assert provider.category == ProviderCategory.REVIEW
    assert "booking" not in provider.capabilities
    assert "reviews" in provider.capabilities[0]
    res = provider.search(hotel_name="Casa Bonay", city="Barcelona")
    assert res.items[0].rating >= 4.0
    assert "StayAPI" in res.items[0].title


def test_mock_activity_nine_dimensions_and_rain_plan_b() -> None:
    """Test activity curator covers indoor/outdoor, rain plan B, and anti-crowd strategy."""
    provider = MockActivityProvider()
    res = provider.search(city="Barcelona", category="culture")
    assert res.total_results >= 1
    item = res.items[0]
    assert item.details["anti_crowd_strategy"] is not None
    assert item.details["weather_alternative"] is not None
    assert item.details["closure_alternative"] is not None
    assert item.details["booking_required"] is True
    assert item.price_status == PriceStatus.CONFIRMED.value


def test_mock_maps_routing_matrix_and_overload_detection() -> None:
    """Test maps provider computes distance, city matrix, and detects daily transit overload."""
    provider = MockMapsProvider()

    # Short route
    route = provider.calculate_route("Paris", "Lyon")
    assert route["distance_km"] > 300
    assert route["is_transit_overloaded"] is True  # Driving > 240 min

    # Intra-city
    intra = provider.calculate_route("Sagrada Familia", "Park Guell")
    assert intra["distance_km"] <= 15
    assert intra["is_transit_overloaded"] is False

    # Matrix
    matrix = provider.create_city_matrix(["Paris", "Lyon", "Barcelona"])
    assert matrix["Paris"]["Lyon"] > 0
    assert matrix["Paris"]["Paris"] == 0.0

    # Stage order suggestion (greedy TSP)
    ordered = provider.suggest_stage_order(["Paris", "Barcelona", "Perpignan", "Lyon"], start_stage="Paris")
    assert ordered[0] == "Paris"
    assert len(ordered) == 4


def test_mock_weather_rain_plan_b_trigger() -> None:
    """Test weather provider triggers indoor plan B on high precipitation risk."""
    provider = MockWeatherProvider()
    # Reykjavik has brisk rain risk in autumn
    res_reyk = provider.search(city="Reykjavík")
    assert res_reyk.items[0].details["indoor_plan_b_needed"] is True
    assert len(res_reyk.warnings) >= 1
    assert "Plan B" in res_reyk.warnings[0]

    # Barcelona has pleasant sunshine
    res_bcn = provider.search(city="Barcelona")
    assert res_bcn.items[0].details["indoor_plan_b_needed"] is False


def test_currency_converter_and_outdated_detection() -> None:
    """Test currency converter publishes rate date and handles unknown currency."""
    provider = MockCurrencyProvider()
    res = provider.search(amount=100.0, from_currency="EUR", to_currency="USD")
    assert res.items[0].details["rate_date"] == "2026-09-01"
    assert res.items[0].price == 108.0

    # Unknown currency
    res_unk = provider.search(amount=50.0, from_currency="XYZ", to_currency="EUR")
    assert len(res_unk.warnings) >= 1
    assert "XYZ" in res_unk.warnings[0]
    assert res_unk.items[0].price == 50.0


def test_social_discovery_strict_unverified_tagging() -> None:
    """Test social discovery is strictly tagged social_discovery_only with unverified pricing."""
    provider = SocialDiscoveryProvider()
    res = provider.search(city="Barcelona")
    assert res.total_results >= 1
    for item in res.items:
        assert item.verification_level == VerificationLevel.SOCIAL_DISCOVERY_ONLY.value
        assert item.price_status == PriceStatus.NEEDS_VERIFICATION.value
        assert item.availability_status == AvailabilityStatus.UNKNOWN.value
        assert item.requires_booking_verification is True
    assert any("SOCIAL DISCOVERY WARNING" in w for w in res.warnings)


def test_mock_provider_rejects_live_mode() -> None:
    """Test that mock providers refuse to execute in live mode to avoid false live claims."""
    mock_flight = MockFlightProvider()
    with pytest.raises(ProviderConfigurationError) as exc_info:
        mock_flight.execute_query(mode="live", origin="PAR", destination="BCN")
    assert "Mock provider" in str(exc_info.value)
    assert "cannot execute in live mode" in str(exc_info.value)


def test_registry_live_mode_routes_to_live_candidate() -> None:
    """Test that registry search in live mode routes to live provider and raises clear error if unconfigured."""
    with pytest.raises(ProviderConfigurationError) as exc_flight:
        default_registry.search(category=ProviderCategory.FLIGHT, mode="live", origin="PAR", destination="BCN")
    assert "amadeus_flight" in str(exc_flight.value)

    with pytest.raises(ProviderConfigurationError) as exc_train:
        default_registry.search(category=ProviderCategory.TRAIN, mode="live", origin="PAR", destination="BCN", date="2026-10-15")
    assert "sncf_train" in str(exc_train.value)


def test_keyless_providers_require_activation_for_live_mode() -> None:
    """Test that keyless providers (ECB, Wikivoyage, Open-Meteo) require explicit activation for live calls."""
    from ultimate_travel_agent.integrations import ECBCurrencyProvider, OpenMeteoProvider, WikivoyageProvider

    ecb = ECBCurrencyProvider()
    with pytest.raises(ProviderConfigurationError) as exc_ecb:
        ecb.execute_query(mode="live", amount=100.0, from_currency="EUR", to_currency="USD")
    assert "not configured" in str(exc_ecb.value) or "not activated" in str(exc_ecb.value)

    wiki = WikivoyageProvider()
    with pytest.raises(ProviderConfigurationError) as exc_wiki:
        wiki.execute_query(mode="live", city="Paris")
    assert "not configured" in str(exc_wiki.value) or "not activated" in str(exc_wiki.value)

