"""Activity and point-of-interest models for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import (
    ActivityCategory,
    DifficultyLevel,
    EnvironmentType,
    VerificationLevel,
)
from ultimate_travel_agent.models.source import SourceReference


class Activity(BaseModel):
    """Activity, museum, landmark, or dining experience with rich context."""

    id: str = Field(..., description="Unique activity identifier")
    title: str = Field(..., description="Name of the activity or venue")
    destination_id: str = Field(..., description="Destination identifier where activity is located")
    category: ActivityCategory = Field(
        default=ActivityCategory.CULTURE,
        description="Category of activity"
    )
    description: str = Field(..., description="Description of the visit or experience")

    # Geographic granularity
    country: Optional[str] = Field(None, description="Country where the activity is located")
    region: Optional[str] = Field(None, description="Region or province")
    city: Optional[str] = Field(None, description="City name")
    neighborhood: Optional[str] = Field(None, description="Neighborhood or district")

    # Local context & anecdotes
    anecdote: Optional[str] = Field(
        None,
        description="Anecdote, local story, or cultural context about the venue"
    )

    # Environment, difficulty & accessibility
    environment: EnvironmentType = Field(
        default=EnvironmentType.INDOOR,
        description="Indoor, outdoor, or hybrid environment"
    )
    difficulty_level: DifficultyLevel = Field(
        default=DifficultyLevel.EASY,
        description="Physical difficulty: easy, moderate, demanding"
    )
    accessibility: Optional[str] = Field(
        None,
        description="Accessibility features (wheelchair, reduced mobility, stroller, sensory)"
    )

    # Scheduling & best time
    duration_minutes: int = Field(default=90, description="Recommended visit duration in minutes")
    best_time_slot: Optional[str] = Field(
        None,
        description="Best time of day or slot to visit (e.g. '08:30 - 10:00' or 'sunset')"
    )
    opening_hours: Optional[str] = Field(
        None,
        description="Standard operating hours and opening days"
    )

    # Costs
    estimated_cost: float = Field(default=0.0, description="Cost per person in currency")
    currency: str = Field(default="EUR", description="Currency ISO code")

    # Transit access
    access_method: Optional[str] = Field(
        None,
        description="How to reach the venue (e.g. 'Metro L3 to Fontana, then 7 min walk')"
    )
    transit_duration_minutes: Optional[int] = Field(
        None,
        description="Estimated transit time from lodging/hub in minutes"
    )
    transit_cost: Optional[float] = Field(
        None,
        description="Estimated transit fare per person"
    )

    # Booking & Crowds
    advance_booking_required: bool = Field(
        default=False,
        description="Whether advance timed tickets are strictly mandatory"
    )
    official_booking_url: Optional[str] = Field(
        None,
        description="Direct link to official ticketing box office"
    )
    crowd_level: Optional[str] = Field(
        "medium",
        description="Observed crowd density: low, medium, high, extreme"
    )
    quiet_slot_advice: Optional[str] = Field(
        None,
        description="Advice on optimal slot to avoid peak crowds (e.g. 'Enter at 08:30 or after 17:00')"
    )
    crowd_avoidance_strategy: Optional[str] = Field(
        None,
        description="Specific strategy to bypass peak crowds or queues"
    )

    # Weather & Closure contingencies
    indoor_contingency: bool = Field(
        default=False,
        description="Whether this activity itself serves as a rainy-day indoor backup"
    )
    weather_alternative: Optional[str] = Field(
        None,
        description="Recommended indoor alternative activity if weather is poor"
    )
    closure_alternative: Optional[str] = Field(
        None,
        description="Recommended alternative activity in case of unexpected closure or strike"
    )

    # Verification & Sources
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.UNVERIFIED,
        description="Verification level of activity information"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Sources used to verify hours, ticketing, and crowding"
    )

    @property
    def effective_crowd_strategy(self) -> Optional[str]:
        """Return the best crowd avoidance guidance available."""
        return self.crowd_avoidance_strategy or self.quiet_slot_advice
