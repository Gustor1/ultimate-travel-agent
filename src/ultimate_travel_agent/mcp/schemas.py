"""Pydantic-owned request and response contracts for the MCP surface."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ultimate_travel_agent.adaptive import (
    ActivityCandidate,
    AdaptiveDayPlan,
    AdaptiveDayRequest,
)
from ultimate_travel_agent.booking import BookingConfirmation, BookingHandoff, BookingIntent
from ultimate_travel_agent.connectors import (
    ConnectorConfig,
    ConnectorNormalizationSpec,
    ConnectorRequest,
    ConnectorResult,
    NormalizedConnectorResult,
    ReadOnlyConnectorRequest,
)
from ultimate_travel_agent.disruptions import (
    Disruption,
    ItineraryItem,
    RecoveryOption,
    RecoveryPlan,
)
from ultimate_travel_agent.flight_flex import (
    CoverageReport,
    FlightSearchPlan,
    FlightSearchRequest,
)
from ultimate_travel_agent.group_planning import GroupDecision, GroupOption, ParticipantBallot
from ultimate_travel_agent.hotel_search import (
    HotelComparison,
    HotelCoverageReport,
    HotelMobilityAssessment,
    HotelProperty,
    HotelResearchPlan,
    HotelSearchRequest,
    MobilityAnchor,
    TransitJourney,
)
from ultimate_travel_agent.monitoring import (
    PriceAlertPolicy,
    PriceAlertState,
    PriceMonitoringDecision,
    PriceObservation,
    PriceWatch,
    PriceWatchAssessment,
    RevalidationTask,
)
from ultimate_travel_agent.neighborhood import (
    NeighborhoodAssessment,
    NeighborhoodProfile,
    NeighborhoodRequirements,
)
from ultimate_travel_agent.notifications import (
    NotificationMessage,
    NotificationReceipt,
    WebhookNotificationConfig,
)
from ultimate_travel_agent.profiles import TravelerProfile
from ultimate_travel_agent.route_optimizer import (
    OptimizedRoute,
    RouteVisit,
    SourcedTravelTime,
)
from ultimate_travel_agent.trip_mode import TripCompanionState, TripModeRequest
from ultimate_travel_agent.true_cost import (
    CostCategory,
    DoorToDoorOption,
    TrueCostComparison,
)


class MCPModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EmptyInput(MCPModel):
    pass


class PathInput(MCPModel):
    path: str = Field(min_length=1, description="Path below the configured MCP root.")


class OptionalPathInput(MCPModel):
    path: str | None = Field(
        default=None, description="Optional path below the configured MCP root."
    )


class InstallSkillsInput(MCPModel):
    target: str = Field(min_length=1, description="Target directory below the MCP root.")
    include_agents: bool = False
    include_workflows: bool = False
    force: bool = False
    dry_run: bool = False


class UninstallSkillsInput(MCPModel):
    target: str = Field(min_length=1, description="Installed project below the MCP root.")
    force: bool = False
    clean_modified: bool = False
    dry_run: bool = False


class FileOperationOutput(MCPModel):
    installed: list[str] = Field(default_factory=list)
    overwritten: list[str] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    restored: list[str] = Field(default_factory=list)
    skipped_modified: list[str] = Field(default_factory=list)
    not_found: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    manifest_path: str | None = None
    manifest_cleaned: bool | None = None
    skills_count: int | None = Field(default=None, ge=0)
    agents_count: int | None = Field(default=None, ge=0)
    workflows_count: int | None = Field(default=None, ge=0)
    assets_count: int | None = Field(default=None, ge=0)


class SkillInfo(MCPModel):
    name: str
    description: str = ""
    path: str | None = None


class SkillsListOutput(MCPModel):
    skills: list[SkillInfo]


class SkillsValidationOutput(MCPModel):
    passed: bool
    reports: dict[str, list[str]]


class ValidateDossierInput(MCPModel):
    dossier: dict[str, Any] = Field(description="TravelDossier v1 object to validate.")


class ValidateHandoffInput(MCPModel):
    handoff: dict[str, Any] = Field(description="compact-handoff/v2 object to validate.")


class ContractValidationOutput(MCPModel):
    passed: bool
    issues: list[str]
    normalized: dict[str, Any] | None = None


class CorpusMetrics(MCPModel):
    files: int = Field(ge=0)
    characters: int = Field(ge=0)
    estimated_tokens: int = Field(ge=0)


class PromptAuditOutput(MCPModel):
    skills: CorpusMetrics
    agents: CorpusMetrics
    workflows: CorpusMetrics
    shared: CorpusMetrics


class NormalizeSourceUrlInput(MCPModel):
    url: HttpUrl


class NormalizeSourceUrlOutput(MCPModel):
    url: HttpUrl


class ProfileSaveInput(MCPModel):
    profile: TravelerProfile
    output_path: str = Field(min_length=1, description="JSON path below the MCP root.")


class ProfileOutput(MCPModel):
    profile: TravelerProfile
    path: str


class ExportDossierInput(MCPModel):
    dossier: dict[str, Any]
    output_path: str = Field(min_length=1, description="Artifact path below the MCP root.")
    format: Literal["ics", "geojson", "pdf", "checklist", "offline", "html"]


class ExportDossierOutput(MCPModel):
    path: str
    format: Literal["ics", "geojson", "pdf", "checklist", "offline", "html"]
    bytes_written: int = Field(ge=0)


class RevalidationPlanInput(MCPModel):
    dossier: dict[str, Any]
    departure: date


class RevalidationPlanOutput(MCPModel):
    tasks: list[RevalidationTask]


class PriceWatchInput(MCPModel):
    watch: PriceWatch
    observations: list[PriceObservation]
    policy: PriceAlertPolicy | None = None
    state: PriceAlertState | None = None


class PriceWatchOutput(MCPModel):
    mode: Literal["assessment", "scheduled"]
    assessment: PriceWatchAssessment | None = None
    decision: PriceMonitoringDecision | None = None


class FlightSearchPlanInput(MCPModel):
    request: FlightSearchRequest
    output_path: str | None = Field(
        default=None, description="Optional JSON path below the MCP root."
    )


class FlightCoverageInput(MCPModel):
    plan: FlightSearchPlan
    booking_ready: bool = False


class HotelSearchPlanInput(MCPModel):
    request: HotelSearchRequest
    output_path: str | None = Field(
        default=None, description="Optional JSON path below the MCP root."
    )


class HotelCoverageInput(MCPModel):
    plan: HotelResearchPlan
    booking_ready: bool = False


class HotelCompareInput(MCPModel):
    request: HotelSearchRequest
    property: HotelProperty
    room_key: str = Field(min_length=1)


class HotelMobilityInput(MCPModel):
    anchors: list[MobilityAnchor]
    journeys: list[TransitJourney]
    maximum_walking_minutes: int = Field(default=15, ge=0, le=240)
    step_free_required: bool = False


class CompareTotalCostInput(MCPModel):
    options: list[DoorToDoorOption] = Field(min_length=1)
    required_categories: list[CostCategory] = Field(min_length=1)
    value_of_time_per_hour: Decimal = Field(default=Decimal("0"), ge=0)
    separate_ticket_reserve_percent: Decimal = Field(default=Decimal("10"), ge=0)


class DisruptionPlanInput(MCPModel):
    itinerary: list[ItineraryItem]
    disruption: Disruption
    options: list[RecoveryOption]
    cascade: bool = False


class ConnectorInput(MCPModel):
    config: ConnectorConfig
    request: ConnectorRequest
    normalization: ConnectorNormalizationSpec | None = None


class ConnectorReadInput(MCPModel):
    config: ConnectorConfig
    request: ReadOnlyConnectorRequest
    normalization: ConnectorNormalizationSpec | None = None


class ConnectorOutput(MCPModel):
    normalized: bool
    result: ConnectorResult | NormalizedConnectorResult


class AdaptiveDayInput(MCPModel):
    request: AdaptiveDayRequest
    activities: list[ActivityCandidate] = Field(min_length=1)


class RouteOptimizeInput(MCPModel):
    origin_id: str = Field(min_length=1)
    day_start: datetime
    day_end: datetime
    visits: list[RouteVisit]
    travel_times: list[SourcedTravelTime]
    destination_id: str | None = None


class GroupDecideInput(MCPModel):
    options: list[GroupOption] = Field(min_length=1)
    ballots: list[ParticipantBallot] = Field(min_length=1)


class NeighborhoodScoreInput(MCPModel):
    profile: NeighborhoodProfile
    requirements: NeighborhoodRequirements = Field(default_factory=NeighborhoodRequirements)
    as_of: date | None = None


class BookingHandoffInput(MCPModel):
    intent: BookingIntent
    now: datetime
    confirmation: BookingConfirmation | None = None


class NotifyWebhookInput(MCPModel):
    config: WebhookNotificationConfig
    message: NotificationMessage


INPUT_MODELS: dict[str, type[BaseModel]] = {
    "install-skills": InstallSkillsInput,
    "uninstall-skills": UninstallSkillsInput,
    "list-skills": EmptyInput,
    "validate-skills": OptionalPathInput,
    "validate-dossier": ValidateDossierInput,
    "validate-handoff": ValidateHandoffInput,
    "prompt-audit": OptionalPathInput,
    "normalize-source-url": NormalizeSourceUrlInput,
    "profile-save": ProfileSaveInput,
    "profile-show": PathInput,
    "export-dossier": ExportDossierInput,
    "revalidation-plan": RevalidationPlanInput,
    "price-watch": PriceWatchInput,
    "flight-search-plan": FlightSearchPlanInput,
    "flight-search-coverage": FlightCoverageInput,
    "hotel-search-plan": HotelSearchPlanInput,
    "hotel-search-coverage": HotelCoverageInput,
    "hotel-compare": HotelCompareInput,
    "hotel-mobility": HotelMobilityInput,
    "compare-total-cost": CompareTotalCostInput,
    "disruption-plan": DisruptionPlanInput,
    "connector-fetch": ConnectorInput,
    "connector-read": ConnectorReadInput,
    "adaptive-day": AdaptiveDayInput,
    "route-optimize": RouteOptimizeInput,
    "group-decide": GroupDecideInput,
    "neighborhood-score": NeighborhoodScoreInput,
    "booking-handoff": BookingHandoffInput,
    "trip-mode": TripModeRequest,
    "notify-webhook": NotifyWebhookInput,
}

OUTPUT_MODELS: dict[str, type[BaseModel]] = {
    "install-skills": FileOperationOutput,
    "uninstall-skills": FileOperationOutput,
    "list-skills": SkillsListOutput,
    "validate-skills": SkillsValidationOutput,
    "validate-dossier": ContractValidationOutput,
    "validate-handoff": ContractValidationOutput,
    "prompt-audit": PromptAuditOutput,
    "normalize-source-url": NormalizeSourceUrlOutput,
    "profile-save": ProfileOutput,
    "profile-show": ProfileOutput,
    "export-dossier": ExportDossierOutput,
    "revalidation-plan": RevalidationPlanOutput,
    "price-watch": PriceWatchOutput,
    "flight-search-plan": FlightSearchPlan,
    "flight-search-coverage": CoverageReport,
    "hotel-search-plan": HotelResearchPlan,
    "hotel-search-coverage": HotelCoverageReport,
    "hotel-compare": HotelComparison,
    "hotel-mobility": HotelMobilityAssessment,
    "compare-total-cost": TrueCostComparison,
    "disruption-plan": RecoveryPlan,
    "connector-fetch": ConnectorOutput,
    "connector-read": ConnectorOutput,
    "adaptive-day": AdaptiveDayPlan,
    "route-optimize": OptimizedRoute,
    "group-decide": GroupDecision,
    "neighborhood-score": NeighborhoodAssessment,
    "booking-handoff": BookingHandoff,
    "trip-mode": TripCompanionState,
    "notify-webhook": NotificationReceipt,
}


def get_input_model(name: str) -> type[BaseModel]:
    return INPUT_MODELS[name]


def get_output_model(name: str) -> type[BaseModel]:
    return OUTPUT_MODELS[name]


__all__ = [
    "ConnectorReadInput",
    "INPUT_MODELS",
    "OUTPUT_MODELS",
    "get_input_model",
    "get_output_model",
]
