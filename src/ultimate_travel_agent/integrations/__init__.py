"""Optional external integrations package for ultimate-travel-agent."""

from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.integrations.weather import WeatherAdapter
from ultimate_travel_agent.integrations.routing import RoutingAdapter
from ultimate_travel_agent.integrations.currency import CurrencyAdapter
from ultimate_travel_agent.integrations.flights import FlightAdapter
from ultimate_travel_agent.integrations.trains import TrainAdapter
from ultimate_travel_agent.integrations.hotels import HotelAdapter
from ultimate_travel_agent.integrations.activities import ActivityAdapter
from ultimate_travel_agent.integrations.reviews import ReviewAdapter
from ultimate_travel_agent.integrations.guides import GuideAdapter
from ultimate_travel_agent.integrations.social_discovery import SocialDiscoveryAdapter

__all__ = [
    "ActivityAdapter",
    "BaseIntegrationAdapter",
    "CurrencyAdapter",
    "FlightAdapter",
    "GuideAdapter",
    "HotelAdapter",
    "ReviewAdapter",
    "RoutingAdapter",
    "SocialDiscoveryAdapter",
    "TrainAdapter",
    "WeatherAdapter",
]
