"""Weather integrations package."""

from ultimate_travel_agent.integrations.weather.adapter import WeatherAdapter
from ultimate_travel_agent.integrations.weather.mock import MockWeatherProvider
from ultimate_travel_agent.integrations.weather.open_meteo import OpenMeteoProvider
from ultimate_travel_agent.integrations.weather.openweather import OpenWeatherMapProvider

__all__ = [
    "MockWeatherProvider",
    "OpenMeteoProvider",
    "OpenWeatherMapProvider",
    "WeatherAdapter",
]
