"""Progressive travel research gates that prevent premature deep searches."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ResearchStage = Literal["brief", "destination", "dates", "area", "options", "booking"]
STAGES: tuple[ResearchStage, ...] = (
    "brief",
    "destination",
    "dates",
    "area",
    "options",
    "booking",
)


class ResearchState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_stage: ResearchStage = "brief"
    completed_stages: list[ResearchStage] = Field(default_factory=list)
    destination: str | None = None
    travel_dates: tuple[date, date] | None = None
    area: str | None = None
    option_ids: list[str] = Field(default_factory=list)
    pending_questions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def dates_are_ordered(self) -> "ResearchState":
        if self.travel_dates is not None and self.travel_dates[1] < self.travel_dates[0]:
            raise ValueError("travel end date cannot precede start date")
        return self


def stage_requirements(state: ResearchState, stage: ResearchStage) -> list[str]:
    """Return missing inputs for entering a research stage."""

    if stage == "brief":
        return []
    if stage == "destination":
        return [] if "brief" in state.completed_stages else ["complete traveler brief"]
    if stage == "dates":
        return [] if state.destination else ["select destination"]
    if stage == "area":
        return [] if state.travel_dates else ["select travel dates"]
    if stage == "options":
        return [] if state.area else ["select target area"]
    return [] if state.option_ids else ["shortlist options"]


def advance_research(state: ResearchState, target: ResearchStage) -> ResearchState:
    """Advance one or more stages only when each prerequisite is present."""

    current_index = STAGES.index(state.current_stage)
    target_index = STAGES.index(target)
    if target_index < current_index:
        raise ValueError("research cannot move backward; start a new state instead")
    updated = state.model_copy(deep=True)
    for index in range(current_index, target_index + 1):
        stage = STAGES[index]
        missing = stage_requirements(updated, stage)
        if missing:
            updated.pending_questions = missing
            return updated
        if stage not in updated.completed_stages and stage != target:
            updated.completed_stages.append(stage)
    updated.current_stage = target
    updated.pending_questions = stage_requirements(updated, target)
    return updated


def next_research_actions(state: ResearchState) -> list[str]:
    """Provide the smallest useful next research step."""

    missing = stage_requirements(state, state.current_stage)
    if missing:
        return missing
    index = STAGES.index(state.current_stage)
    if index == len(STAGES) - 1:
        return ["verify booking-critical facts and revalidate prices"]
    return [f"complete {state.current_stage} research", f"prepare {STAGES[index + 1]} stage"]
