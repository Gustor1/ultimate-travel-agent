"""Train and rail transit integrations package."""

from ultimate_travel_agent.integrations.trains.adapter import TrainAdapter
from ultimate_travel_agent.integrations.trains.mock import MockTrainProvider
from ultimate_travel_agent.integrations.trains.navitia import NavitiaTrainProvider
from ultimate_travel_agent.integrations.trains.sncf import SNCFTrainProvider

__all__ = [
    "MockTrainProvider",
    "NavitiaTrainProvider",
    "SNCFTrainProvider",
    "TrainAdapter",
]
