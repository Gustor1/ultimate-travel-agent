"""Accommodation integrations package."""

from ultimate_travel_agent.integrations.accommodation.adapter import HotelAdapter
from ultimate_travel_agent.integrations.accommodation.amadeus_hotel import AmadeusHotelProvider
from ultimate_travel_agent.integrations.accommodation.booking import BookingProvider
from ultimate_travel_agent.integrations.accommodation.mock import MockAccommodationProvider

__all__ = [
    "AmadeusHotelProvider",
    "BookingProvider",
    "HotelAdapter",
    "MockAccommodationProvider",
]
