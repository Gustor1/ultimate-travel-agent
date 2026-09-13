"""Provider Registry: Central hub managing and querying travel data integrations."""

from typing import Any, Dict, List, Optional, Union
from ultimate_travel_agent.integrations.accommodation import (
    AmadeusHotelProvider,
    BookingProvider,
    MockAccommodationProvider,
)
from ultimate_travel_agent.integrations.activities import (
    GetYourGuideActivityProvider,
    MockActivityProvider,
    OpenTripMapActivityProvider,
    ViatorActivityProvider,
)
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.currency import (
    ECBCurrencyProvider,
    MockCurrencyProvider,
)
from ultimate_travel_agent.integrations.flights import (
    AmadeusFlightProvider,
    AviationEdgeFlightProvider,
    MockFlightProvider,
)
from ultimate_travel_agent.integrations.guides import (
    MockGuideProvider,
    WikivoyageProvider,
)
from ultimate_travel_agent.integrations.maps import (
    GoogleMapsRoutesProvider,
    MockMapsProvider,
    NominatimProvider,
    OpenRouteServiceProvider,
    OSRMProvider,
)
from ultimate_travel_agent.integrations.models import (
    HealthCheckResult,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    ProviderSearchResult,
)
from ultimate_travel_agent.integrations.reviews import (
    MockReviewProvider,
    StayAPIReviewProvider,
    TripadvisorReviewProvider,
)
from ultimate_travel_agent.integrations.social_discovery import SocialDiscoveryProvider
from ultimate_travel_agent.integrations.trains import (
    MockTrainProvider,
    NavitiaTrainProvider,
    SNCFTrainProvider,
)
from ultimate_travel_agent.integrations.weather import (
    MockWeatherProvider,
    OpenMeteoProvider,
    OpenWeatherMapProvider,
)


class ProviderRegistry:
    """Registry managing travel integration providers across offline, mock, and live modes."""

    def __init__(self) -> None:
        self._providers: Dict[str, Provider] = {}
        self._category_defaults: Dict[str, str] = {}

    def register(self, provider: Provider, is_default_for_category: bool = False) -> None:
        """Register a provider instance."""
        cat_str = provider.category.value if isinstance(provider.category, ProviderCategory) else str(provider.category)
        self._providers[provider.name] = provider
        if is_default_for_category or cat_str not in self._category_defaults:
            self._category_defaults[cat_str] = provider.name

    def get_provider(self, name: str) -> Optional[Provider]:
        """Retrieve provider by unique name."""
        return self._providers.get(name)

    def get_default_provider(self, category: Union[ProviderCategory, str]) -> Optional[Provider]:
        """Retrieve default registered provider for a category."""
        cat_str = category.value if isinstance(category, ProviderCategory) else str(category)
        default_name = self._category_defaults.get(cat_str)
        if default_name:
            return self._providers.get(default_name)
        return None

    def list_providers(
        self,
        category: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List summary info for all registered providers."""
        results = []
        for p in self._providers.values():
            cat_str = p.category.value if isinstance(p.category, ProviderCategory) else str(p.category)
            mode_str = p.mode.value if isinstance(p.mode, ProviderMode) else str(p.mode)

            if category and cat_str.lower() != category.lower():
                continue
            if mode and mode_str.lower() != mode.lower():
                continue

            results.append({
                "name": p.name,
                "category": cat_str,
                "mode": mode_str,
                "is_configured": p.is_configured(),
                "requires_api_key": p.requires_api_key,
                "requires_partner_approval": p.requires_partner_approval,
                "requires_payment_setup": p.requires_payment_setup,
                "privacy_level": p.privacy_level,
                "capabilities": p.capabilities,
                "supported_countries": p.supported_countries,
            })
        return results

    def get_provider_status(self, name: str) -> HealthCheckResult:
        """Get the health and configuration status of a provider."""
        provider = self.get_provider(name)
        if not provider:
            raise KeyError(f"Provider '{name}' not found in registry.")
        return provider.health_check()

    def search(
        self,
        category: Union[ProviderCategory, str],
        provider_name: Optional[str] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> ProviderSearchResult:
        """Execute search using named provider or category default."""
        cat_str = category.value if isinstance(category, ProviderCategory) else str(category)
        target_provider = self.get_provider(provider_name) if provider_name else self.get_default_provider(cat_str)

        if not target_provider:
            raise ValueError(f"No provider available for category '{cat_str}'.")

        return target_provider.execute_query(mode=mode, **kwargs)


def create_default_registry() -> ProviderRegistry:
    """Initialize and populate the default travel provider registry."""
    registry = ProviderRegistry()

    # 1. Flights
    mock_flight = MockFlightProvider()
    amadeus_flight = AmadeusFlightProvider()
    aviation_edge = AviationEdgeFlightProvider()
    registry.register(mock_flight, is_default_for_category=True)
    registry.register(amadeus_flight)
    registry.register(aviation_edge)

    # 2. Trains
    mock_train = MockTrainProvider()
    sncf_train = SNCFTrainProvider()
    navitia_train = NavitiaTrainProvider()
    registry.register(mock_train, is_default_for_category=True)
    registry.register(sncf_train)
    registry.register(navitia_train)

    # 3. Accommodations
    mock_hotel = MockAccommodationProvider()
    amadeus_hotel = AmadeusHotelProvider()
    booking_hotel = BookingProvider()
    registry.register(mock_hotel, is_default_for_category=True)
    registry.register(amadeus_hotel)
    registry.register(booking_hotel)

    # 4. Reviews
    mock_review = MockReviewProvider()
    stayapi_review = StayAPIReviewProvider()
    tripadvisor_review = TripadvisorReviewProvider()
    registry.register(mock_review, is_default_for_category=True)
    registry.register(stayapi_review)
    registry.register(tripadvisor_review)

    # 5. Activities
    mock_activity = MockActivityProvider()
    gyg_activity = GetYourGuideActivityProvider()
    viator_activity = ViatorActivityProvider()
    opentripmap_activity = OpenTripMapActivityProvider()
    registry.register(mock_activity, is_default_for_category=True)
    registry.register(gyg_activity)
    registry.register(viator_activity)
    registry.register(opentripmap_activity)

    # 6. Maps & Routes
    mock_maps = MockMapsProvider()
    osrm = OSRMProvider()
    ors = OpenRouteServiceProvider()
    nominatim = NominatimProvider()
    google_maps = GoogleMapsRoutesProvider()
    registry.register(mock_maps, is_default_for_category=True)
    registry.register(osrm)
    registry.register(ors)
    registry.register(nominatim)
    registry.register(google_maps)

    # 7. Weather
    mock_weather = MockWeatherProvider()
    open_meteo = OpenMeteoProvider()
    openweather = OpenWeatherMapProvider()
    registry.register(mock_weather, is_default_for_category=True)
    registry.register(open_meteo)
    registry.register(openweather)

    # 8. Currency
    mock_currency = MockCurrencyProvider()
    ecb_currency = ECBCurrencyProvider()
    registry.register(mock_currency, is_default_for_category=True)
    registry.register(ecb_currency)

    # 9. Guides
    mock_guide = MockGuideProvider()
    wikivoyage = WikivoyageProvider()
    registry.register(mock_guide, is_default_for_category=True)
    registry.register(wikivoyage)

    # 10. Social Discovery
    social_discovery = SocialDiscoveryProvider()
    registry.register(social_discovery, is_default_for_category=True)

    return registry


# Global default registry instance
default_registry = create_default_registry()
