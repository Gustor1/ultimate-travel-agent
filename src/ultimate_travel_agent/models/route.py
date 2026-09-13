"""Inter-city route option models for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import (
    RouteOptionStatus,
    RoutePreference,
    RouteTransportMode,
    VerificationLevel,
)
from ultimate_travel_agent.models.source import SourceReference


class RouteOption(BaseModel):
    """Specific transit option between two cities or waypoints."""

    id: str = Field(..., description="Unique route option identifier")
    origin: str = Field(..., description="Departure city or hub")
    destination: str = Field(..., description="Arrival city or hub")
    mode: RouteTransportMode = Field(..., description="Transport mode")
    carrier: Optional[str] = Field(None, description="Transport company, airline or rail operator")
    estimated_duration_minutes: int = Field(
        ...,
        description="Total estimated door-to-door duration in minutes"
    )
    transfers_count: int = Field(
        default=0,
        description="Number of connections or vehicle changes"
    )
    estimated_cost: float = Field(
        default=0.0,
        description="Estimated fare or cost per person"
    )
    currency: str = Field(
        default="EUR",
        description="Currency code for cost"
    )
    comfort_level: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Estimated comfort index from 1 (basic) to 5 (high comfort)"
    )
    carbon_footprint_kg: Optional[float] = Field(
        None,
        description="Estimated CO2 emission per passenger in kg"
    )
    booking_required: bool = Field(
        default=False,
        description="Whether reservation is required in advance"
    )
    official_booking_url: Optional[str] = Field(
        None,
        description="Direct link to official booking portal"
    )
    confidence_level: VerificationLevel = Field(
        default=VerificationLevel.CROSS_CHECKED,
        description="Verification/confidence level of route data"
    )
    status: RouteOptionStatus = Field(
        default=RouteOptionStatus.ESTIMATED,
        description="Status: confirmed, estimated, needs_verification"
    )
    notes: Optional[str] = Field(
        None,
        description="Strategic route notes (e.g. scenic views, luggage limits, check-in buffer)"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Sources used for route and price estimation"
    )


class InterCityRoute(BaseModel):
    """Collection of competing route options between two key journey points."""

    id: str = Field(..., description="Unique inter-city route identifier")
    origin: str = Field(..., description="Departure city or stage")
    destination: str = Field(..., description="Destination city or stage")
    options: List[RouteOption] = Field(
        default_factory=list,
        description="Available transit options"
    )
    recommended_option_id: Optional[str] = Field(
        None,
        description="ID of the currently recommended option"
    )
    recommendation_reason: Optional[str] = Field(
        None,
        description="Explanation of why this option was chosen"
    )
