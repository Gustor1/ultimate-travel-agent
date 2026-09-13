"""Travel Integrations and Provider Hub for ultimate-travel-agent."""

from ultimate_travel_agent.integrations.accommodation import (
    AmadeusHotelProvider,
    BookingProvider,
    HotelAdapter,
    MockAccommodationProvider,
)
from ultimate_travel_agent.integrations.activities import (
    ActivityAdapter,
    GetYourGuideActivityProvider,
    MockActivityProvider,
    OpenTripMapActivityProvider,
    ViatorActivityProvider,
)
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter, Provider
from ultimate_travel_agent.integrations.currency import (
    CurrencyAdapter,
    ECBCurrencyProvider,
    MockCurrencyProvider,
)
from ultimate_travel_agent.integrations.flights import (
    AmadeusFlightProvider,
    AviationEdgeFlightProvider,
    FlightAdapter,
    MockFlightProvider,
)
from ultimate_travel_agent.integrations.guides import (
    GuideAdapter,
    MockGuideProvider,
    WikivoyageProvider,
)
from ultimate_travel_agent.integrations.health import create_health_report
from ultimate_travel_agent.integrations.maps import (
    GoogleMapsRoutesProvider,
    MockMapsProvider,
    NominatimProvider,
    OpenRouteServiceProvider,
    OSRMProvider,
    RoutingAdapter,
)
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    HealthCheckResult,
    HealthStatus,
    PriceStatus,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderError,
    ProviderMode,
    ProviderNetworkError,
    ProviderResultItem,
    ProviderSearchResult,
)
from ultimate_travel_agent.integrations.registry import (
    ProviderRegistry,
    create_default_registry,
    default_registry,
)
from ultimate_travel_agent.integrations.reviews import (
    MockReviewProvider,
    ReviewAdapter,
    StayAPIReviewProvider,
    TripadvisorReviewProvider,
)
from ultimate_travel_agent.integrations.social_discovery import (
    SocialDiscoveryAdapter,
    SocialDiscoveryProvider,
)
from ultimate_travel_agent.integrations.trains import (
    MockTrainProvider,
    NavitiaTrainProvider,
    SNCFTrainProvider,
    TrainAdapter,
)
from ultimate_travel_agent.integrations.weather import (
    MockWeatherProvider,
    OpenMeteoProvider,
    OpenWeatherMapProvider,
    WeatherAdapter,
)

__all__ = [
    # Core interfaces and registry
    "BaseIntegrationAdapter",
    "Provider",
    "ProviderRegistry",
    "create_default_registry",
    "default_registry",
    "create_health_report",
    # Enums and models
    "ProviderMode",
    "ProviderCategory",
    "PriceStatus",
    "AvailabilityStatus",
    "HealthStatus",
    "HealthCheckResult",
    "ProviderResultItem",
    "ProviderSearchResult",
    "ProviderError",
    "ProviderConfigurationError",
    "ProviderNetworkError",
    # Legacy adapters (v1.0 backward compatibility)
    "ActivityAdapter",
    "CurrencyAdapter",
    "FlightAdapter",
    "GuideAdapter",
    "HotelAdapter",
    "ReviewAdapter",
    "RoutingAdapter",
    "SocialDiscoveryAdapter",
    "TrainAdapter",
    "WeatherAdapter",
    # Modular v1.2 Providers
    "AmadeusFlightProvider",
    "AviationEdgeFlightProvider",
    "MockFlightProvider",
    "SNCFTrainProvider",
    "NavitiaTrainProvider",
    "MockTrainProvider",
    "AmadeusHotelProvider",
    "BookingProvider",
    "MockAccommodationProvider",
    "StayAPIReviewProvider",
    "TripadvisorReviewProvider",
    "MockReviewProvider",
    "GetYourGuideActivityProvider",
    "ViatorActivityProvider",
    "OpenTripMapActivityProvider",
    "MockActivityProvider",
    "GoogleMapsRoutesProvider",
    "OSRMProvider",
    "OpenRouteServiceProvider",
    "NominatimProvider",
    "MockMapsProvider",
    "OpenMeteoProvider",
    "OpenWeatherMapProvider",
    "MockWeatherProvider",
    "ECBCurrencyProvider",
    "MockCurrencyProvider",
    "WikivoyageProvider",
    "MockGuideProvider",
    "SocialDiscoveryProvider",
]
