"""Traveler profile model for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import CrowdSensitivity, PacingPreference, TravelerProfile


class Traveler(BaseModel):
    """Profile of a traveler participating in the trip."""

    id: str = Field(..., description="Unique traveler ID (e.g. traveler-1)")
    name: str = Field(..., description="Name or nickname of the traveler")
    profile: TravelerProfile = Field(
        default=TravelerProfile.SOLO,
        description="Traveler archetype"
    )
    pacing_preference: PacingPreference = Field(
        default=PacingPreference.BALANCED,
        description="Preferred daily tempo"
    )
    crowd_sensitivity: CrowdSensitivity = Field(
        default=CrowdSensitivity.STANDARD,
        description="Sensitivity to crowds and overtourism"
    )
    dietary_restrictions: List[str] = Field(
        default_factory=list,
        description="Allergies and dietary restrictions (e.g. vegetarian, gluten-free, halal)"
    )
    mobility_needs: Optional[str] = Field(
        None,
        description="Special mobility requirements (e.g. step-free, wheelchair, stroller)"
    )
    budget_preference: Optional[str] = Field(
        "mid-range",
        description="Budget tier: budget, mid-range, premium, luxury"
    )
