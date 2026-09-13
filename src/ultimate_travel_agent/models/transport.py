"""Transport segment model for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import TransportMode, VerificationLevel
from ultimate_travel_agent.models.source import SourceReference


class TransportSegment(BaseModel):
    """Macro or micro travel transit segment."""

    id: str = Field(..., description="Unique segment identifier")
    origin: str = Field(..., description="Origin location, station, or airport")
    destination: str = Field(..., description="Destination location, station, or airport")
    mode: TransportMode = Field(..., description="Mode of transport")
    carrier: Optional[str] = Field(None, description="Carrier, airline, or transit agency name")
    departure_time: Optional[str] = Field(None, description="Estimated or scheduled departure time (HH:MM or ISO)")
    arrival_time: Optional[str] = Field(None, description="Estimated or scheduled arrival time (HH:MM or ISO)")
    duration_minutes: int = Field(..., description="Duration in minutes including connection buffers")
    estimated_cost: float = Field(default=0.0, description="Estimated ticket or fare cost")
    is_per_person: Optional[bool] = Field(
        None,
        description="Whether cost is per passenger (True) or for the vehicle/group (False). Defaults to False for car_rental/taxi, True otherwise."
    )
    currency: str = Field(default="EUR", description="Currency code for cost")
    official_booking_url: Optional[str] = Field(None, description="Direct URL to official ticketing operator")
    door_to_door_notes: Optional[str] = Field(
        None,
        description="Door-to-door transit instructions, transfer stations, and baggage advice"
    )
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.UNVERIFIED,
        description="Verification level of price and schedule"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Sources used for route and price estimation"
    )

    @property
    def effective_is_per_person(self) -> bool:
        """Determine if pricing scales per traveler or is fixed per group/vehicle."""
        if self.is_per_person is not None:
            return self.is_per_person
        # Vehicle / charter modes are group-based by default
        return self.mode not in (TransportMode.CAR_RENTAL, TransportMode.TAXI)
