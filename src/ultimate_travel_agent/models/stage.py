"""Trip stage (étape) model for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import VerificationLevel
from ultimate_travel_agent.models.source import SourceReference


class TripStage(BaseModel):
    """Stage, leg, or stopover of a journey (étape)."""

    id: str = Field(..., description="Unique stage identifier (e.g. stage-1-paris)")
    destination_id: str = Field(..., description="Referenced destination identifier")
    order: int = Field(default=1, description="1-indexed sequence order of this stage")
    title: Optional[str] = Field(None, description="Descriptive stage title (e.g. 'Stopover in Lyon')")
    arrival_date: Optional[str] = Field(None, description="ISO arrival date YYYY-MM-DD")
    departure_date: Optional[str] = Field(None, description="ISO departure date YYYY-MM-DD")
    nights: int = Field(default=0, description="Number of nights spent in this stage")
    notes: Optional[str] = Field(None, description="Logistical notes, scenic route tips, or warnings")
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.CROSS_CHECKED,
        description="Confidence level of stage information"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Sources used to verify stage feasibility and stops"
    )
