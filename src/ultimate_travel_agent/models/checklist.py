"""Checklist and preparation models for ultimate-travel-agent."""

from typing import Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import ChecklistCategory, VerificationLevel


class ChecklistItem(BaseModel):
    """Preparation task or regulatory requirement."""

    id: str = Field(..., description="Unique task identifier")
    category: ChecklistCategory = Field(
        default=ChecklistCategory.DOCUMENTS_VISA,
        description="Category of preparation task"
    )
    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Details and actionable instructions")
    is_mandatory: bool = Field(default=True, description="Whether completion is legally or logistically mandatory")
    due_before_departure_days: int = Field(
        default=7,
        description="Recommended deadline in days prior to departure date"
    )
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.OFFICIAL_VERIFIED,
        description="Confidence level of the requirement"
    )
    official_reference_url: Optional[str] = Field(
        None,
        description="Official embassy, consulate, or government advisory URL"
    )
    completed: bool = Field(default=False, description="User completion checkmark")
