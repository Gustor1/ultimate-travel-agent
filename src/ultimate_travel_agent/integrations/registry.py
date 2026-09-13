"""Provider Registry: Central hub managing and querying travel data integrations."""

import os
from pathlib import Path
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

PROVIDER_ALIASES: Dict[str, str] = {
    # Flights
    "amadeus": "amadeus_flight",
    "amadeus_flight": "amadeus_flight",
    "aviation_edge": "aviation_edge",
    "aviationedge": "aviation_edge",
    "mock_flight": "mock_flight",
    # Trains
    "sncf": "sncf_train",
    "sncf_train": "sncf_train",
    "navitia": "navitia_train",
    "mock_train": "mock_train",
    # Accommodations
    "amadeus_hotels": "amadeus_hotel",
    "amadeus_hotel": "amadeus_hotel",
    "booking": "booking",
    "mock_hotel": "mock_accommodation",
    "mock_accommodation": "mock_accommodation",
    # Reviews
    "stayapi": "stayapi_review",
    "stayapi_review": "stayapi_review",
    "tripadvisor": "tripadvisor_review",
    "tripadvisor_review": "tripadvisor_review",
    "mock_review": "mock_review",
    # Activities
    "viator": "viator_activity",
    "viator_activity": "viator_activity",
    "getyourguide": "getyourguide_activity",
    "opentripmap": "opentripmap_activity",
    "mock_activity": "mock_activity",
    # Maps
    "openrouteservice": "openrouteservice",
    "ors": "openrouteservice",
    "google": "google_maps",
    "google_maps": "google_maps",
    "osrm": "osrm",
    "nominatim": "nominatim",
    "mock_maps": "mock_maps",
    # Weather
    "open_meteo": "open_meteo",
    "openmeteo": "open_meteo",
    "openweathermap": "openweathermap",
    "mock_weather": "mock_weather",
    # Currency
    "ecb": "ecb_currency",
    "ecb_currency": "ecb_currency",
    "mock_currency": "mock_currency",
    # Guides
    "wikivoyage": "wikivoyage",
    "mock_guide": "mock_guide",
    # Social
    "social_discovery": "social_discovery",
}

CATEGORY_ENV_VARS: Dict[str, List[str]] = {
    "flight": ["TRAVEL_PROVIDER_FLIGHTS", "TRAVEL_PROVIDER_FLIGHT"],
    "train": ["TRAVEL_PROVIDER_TRAINS", "TRAVEL_PROVIDER_TRAIN"],
    "hotel": [
        "TRAVEL_PROVIDER_HOTELS",
        "TRAVEL_PROVIDER_HOTEL",
        "TRAVEL_PROVIDER_ACCOMMODATIONS",
        "TRAVEL_PROVIDER_ACCOMMODATION",
    ],
    "review": ["TRAVEL_PROVIDER_REVIEWS", "TRAVEL_PROVIDER_REVIEW"],
    "activity": ["TRAVEL_PROVIDER_ACTIVITIES", "TRAVEL_PROVIDER_ACTIVITY"],
    "map": ["TRAVEL_PROVIDER_MAPS", "TRAVEL_PROVIDER_MAP"],
    "weather": ["TRAVEL_PROVIDER_WEATHER"],
    "currency": ["TRAVEL_PROVIDER_CURRENCY"],
    "guide": ["TRAVEL_PROVIDER_GUIDES", "TRAVEL_PROVIDER_GUIDE"],
    "social": ["TRAVEL_PROVIDER_SOCIAL", "TRAVEL_PROVIDER_SOCIAL_DISCOVERY"],
}


class ProviderRegistry:
    """Registry managing travel integration providers across offline, mock, and live modes."""

    def __init__(self) -> None:
        self._providers: Dict[str, Provider] = {}
        self._category_defaults: Dict[str, str] = {}
        self._category_live_defaults: Dict[str, str] = {}

    def register(
        self,
        provider: Provider,
        is_default_for_category: bool = False,
        is_live_default: bool = False,
    ) -> None:
        """Register a provider instance."""
        cat_str = provider.category.value if isinstance(provider.category, ProviderCategory) else str(provider.category)
        self._providers[provider.name] = provider

        is_mock = getattr(provider, "is_mock", False) or "mock" in provider.name.lower() or provider.name == "social_discovery"

        if is_default_for_category or (is_mock and cat_str not in self._category_defaults):
            self._category_defaults[cat_str] = provider.name

        if is_live_default or (not is_mock and cat_str not in self._category_live_defaults):
            self._category_live_defaults[cat_str] = provider.name

    def get_provider(self, name: str) -> Optional[Provider]:
        """Retrieve provider by unique name or registered alias."""
        if name in self._providers:
            return self._providers[name]
        alias = PROVIDER_ALIASES.get(name.lower())
        if alias and alias in self._providers:
            return self._providers[alias]
        return None

    def get_default_provider(
        self,
        category: Union[ProviderCategory, str],
        mode: Optional[Union[ProviderMode, str]] = None,
    ) -> Optional[Provider]:
        """Retrieve default registered provider for a category based on mode and server config."""
        cat_str = category.value if isinstance(category, ProviderCategory) else str(category)
        mode_str = mode.value if isinstance(mode, ProviderMode) else str(mode or "").lower()

        # 1. Check environment variable override for this category
        env_vars = CATEGORY_ENV_VARS.get(cat_str.lower(), [])
        for env_var in env_vars:
            val = os.environ.get(env_var)
            if val:
                prov = self.get_provider(val)
                if prov:
                    return prov

        # 2. Check live defaults when in live mode
        if mode_str == "live":
            default_live = self._category_live_defaults.get(cat_str)
            if default_live and default_live in self._providers:
                return self._providers[default_live]

        # 3. Category default (mock/offline fallback)
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
        """Execute search using named provider or category default for specified mode."""
        cat_str = category.value if isinstance(category, ProviderCategory) else str(category)
        if provider_name:
            target_provider = self.get_provider(provider_name)
            if not target_provider:
                raise KeyError(f"Provider '{provider_name}' not found in registry.")
        else:
            target_provider = self.get_default_provider(cat_str, mode=mode)

        if not target_provider:
            raise ProviderConfigurationError(f"No provider available for category '{cat_str}'.")

        return target_provider.execute_query(mode=mode, **kwargs)

    def load_config_file(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Apply provider configuration from a YAML file."""
        target = Path(config_path) if config_path else Path("config/providers.yaml")
        if not target.exists():
            return
        try:
            import yaml
            with open(target, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            providers_cfg = data.get("providers", {})
            for cat, details in providers_cfg.items():
                active = details.get("active_provider")
                if active:
                    norm_cat = cat.lower()
                    if norm_cat in ("flights", "flight"):
                        cat_key = "flight"
                    elif norm_cat in ("trains", "train"):
                        cat_key = "train"
                    elif norm_cat in ("accommodations", "hotels", "hotel", "accommodation"):
                        cat_key = "hotel"
                    elif norm_cat in ("reviews", "review"):
                        cat_key = "review"
                    elif norm_cat in ("activities", "activity"):
                        cat_key = "activity"
                    elif norm_cat in ("maps", "map"):
                        cat_key = "map"
                    else:
                        cat_key = norm_cat

                    prov = self.get_provider(active)
                    if prov:
                        self._category_defaults[cat_key] = prov.name
                        self._category_live_defaults[cat_key] = prov.name
        except Exception:
            pass


def create_default_registry() -> ProviderRegistry:
    """Initialize and populate the default travel provider registry."""
    registry = ProviderRegistry()

    # 1. Flights
    mock_flight = MockFlightProvider()
    amadeus_flight = AmadeusFlightProvider()
    aviation_edge = AviationEdgeFlightProvider()
    registry.register(mock_flight, is_default_for_category=True)
    registry.register(amadeus_flight, is_live_default=True)
    registry.register(aviation_edge)

    # 2. Trains
    mock_train = MockTrainProvider()
    sncf_train = SNCFTrainProvider()
    navitia_train = NavitiaTrainProvider()
    registry.register(mock_train, is_default_for_category=True)
    registry.register(sncf_train, is_live_default=True)
    registry.register(navitia_train)

    # 3. Accommodations
    mock_hotel = MockAccommodationProvider()
    amadeus_hotel = AmadeusHotelProvider()
    booking_hotel = BookingProvider()
    registry.register(mock_hotel, is_default_for_category=True)
    registry.register(amadeus_hotel, is_live_default=True)
    registry.register(booking_hotel)

    # 4. Reviews
    mock_review = MockReviewProvider()
    stayapi_review = StayAPIReviewProvider()
    tripadvisor_review = TripadvisorReviewProvider()
    registry.register(mock_review, is_default_for_category=True)
    registry.register(stayapi_review, is_live_default=True)
    registry.register(tripadvisor_review)

    # 5. Activities
    mock_activity = MockActivityProvider()
    gyg_activity = GetYourGuideActivityProvider()
    viator_activity = ViatorActivityProvider()
    opentripmap_activity = OpenTripMapActivityProvider()
    registry.register(mock_activity, is_default_for_category=True)
    registry.register(gyg_activity, is_live_default=True)
    registry.register(viator_activity)
    registry.register(opentripmap_activity)

    # 6. Maps & Routes
    mock_maps = MockMapsProvider()
    google_maps = GoogleMapsRoutesProvider()
    ors = OpenRouteServiceProvider()
    osrm = OSRMProvider()
    nominatim = NominatimProvider()
    registry.register(mock_maps, is_default_for_category=True)
    registry.register(google_maps, is_live_default=True)
    registry.register(ors)
    registry.register(osrm)
    registry.register(nominatim)

    # 7. Weather
    mock_weather = MockWeatherProvider()
    openweather = OpenWeatherMapProvider()
    open_meteo = OpenMeteoProvider()
    registry.register(mock_weather, is_default_for_category=True)
    registry.register(openweather, is_live_default=True)
    registry.register(open_meteo)

    # 8. Currency
    mock_currency = MockCurrencyProvider()
    ecb_currency = ECBCurrencyProvider()
    registry.register(mock_currency, is_default_for_category=True)
    registry.register(ecb_currency, is_live_default=True)

    # 9. Guides
    mock_guide = MockGuideProvider()
    wikivoyage = WikivoyageProvider()
    registry.register(mock_guide, is_default_for_category=True)
    registry.register(wikivoyage, is_live_default=True)

    # 10. Social Discovery
    social_discovery = SocialDiscoveryProvider()
    registry.register(social_discovery, is_default_for_category=True)

    # Check for optional YAML configuration override
    cfg_file = os.environ.get("TRAVEL_PROVIDERS_CONFIG") or "config/providers.yaml"
    registry.load_config_file(cfg_file)

    return registry


# Global default registry instance
default_registry = create_default_registry()
