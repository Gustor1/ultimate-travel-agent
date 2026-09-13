"""Activity and point-of-interest models for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import ActivityCategory, VerificationLevel
from ultimate_travel_agent.models.source import SourceReference


class Activity(BaseModel):
    """Activity, museum, landmark, or dining experience."""

    id: str = Field(..., description="Unique activity identifier")
    title: str = Field(..., description="Name of the activity or venue")
    destination_id: str = Field(..., description="Destination identifier where activity is located")
    category: ActivityCategory = Field(
        default=ActivityCategory.CULTURE,
        description="Category of activity"
    )
    description: str = Field(..., description="Description of the visit or experience")
    duration_minutes: int = Field(default=90, description="Recommended visit duration in minutes")
    estimated_cost: float = Field(default=0.0, description="Cost per person in currency")
    currency: str = Field(default="EUR", description="Currency ISO code")
    crowd_level: Optional[str] = Field(
        "medium",
        description="Observed crowd density: low, medium, high, extreme"
    )
    quiet_slot_advice: Optional[str] = Field(
        None,
        description="Advice on optimal slot to avoid peak crowds (e.g. 'Enter at 08:30 or after 17:00')"
    )
    advance_booking_required: bool = Field(
        default=False,
        description="Whether advance timed tickets are strictly mandatory"
    )
    official_booking_url: Optional[str] = Field(
        None,
        description="Direct link to official ticketing box office"
    )
    indoor_contingency: bool = Field(
        default=False,
        description="Whether this activity is suitable as a rainy-day backup"
    )
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.UNVERIFIED,
        description="Verification level of activity information"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Sources used to verify hours, ticketing, and crowding"
    )
