"""Accommodation model for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import AccommodationType, VerificationLevel
from ultimate_travel_agent.models.source import SourceReference


class Accommodation(BaseModel):
    """Accommodation recommendation or reservation details."""

    id: str = Field(..., description="Unique accommodation identifier")
    name: str = Field(..., description="Name of the hotel, apartment, or lodging")
    destination_id: str = Field(..., description="Referenced destination identifier")
    neighborhood: str = Field(..., description="Strategic neighborhood or district name")
    accommodation_type: AccommodationType = Field(
        default=AccommodationType.HOTEL,
        description="Type of accommodation"
    )
    cost_per_night: float = Field(..., description="Estimated cost per night")
    total_nights: int = Field(default=1, description="Number of nights booked or planned")
    currency: str = Field(default="EUR", description="Currency code for cost")
    price_status: Optional[str] = Field(
        default="estimated",
        description="Price status: confirmed | estimated | needs_verification"
    )
    availability_status: Optional[str] = Field(
        default="estimated",
        description="Availability status: live | estimated | unavailable | unknown"
    )
    quietness_rating: Optional[str] = Field(
        None,
        description="Quietness assessment: high, medium, noisy"
    )
    criteria_matched: List[str] = Field(
        default_factory=list,
        description="List of traveler criteria satisfied (e.g. ['metro proximity', 'quiet street', 'kitchen'])"
    )
    official_booking_url: Optional[str] = Field(
        None,
        description="Direct URL to hotel or official lodging site (never automated booking)"
    )
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.UNVERIFIED,
        description="Level of verification of this listing"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Sources confirming price or reputation"
    )

    @property
    def total_cost(self) -> float:
        """Calculate total accommodation cost for all nights."""
        return self.cost_per_night * self.total_nights
