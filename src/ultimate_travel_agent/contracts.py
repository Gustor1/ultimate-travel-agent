"""Versioned contracts for portable travel dossiers.

The v1 contract keeps the legacy top-level fields while adding claim-level
provenance, freshness, typed money, and an explicit booking-readiness gate.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Literal, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    ValidationError,
    field_validator,
    model_validator,
)

from ultimate_travel_agent.evidence import canonicalize_source_url
from ultimate_travel_agent.profiles import TravelerProfile

VerificationStatus = Literal[
    "official_verified",
    "cross_checked",
    "community_recommended",
    "social_discovery_only",
    "estimated",
    "unverified",
    "outdated",
]
SourceType = Literal[
    "government",
    "direct_operator",
    "tourism_institution",
    "comparison_engine",
    "editorial",
    "community",
    "social",
]
AuthorityLevel = Literal["primary", "secondary", "discovery_only"]


class Money(BaseModel):
    """Exact monetary amount; floating-point values are intentionally avoided."""

    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    total: Decimal | None = Field(default=None, ge=0)

    @field_validator("amount", "quantity", "total", mode="before")
    @classmethod
    def reject_binary_floats(cls, value: Any) -> Any:
        if isinstance(value, float):
            raise ValueError("money values must be decimal strings or integers, not binary floats")
        return value

    @model_validator(mode="after")
    def calculate_or_check_total(self) -> "Money":
        expected = (self.amount * self.quantity).quantize(Decimal("0.01"))
        if self.total is None:
            self.total = expected
        elif abs(self.total - expected) > Decimal("0.01"):
            raise ValueError(
                f"money total {self.total} does not equal amount × quantity ({expected})"
            )
        return self


class SourceEvidence(BaseModel):
    """One source, classified independently by type and authority."""

    model_config = ConfigDict(extra="allow")

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    name: str = Field(min_length=1)
    url: HttpUrl
    canonical_url: HttpUrl | None = None
    source_type: SourceType
    authority: AuthorityLevel
    independence_group: str | None = Field(default=None, min_length=1)
    retrieved_at: date
    expires_at: date | None = None
    tier: int | None = Field(default=None, ge=1, le=6, description="Legacy display field")

    @model_validator(mode="before")
    @classmethod
    def derive_canonical_url(cls, value: Any) -> Any:
        if isinstance(value, dict) and value.get("url") and not value.get("canonical_url"):
            value = dict(value)
            value["canonical_url"] = canonicalize_source_url(str(value["url"]))
        return value

    @model_validator(mode="after")
    def check_freshness_window(self) -> "SourceEvidence":
        if self.expires_at is not None and self.expires_at < self.retrieved_at:
            raise ValueError("source expires_at cannot precede retrieved_at")
        return self


class Claim(BaseModel):
    """A factual claim connected to the exact evidence supporting it."""

    model_config = ConfigDict(extra="allow")

    claim_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    text: str = Field(min_length=1)
    status: VerificationStatus
    source_ids: list[str] = Field(default_factory=list)
    critical: bool = False
    observed_at: date | None = None
    expires_at: date | None = None
    topic: str | None = None
    confidence: int | None = Field(default=None, ge=0, le=100)
    conflicts_with: list[str] = Field(default_factory=list)
    fallback: str | None = None


class ReadinessGate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_ready: bool = False
    blockers: list[str] = Field(default_factory=list)


class HandoffCoverage(BaseModel):
    """Machine-verifiable execution counts for one specialist stage."""

    model_config = ConfigDict(extra="forbid")

    expected: int = Field(ge=0)
    searched: int = Field(ge=0)
    unavailable: int = Field(ge=0)
    skipped: int = Field(ge=0)
    pending: int = Field(ge=0)

    @model_validator(mode="after")
    def check_total(self) -> "HandoffCoverage":
        terminal_and_pending = self.searched + self.unavailable + self.skipped + self.pending
        if self.expected != terminal_and_pending:
            raise ValueError(
                "coverage expected must equal searched + unavailable + skipped + pending"
            )
        return self


class HandoffGates(BaseModel):
    """Separate execution, evidence, recommendation, and booking readiness."""

    model_config = ConfigDict(extra="forbid")

    coverage_complete: bool = False
    evidence_sufficient: bool = False
    recommendation_ready: bool = False
    booking_ready: bool = False


class CompactHandoffV2(BaseModel):
    """Small artifact index exchanged between isolated specialist contexts."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: Literal["compact-handoff/v2"] = Field(
        default="compact-handoff/v2", alias="schema", serialization_alias="schema"
    )
    run_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    stage: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    status: Literal["complete", "partial", "blocked"]
    artifacts: list[str] = Field(default_factory=list)
    new_ids: list[str] = Field(default_factory=list)
    changed_ids: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    coverage: HandoffCoverage
    gates: HandoffGates

    @model_validator(mode="after")
    def check_consistency(self) -> "CompactHandoffV2":
        for field_name in ("artifacts", "new_ids", "changed_ids", "decision_ids"):
            values = getattr(self, field_name)
            if len(values) != len(set(values)):
                raise ValueError(f"{field_name} values must be unique")
        overlap = set(self.new_ids) & set(self.changed_ids)
        if overlap:
            raise ValueError("new_ids and changed_ids must not overlap")

        should_be_complete = self.coverage.pending == 0
        if self.gates.coverage_complete != should_be_complete:
            raise ValueError("coverage_complete must equal whether pending is zero")
        if self.gates.evidence_sufficient and not self.gates.coverage_complete:
            raise ValueError("evidence_sufficient requires coverage_complete")
        if self.gates.recommendation_ready and not self.gates.evidence_sufficient:
            raise ValueError("recommendation_ready requires evidence_sufficient")
        if self.gates.booking_ready and not self.gates.recommendation_ready:
            raise ValueError("booking_ready requires recommendation_ready")
        if self.gates.booking_ready and self.blockers:
            raise ValueError("booking_ready handoff cannot contain blockers")
        if self.status == "complete" and not self.gates.coverage_complete:
            raise ValueError("complete status requires coverage_complete")
        if self.status == "blocked" and not self.blockers:
            raise ValueError("blocked status requires at least one blocker")
        return self


class TravelDossierV1(BaseModel):
    """Portable contract shared by skills, agents, workflows, and validators."""

    model_config = ConfigDict(extra="allow")

    schema_version: Literal["travel-dossier/v1"] = "travel-dossier/v1"
    mode: Literal["inspiration", "booking_ready"] = "inspiration"
    status: Literal["complete", "partial", "blocked"] = "partial"
    summary: str = Field(min_length=1)
    recommendations: list[Any] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    sources: list[SourceEvidence] = Field(default_factory=list)
    costs: list[Money] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    verification_required: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    readiness: ReadinessGate = Field(default_factory=ReadinessGate)
    traveler_profile: TravelerProfile | None = None
    research_state: dict[str, Any] = Field(default_factory=dict)
    itinerary: list[dict[str, Any]] = Field(default_factory=list)
    locations: list[dict[str, Any]] = Field(default_factory=list)
    scenarios: list[dict[str, Any]] = Field(default_factory=list)
    decision_log: list[dict[str, Any]] = Field(default_factory=list)
    revalidation_plan: list[dict[str, Any]] = Field(default_factory=list)
    flight_search: dict[str, Any] = Field(default_factory=dict)
    accommodation_search: dict[str, Any] = Field(default_factory=dict)
    mobility_assessment: dict[str, Any] = Field(default_factory=dict)
    true_cost_comparison: dict[str, Any] = Field(default_factory=dict)
    price_watch: dict[str, Any] = Field(default_factory=dict)
    disruption_recovery: dict[str, Any] = Field(default_factory=dict)
    connector_results: list[dict[str, Any]] = Field(default_factory=list)
    adaptive_plans: list[dict[str, Any]] = Field(default_factory=list)
    group_decisions: list[dict[str, Any]] = Field(default_factory=list)
    neighborhood_assessments: list[dict[str, Any]] = Field(default_factory=list)
    booking_handoffs: list[dict[str, Any]] = Field(default_factory=list)
    trip_mode: dict[str, Any] = Field(default_factory=dict)
    optimized_routes: list[dict[str, Any]] = Field(default_factory=list)
    notification_receipts: list[dict[str, Any]] = Field(default_factory=list)


def validate_compact_handoff(
    data: dict[str, Any],
) -> tuple[bool, list[str], CompactHandoffV2 | None]:
    """Validate the portable compact handoff and return actionable issues."""

    try:
        handoff = CompactHandoffV2.model_validate(data)
    except ValidationError as exc:
        return False, [error["msg"] for error in exc.errors()], None
    return True, [], handoff


def _legacy_source_type(tier: int) -> SourceType:
    value = {
        1: "government",
        2: "direct_operator",
        3: "tourism_institution",
        4: "editorial",
        5: "community",
        6: "social",
    }.get(tier, "editorial")
    return cast(SourceType, value)


def upgrade_legacy_dossier(data: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    """Expand the legacy envelope without discarding any original field."""

    upgraded = dict(data)
    upgraded.setdefault("schema_version", "travel-dossier/v1")
    upgraded.setdefault("mode", "inspiration")
    upgraded.setdefault("status", "partial")
    upgraded.setdefault("recommendations", [])
    upgraded.setdefault("claims", [])
    upgraded.setdefault("costs", [])
    upgraded.setdefault("assumptions", [])
    upgraded.setdefault("missing_information", [])
    upgraded.setdefault("verification_required", [])
    upgraded.setdefault("risks", [])

    retrieval_date = (today or date.today()).isoformat()
    if "sources" not in upgraded:
        sources: list[dict[str, Any]] = []
        for index, raw in enumerate(upgraded.get("source_log", []), start=1):
            if not isinstance(raw, dict):
                continue
            tier = int(raw.get("tier", 4)) if str(raw.get("tier", "4")).isdigit() else 4
            source_type = _legacy_source_type(tier)
            authority: AuthorityLevel = (
                "primary" if tier in (1, 2) else "secondary" if tier in (3, 4) else "discovery_only"
            )
            sources.append(
                {
                    **raw,
                    "source_id": raw.get("source_id", f"legacy-source-{index}"),
                    "source_type": raw.get("source_type", source_type),
                    "authority": raw.get("authority", authority),
                    "retrieved_at": raw.get("retrieved_at")
                    or raw.get("verification_date")
                    or retrieval_date,
                }
            )
        upgraded["sources"] = sources

    upgraded.setdefault(
        "readiness",
        {
            "booking_ready": False,
            "blockers": ["Legacy dossier has no claim-level booking-readiness proof"],
        },
    )
    return upgraded


def validate_travel_dossier(
    data: dict[str, Any], today: date | None = None
) -> tuple[bool, list[str], TravelDossierV1 | None]:
    """Validate structure, evidence references, freshness, and booking readiness."""

    issues: list[str] = []
    try:
        dossier = TravelDossierV1.model_validate(upgrade_legacy_dossier(data, today=today))
    except ValidationError as exc:
        return False, [error["msg"] for error in exc.errors()], None

    source_map = {source.source_id: source for source in dossier.sources}
    if len(source_map) != len(dossier.sources):
        issues.append("Duplicate source_id values")

    claim_ids = {claim.claim_id for claim in dossier.claims}
    if len(claim_ids) != len(dossier.claims):
        issues.append("Duplicate claim_id values")

    current_date = today or date.today()
    for claim in dossier.claims:
        missing_sources = [
            source_id for source_id in claim.source_ids if source_id not in source_map
        ]
        if missing_sources:
            issues.append(f"Claim {claim.claim_id} references unknown sources: {missing_sources}")
        if claim.expires_at is not None and claim.expires_at < current_date:
            issues.append(f"Claim {claim.claim_id} is expired")
        unknown_conflicts = [
            claim_id for claim_id in claim.conflicts_with if claim_id not in claim_ids
        ]
        if unknown_conflicts:
            issues.append(
                f"Claim {claim.claim_id} conflicts with unknown claims: {unknown_conflicts}"
            )

    if dossier.mode == "booking_ready" or dossier.readiness.booking_ready:
        if dossier.mode != "booking_ready" or not dossier.readiness.booking_ready:
            issues.append("booking_ready mode and readiness.booking_ready must agree")
        critical_claims = [claim for claim in dossier.claims if claim.critical]
        if not critical_claims:
            issues.append("Booking-ready dossier has no critical claims")
        for claim in critical_claims:
            if claim.status not in ("official_verified", "cross_checked"):
                issues.append(f"Critical claim {claim.claim_id} is not verified")
            if not claim.source_ids:
                issues.append(f"Critical claim {claim.claim_id} has no source")
            if claim.conflicts_with:
                issues.append(f"Critical claim {claim.claim_id} has unresolved conflicts")
            for source_id in claim.source_ids:
                source = source_map.get(source_id)
                if (
                    source is not None
                    and source.expires_at is not None
                    and source.expires_at < current_date
                ):
                    issues.append(
                        f"Critical claim {claim.claim_id} uses expired source {source_id}"
                    )
            linked_sources = [source_map[source_id] for source_id in claim.source_ids if source_id in source_map]
            if linked_sources and not any(source.authority == "primary" for source in linked_sources):
                issues.append(f"Critical claim {claim.claim_id} has no primary evidence")
            if claim.status == "cross_checked":
                independence_groups = {
                    source.independence_group
                    for source in linked_sources
                    if source.independence_group is not None
                }
                if len(independence_groups) < 2:
                    issues.append(
                        f"Cross-checked claim {claim.claim_id} lacks two independent evidence origins"
                    )
        if dossier.readiness.blockers:
            issues.append("Booking-ready dossier still contains readiness blockers")
        if dossier.missing_information:
            issues.append("Booking-ready dossier still contains missing information")
        if dossier.verification_required:
            issues.append("Booking-ready dossier still requires verification")

    return len(issues) == 0, issues, dossier
