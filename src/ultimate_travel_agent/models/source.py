"""Source reference models for ultimate-travel-agent."""

from typing import Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import VerificationLevel


class SourceReference(BaseModel):
    """Reference to an authoritative, guidebook, or community source."""

    title: str = Field(..., description="Title or name of the source")
    url: Optional[str] = Field(None, description="Direct URL to the source")
    source_type: str = Field(
        default="official",
        description="Type of source: official, guidebook, community, social_media, local_knowledge"
    )
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.UNVERIFIED,
        description="Verification level of this source"
    )
    notes: Optional[str] = Field(None, description="Contextual notes on reliability")
    retrieved_at: Optional[str] = Field(None, description="ISO date when information was verified")
