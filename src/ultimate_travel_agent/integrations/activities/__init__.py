"""Activity and excursions integrations package."""

from ultimate_travel_agent.integrations.activities.adapter import ActivityAdapter
from ultimate_travel_agent.integrations.activities.getyourguide import GetYourGuideActivityProvider
from ultimate_travel_agent.integrations.activities.mock import MockActivityProvider
from ultimate_travel_agent.integrations.activities.opentripmap import OpenTripMapActivityProvider
from ultimate_travel_agent.integrations.activities.viator import ViatorActivityProvider

__all__ = [
    "ActivityAdapter",
    "GetYourGuideActivityProvider",
    "MockActivityProvider",
    "OpenTripMapActivityProvider",
    "ViatorActivityProvider",
]
