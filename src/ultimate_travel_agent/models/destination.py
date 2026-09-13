"""Destination models for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Destination(BaseModel):
    """Geographic destination for a trip or trip leg."""

    id: str = Field(..., description="Unique destination identifier (e.g. bcn, tyo)")
    name: str = Field(..., description="City or area name (e.g. Barcelona)")
    country: str = Field(..., description="Country name (e.g. Spain)")
    region: Optional[str] = Field(None, description="Region or province (e.g. Catalonia)")
    currency: str = Field(default="EUR", description="Local currency ISO code (e.g. EUR, JPY)")
    timezone: str = Field(default="UTC", description="Timezone name (e.g. Europe/Madrid)")
    ideal_seasons: List[str] = Field(
        default_factory=list,
        description="Best months or seasons to visit (e.g. ['April-May', 'September-October'])"
    )
    quiet_periods: List[str] = Field(
        default_factory=list,
        description="Low season / quiet periods to avoid peak crowds"
    )
    description: Optional[str] = Field(None, description="Overview of the destination")
    anecdote: Optional[str] = Field(None, description="Interesting local fact or historical anecdote")
