"""Itinerary scheduling models for ultimate-travel-agent."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ItineraryItem(BaseModel):
    """Specific event or visit inside a daily itinerary."""

    time: str = Field(..., description="Time of day or slot (e.g. '09:00', 'morning', '14:30')")
    item_type: str = Field(..., description="Type: activity, transport, meal, rest, checkin, checkout")
    title: str = Field(..., description="Short title of the step")
    reference_id: Optional[str] = Field(None, description="Linked Activity ID or Transport ID")
    duration_minutes: int = Field(default=60, description="Duration in minutes")
    notes: Optional[str] = Field(None, description="Actionable tips, tickets, or transport notes")
    indoor_backup: Optional[str] = Field(None, description="Backup plan if weather turns bad")


class DaySchedule(BaseModel):
    """Chronological plan for a single day of travel."""

    day_number: int = Field(..., description="1-indexed day sequence number")
    date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")
    destination_id: str = Field(..., description="Active destination identifier")
    theme: Optional[str] = Field(None, description="Day theme (e.g. 'Gaudí Architecture & Gothic Quarter')")
    items: List[ItineraryItem] = Field(default_factory=list, description="Ordered schedule events")
    daily_cost_estimate: float = Field(default=0.0, description="Estimated total cost for the day")
    currency: str = Field(default="EUR", description="Currency code")
    weather_contingency_notes: Optional[str] = Field(None, description="Contingency advice in case of rain or storms")
