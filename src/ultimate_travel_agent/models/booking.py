"""Booking requirement and reservation model for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import VerificationLevel
from ultimate_travel_agent.models.source import SourceReference


class BookingRequirement(BaseModel):
    """Booking requirement or confirmed reservation (réservation).

    Strict policy: Never triggers automated payment or purchase.
    All actions must be executed manually by the traveler on official portals.
    """

    id: str = Field(..., description="Unique booking requirement identifier")
    category: str = Field(
        ...,
        description="Booking category: transport, accommodation, activity, permit, visa, other"
    )
    title: str = Field(..., description="Title of the booking requirement")
    status: str = Field(
        default="needed",
        description="Booking status: needed, booked, not_needed, optional"
    )
    mandatory: bool = Field(default=True, description="Whether this reservation is mandatory")
    reference_id: Optional[str] = Field(
        None,
        description="Linked entity ID (e.g. transport_id, accommodation_id, activity_id)"
    )
    deadline_days_before: Optional[int] = Field(
        None,
        description="Recommended advance booking deadline in days before departure"
    )
    confirmation_code: Optional[str] = Field(
        None,
        description="Official reservation reference or PNR (if already booked)"
    )
    estimated_cost: float = Field(default=0.0, description="Estimated total cost")
    currency: str = Field(default="EUR", description="Currency ISO code")
    official_booking_url: Optional[str] = Field(
        None,
        description="Direct link to official ticketing or lodging reservation portal"
    )
    action_required: str = Field(
        default="",
        description="Human instructions for completing the reservation"
    )
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.OFFICIAL_VERIFIED,
        description="Confidence level of booking requirement and link"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Authoritative sources for ticketing and terms"
    )
