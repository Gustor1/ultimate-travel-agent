"""Pydantic v2 domain models for ultimate-travel-agent."""

from ultimate_travel_agent.models.enums import (
    AccommodationType,
    ActivityCategory,
    AgentStatus,
    ChecklistCategory,
    CrowdSensitivity,
    DifficultyLevel,
    EnvironmentType,
    PacingPreference,
    RouteOptionStatus,
    RoutePreference,
    RouteTransportMode,
    TransportMode,
    TravelerProfile,
    TripType,
    VerificationLevel,
)
from ultimate_travel_agent.models.source import SourceReference
from ultimate_travel_agent.models.traveler import Traveler
from ultimate_travel_agent.models.destination import Destination
from ultimate_travel_agent.models.transport import TransportSegment
from ultimate_travel_agent.models.route import InterCityRoute, RouteOption
from ultimate_travel_agent.models.accommodation import Accommodation
from ultimate_travel_agent.models.activity import Activity
from ultimate_travel_agent.models.checklist import ChecklistItem
from ultimate_travel_agent.models.budget import Budget, BudgetCategoryBreakdown
from ultimate_travel_agent.models.itinerary import DaySchedule, ItineraryItem
from ultimate_travel_agent.models.stage import TripStage
from ultimate_travel_agent.models.booking import BookingRequirement
from ultimate_travel_agent.models.agent_result import AgentResult
from ultimate_travel_agent.models.trip import Trip

__all__ = [
    "Accommodation",
    "AccommodationType",
    "Activity",
    "ActivityCategory",
    "AgentResult",
    "AgentStatus",
    "BookingRequirement",
    "Budget",
    "BudgetCategoryBreakdown",
    "ChecklistCategory",
    "ChecklistItem",
    "CrowdSensitivity",
    "Destination",
    "DaySchedule",
    "DifficultyLevel",
    "EnvironmentType",
    "InterCityRoute",
    "ItineraryItem",
    "PacingPreference",
    "RouteOption",
    "RouteOptionStatus",
    "RoutePreference",
    "RouteTransportMode",
    "SourceReference",
    "TransportMode",
    "TransportSegment",
    "Traveler",
    "TravelerProfile",
    "Trip",
    "TripStage",
    "TripType",
    "VerificationLevel",
]

