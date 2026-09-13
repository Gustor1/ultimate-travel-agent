"""Enumerations for the ultimate-travel-agent data models."""

from enum import Enum


class VerificationLevel(str, Enum):
    """Trust and verification levels for travel data."""

    OFFICIAL_VERIFIED = "official_verified"
    CROSS_CHECKED = "cross_checked"
    COMMUNITY_RECOMMENDED = "community_recommended"
    SOCIAL_DISCOVERY_ONLY = "social_discovery_only"
    UNVERIFIED = "unverified"
    OUTDATED = "outdated"


class TripType(str, Enum):
    """Styles and types of trips."""

    CITY_TRIP = "city_trip"
    ROAD_TRIP = "road_trip"
    MULTI_CITY = "multi_city"
    NATURE_LANDSCAPE = "nature_landscape"
    SLOW_TRAVEL = "slow_travel"


class TravelerProfile(str, Enum):
    """Traveler personas and party types."""

    SOLO = "solo"
    COUPLE = "couple"
    FAMILY_WITH_CHILDREN = "family_with_children"
    GROUP_FRIENDS = "group_friends"
    SENIORS = "seniors"
    DIGITAL_NOMAD = "digital_nomad"
    QUIET_SEEKER = "quiet_seeker"


class PacingPreference(str, Enum):
    """Pacing of the travel schedule."""

    PACKED = "packed"
    BALANCED = "balanced"
    RELAXED = "relaxed"


class CrowdSensitivity(str, Enum):
    """Sensitivity to crowds and overtourism."""

    STANDARD = "standard"
    AVOID_CROWDS = "avoid_crowds"
    EXTREME_QUIET = "extreme_quiet"


class TransportMode(str, Enum):
    """Modes of transport for macro and micro transit."""

    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR_RENTAL = "car_rental"
    FERRY = "ferry"
    METRO = "metro"
    WALK = "walk"
    BICYCLE = "bicycle"
    TAXI = "taxi"


class AccommodationType(str, Enum):
    """Types of accommodations."""

    HOTEL = "hotel"
    APARTMENT = "apartment"
    HOSTEL = "hostel"
    GUESTHOUSE = "guesthouse"
    RESORT = "resort"
    CAMPSITE = "campsite"


class ActivityCategory(str, Enum):
    """Categories of activities and attractions."""

    NATURE = "nature"
    LANDSCAPE = "landscape"
    CULTURE = "culture"
    GASTRONOMY = "gastronomy"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CITY_SIGHTSEEING = "city_sightseeing"
    FAMILY = "family"
    PHOTOGRAPHY = "photography"
    SHOPPING = "shopping"
    NIGHTLIFE = "nightlife"


class ChecklistCategory(str, Enum):
    """Categories for pre-travel and preparation tasks."""

    DOCUMENTS_VISA = "documents_visa"
    HEALTH_VACCINES = "health_vaccines"
    FINANCE_CURRENCY = "finance_currency"
    CONNECTIVITY_SIM = "connectivity_sim"
    LUGGAGE_GEAR = "luggage_gear"
    SAFETY_EMERGENCY = "safety_emergency"


class AgentStatus(str, Enum):
    """Execution status of a specialized sub-agent."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    BLOCKED = "blocked"
