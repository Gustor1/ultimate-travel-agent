"""Transit-aware hotel research plans and apples-to-apples rate comparison."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

HotelProvider = Literal["official", "google_hotels", "booking", "agoda", "trip_com"]
TaskStatus = Literal["pending", "searched", "unavailable", "skipped"]
TransitMode = Literal[
    "metro", "tram", "commuter_rail", "bus", "ferry", "shuttle", "other"
]

PROVIDERS: tuple[HotelProvider, ...] = (
    "google_hotels",
    "booking",
    "agoda",
    "trip_com",
    "official",
)
_TRANSIT_PRIORITY: dict[TransitMode, int] = {
    "metro": 0,
    "tram": 1,
    "commuter_rail": 2,
    "bus": 3,
    "ferry": 4,
    "shuttle": 5,
    "other": 6,
}


class HotelSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    search_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    city: str = Field(min_length=1)
    country: str = Field(min_length=2)
    check_in: date
    check_out: date
    guests: int = Field(default=2, ge=1, le=30)
    rooms: int = Field(default=1, ge=1, le=15)
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    neighborhoods: list[str] = Field(default_factory=list, max_length=10)
    maximum_transit_walk_minutes: int = Field(default=12, ge=1, le=30)
    step_free_required: bool = False
    breakfast_required: bool = False
    free_cancellation_required: bool = False
    maximum_total: Decimal | None = Field(default=None, ge=0)

    @field_validator("maximum_total", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("hotel budgets must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "HotelSearchRequest":
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days


class HotelResearchTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    phase: Literal["area_transit", "price_discovery", "direct_verification"]
    provider: HotelProvider | Literal["official_transit"]
    priority: int = Field(ge=1)
    status: TaskStatus = "pending"
    source_ids: list[str] = Field(default_factory=list)
    note: str | None = None


class HotelResearchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: HotelSearchRequest
    tasks: list[HotelResearchTask]


def generate_hotel_research_plan(request: HotelSearchRequest) -> HotelResearchPlan:
    """Create transit-first research followed by comparison and direct verification."""

    tasks = [
        HotelResearchTask(
            task_id="area-transit",
            phase="area_transit",
            provider="official_transit",
            priority=1,
        )
    ]
    tasks.extend(
        HotelResearchTask(
            task_id=f"compare-{provider}",
            phase="price_discovery",
            provider=provider,
            priority=2,
        )
        for provider in PROVIDERS
        if provider != "official"
    )
    tasks.append(
        HotelResearchTask(
            task_id="verify-official",
            phase="direct_verification",
            provider="official",
            priority=3,
        )
    )
    return HotelResearchPlan(request=request, tasks=tasks)


class HotelCoverageReport(BaseModel):
    expected: int
    searched: int
    unavailable: int
    skipped: int
    pending: int
    complete: bool
    booking_ready: bool
    issues: list[str]


def assess_hotel_research_coverage(plan: HotelResearchPlan) -> HotelCoverageReport:
    """Verify that transit, all comparison providers, and direct verification were attempted."""

    issues: list[str] = []
    identifiers: set[str] = set()
    for task in plan.tasks:
        if task.task_id in identifiers:
            issues.append(f"duplicate task_id: {task.task_id}")
        identifiers.add(task.task_id)
        if task.status in {"unavailable", "skipped"} and not task.note:
            issues.append(f"{task.status} task lacks reason: {task.task_id}")
        if task.status == "searched" and not task.source_ids:
            issues.append(f"searched task lacks source evidence: {task.task_id}")
    pending = sum(task.status == "pending" for task in plan.tasks)
    searched = sum(task.status == "searched" for task in plan.tasks)
    unavailable = sum(task.status == "unavailable" for task in plan.tasks)
    skipped = sum(task.status == "skipped" for task in plan.tasks)
    if pending:
        issues.append(f"{pending} hotel research tasks remain pending")
    complete = pending == 0 and not any("lacks reason" in issue for issue in issues)
    official_verified = any(
        task.provider == "official" and task.status == "searched" and task.source_ids
        for task in plan.tasks
    )
    transit_verified = any(
        task.phase == "area_transit" and task.status == "searched" and task.source_ids
        for task in plan.tasks
    )
    discovery_count = sum(
        task.phase == "price_discovery" and task.status == "searched"
        for task in plan.tasks
    )
    booking_ready = (
        complete
        and not issues
        and official_verified
        and transit_verified
        and discovery_count >= 2
    )
    return HotelCoverageReport(
        expected=len(plan.tasks),
        searched=searched,
        unavailable=unavailable,
        skipped=skipped,
        pending=pending,
        complete=complete,
        booking_ready=booking_ready,
        issues=issues,
    )


class TransitStop(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    mode: TransitMode
    lines: list[str] = Field(default_factory=list)
    walking_minutes: int = Field(ge=0, le=60)
    step_free: bool | None = None
    service_notes: str | None = None
    source_url: HttpUrl
    verified_at: date


class TransitAssessment(BaseModel):
    preferred_stop: TransitStop | None
    ranked_stops: list[TransitStop]
    issues: list[str]
    warnings: list[str]


class MobilityAnchor(BaseModel):
    """A place that must be practically reachable from a hotel."""

    model_config = ConfigDict(extra="forbid")

    anchor_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    name: str = Field(min_length=1)
    category: Literal["airport", "station", "activity", "city_center", "other"]
    weight: Decimal = Field(default=Decimal("1"), gt=0, le=10)
    required: bool = True
    needed_departure_local: time | None = None

    @field_validator("weight", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("mobility weights must use decimal strings or integers")
        return value


class TransitJourney(BaseModel):
    """One verified public-transport journey from a hotel to an anchor."""

    model_config = ConfigDict(extra="forbid")

    anchor_id: str
    total_minutes: int = Field(gt=0, le=360)
    walking_minutes: int = Field(ge=0, le=120)
    transfers: int = Field(ge=0, le=8)
    modes: list[TransitMode] = Field(min_length=1)
    frequency_minutes: int | None = Field(default=None, gt=0, le=240)
    first_departure_local: time | None = None
    last_departure_local: time | None = None
    step_free: bool | None = None
    source_url: HttpUrl
    verified_at: date


class AnchorMobilityResult(BaseModel):
    anchor_id: str
    score: int = Field(ge=0, le=100)
    journey: TransitJourney
    warnings: list[str]


class HotelMobilityAssessment(BaseModel):
    score: int = Field(ge=0, le=100)
    anchor_results: list[AnchorMobilityResult]
    issues: list[str]
    warnings: list[str]
    complete: bool


def _service_covers(required: time, first: time, last: time) -> bool:
    if first <= last:
        return first <= required <= last
    return required >= first or required <= last


def assess_hotel_mobility(
    anchors: list[MobilityAnchor],
    journeys: list[TransitJourney],
    *,
    maximum_walking_minutes: int = 15,
    step_free_required: bool = False,
) -> HotelMobilityAssessment:
    """Score verified door-to-door journeys instead of station proximity alone."""

    if not anchors:
        raise ValueError("at least one mobility anchor is required")
    if maximum_walking_minutes < 1:
        raise ValueError("maximum_walking_minutes must be positive")

    issues: list[str] = []
    warnings: list[str] = []
    anchor_ids = {anchor.anchor_id for anchor in anchors}
    journey_map: dict[str, TransitJourney] = {}
    for supplied_journey in journeys:
        if supplied_journey.anchor_id not in anchor_ids:
            issues.append(f"journey references unknown anchor: {supplied_journey.anchor_id}")
        elif supplied_journey.anchor_id in journey_map:
            issues.append(f"duplicate journey for anchor: {supplied_journey.anchor_id}")
        else:
            journey_map[supplied_journey.anchor_id] = supplied_journey

    results: list[AnchorMobilityResult] = []
    weighted_score = Decimal("0")
    total_weight = Decimal("0")
    for anchor in anchors:
        matched_journey = journey_map.get(anchor.anchor_id)
        if matched_journey is None:
            message = f"missing journey to {anchor.anchor_id}"
            (issues if anchor.required else warnings).append(message)
            continue
        item_warnings: list[str] = []
        score = 100
        score -= min(55, matched_journey.total_minutes)
        score -= matched_journey.transfers * 8
        score -= max(0, matched_journey.walking_minutes - 8) * 2
        if matched_journey.frequency_minutes is None:
            item_warnings.append("service frequency is not verified")
            score -= 5
        else:
            score -= min(15, max(0, matched_journey.frequency_minutes - 10) // 2)
        if set(matched_journey.modes) == {"bus"}:
            item_warnings.append("journey relies on bus only")
            score -= 8
        if matched_journey.walking_minutes > maximum_walking_minutes:
            issues.append(f"journey to {anchor.anchor_id} exceeds walking limit")
        if step_free_required and matched_journey.step_free is not True:
            issues.append(f"step-free journey to {anchor.anchor_id} is not verified")
        elif matched_journey.step_free is None:
            item_warnings.append("step-free status is unknown")
        if anchor.needed_departure_local is not None:
            if (
                matched_journey.first_departure_local is None
                or matched_journey.last_departure_local is None
            ):
                issues.append(f"service hours to {anchor.anchor_id} are not verified")
            elif not _service_covers(
                anchor.needed_departure_local,
                matched_journey.first_departure_local,
                matched_journey.last_departure_local,
            ):
                issues.append(f"service to {anchor.anchor_id} does not cover required time")
        score = max(0, score)
        results.append(
            AnchorMobilityResult(
                anchor_id=anchor.anchor_id,
                score=score,
                journey=matched_journey,
                warnings=item_warnings,
            )
        )
        warnings.extend(f"{anchor.anchor_id}: {warning}" for warning in item_warnings)
        weighted_score += Decimal(score) * anchor.weight
        total_weight += anchor.weight

    overall = int((weighted_score / total_weight).quantize(Decimal("1"))) if total_weight else 0
    return HotelMobilityAssessment(
        score=overall,
        anchor_results=results,
        issues=issues,
        warnings=warnings,
        complete=not issues and len(results) == len(anchors),
    )


def assess_transit_access(
    stops: list[TransitStop], request: HotelSearchRequest
) -> TransitAssessment:
    """Rank nearby transit with metro/tram first, then rail, bus, and other modes."""

    nearby = [
        stop
        for stop in stops
        if stop.walking_minutes <= request.maximum_transit_walk_minutes
        and (not request.step_free_required or stop.step_free is True)
    ]
    ranked = sorted(
        nearby,
        key=lambda stop: (_TRANSIT_PRIORITY[stop.mode], stop.walking_minutes, stop.name),
    )
    issues: list[str] = []
    warnings: list[str] = []
    if not nearby:
        issues.append("no suitable public transport within the walking limit")
    elif not any(stop.mode in {"metro", "tram"} for stop in nearby):
        warnings.append("no nearby metro or tram; using lower-priority transport")
    if request.step_free_required and not any(stop.step_free is True for stop in stops):
        issues.append("step-free access is not verified")
    return TransitAssessment(
        preferred_stop=ranked[0] if ranked else None,
        ranked_stops=ranked,
        issues=issues,
        warnings=warnings,
    )


class CancellationPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refundable: bool
    free_until: datetime | None = None
    penalty: Decimal = Field(default=Decimal("0"), ge=0)
    details: str = Field(min_length=1)

    @field_validator("penalty", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("cancellation penalties must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def validate_refund_window(self) -> "CancellationPolicy":
        if self.refundable and self.free_until is None:
            raise ValueError("refundable rates require a free cancellation deadline")
        if self.free_until is not None and self.free_until.tzinfo is None:
            raise ValueError("cancellation deadline must be timezone-aware")
        return self


class HotelRateQuote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quote_id: str
    property_id: str
    provider: HotelProvider
    property_url: HttpUrl
    observed_at: datetime
    room_key: str = Field(min_length=1)
    room_name: str = Field(min_length=1)
    nights: int = Field(ge=1)
    rooms: int = Field(ge=1)
    guests: int = Field(ge=1)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    nightly_rate: Decimal = Field(ge=0)
    taxes: Decimal = Field(default=Decimal("0"), ge=0)
    city_tax: Decimal = Field(default=Decimal("0"), ge=0)
    resort_fee: Decimal = Field(default=Decimal("0"), ge=0)
    cleaning_fee: Decimal = Field(default=Decimal("0"), ge=0)
    service_fee: Decimal = Field(default=Decimal("0"), ge=0)
    breakfast_cost: Decimal = Field(default=Decimal("0"), ge=0)
    other_fees: Decimal = Field(default=Decimal("0"), ge=0)
    breakfast_included: bool = False
    available: bool = True
    cancellation: CancellationPolicy
    total: Decimal | None = Field(default=None, ge=0)

    @field_validator(
        "nightly_rate",
        "taxes",
        "city_tax",
        "resort_fee",
        "cleaning_fee",
        "service_fee",
        "breakfast_cost",
        "other_fees",
        "total",
        mode="before",
    )
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("hotel prices must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def calculate_total(self) -> "HotelRateQuote":
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        expected = (
            self.nightly_rate * self.nights * self.rooms
            + self.taxes
            + self.city_tax
            + self.resort_fee
            + self.cleaning_fee
            + self.service_fee
            + self.breakfast_cost
            + self.other_fees
        ).quantize(Decimal("0.01"))
        if self.total is None:
            self.total = expected
        elif abs(self.total - expected) > Decimal("0.01"):
            raise ValueError(f"hotel total {self.total} does not equal final price {expected}")
        parsed = urlparse(str(self.property_url))
        hostname = (parsed.hostname or "").removeprefix("www.")
        path = parsed.path.rstrip("/")
        expected_domains = {
            "google_hotels": "google.com",
            "booking": "booking.com",
            "agoda": "agoda.com",
            "trip_com": "trip.com",
        }
        if self.provider in expected_domains:
            expected_domain = expected_domains[self.provider]
            if hostname != expected_domain and not hostname.endswith(f".{expected_domain}"):
                raise ValueError(
                    f"{self.provider} quote URL must use {expected_domain}"
                )
            if not path:
                raise ValueError("comparison quote requires a property-specific URL")
        elif any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in expected_domains.values()
        ):
            raise ValueError("official hotel quote cannot use an aggregator URL")
        return self

    @property
    def bookable(self) -> bool:
        return self.provider != "google_hotels"


class HotelProperty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    property_id: str
    name: str = Field(min_length=1)
    city: str = Field(min_length=1)
    neighborhood: str = Field(min_length=1)
    official_url: HttpUrl
    transit_stops: list[TransitStop] = Field(default_factory=list)
    quotes: list[HotelRateQuote] = Field(default_factory=list)

    @model_validator(mode="after")
    def official_link_is_direct(self) -> "HotelProperty":
        hostname = (urlparse(str(self.official_url)).hostname or "").removeprefix("www.")
        if any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in {"google.com", "booking.com", "agoda.com", "trip.com"}
        ):
            raise ValueError("official_url must point to the property, not a comparison site")
        return self


class HotelComparison(BaseModel):
    property_id: str
    preferred_quote_id: str | None
    direct_preferred: bool
    comparable_quotes: list[HotelRateQuote]
    transit: TransitAssessment
    complete: bool
    issues: list[str]
    reasons: list[str]


def compare_hotel_property(
    hotel: HotelProperty, request: HotelSearchRequest, room_key: str
) -> HotelComparison:
    """Normalize final prices and select the best comparable booking channel."""

    issues: list[str] = []
    reasons: list[str] = []
    transit = assess_transit_access(hotel.transit_stops, request)
    reasons.extend(transit.warnings)
    candidates = [
        quote
        for quote in hotel.quotes
        if quote.property_id == hotel.property_id
        and quote.room_key == room_key
        and quote.available
        and quote.nights == request.nights
        and quote.rooms == request.rooms
        and quote.guests == request.guests
        and quote.currency == request.currency
        and (not request.breakfast_required or quote.breakfast_included)
        and (
            not request.free_cancellation_required
            or quote.cancellation.refundable
        )
    ]
    providers = {quote.provider for quote in candidates}
    if "google_hotels" not in providers:
        issues.append("Google Hotels discovery quote missing")
    if "booking" not in providers:
        issues.append("Booking.com comparison quote missing")
    if not providers.intersection({"agoda", "trip_com"}):
        issues.append("Agoda or Trip.com comparison quote missing")
    if "official" not in providers:
        issues.append("official hotel quote missing")
    hotel_hostname = urlparse(str(hotel.official_url)).hostname
    for quote in candidates:
        if quote.provider == "official" and (
            urlparse(str(quote.property_url)).hostname != hotel_hostname
        ):
            issues.append("official quote URL does not match the property website")
    bookable = [quote for quote in candidates if quote.bookable]
    if not bookable:
        return HotelComparison(
            property_id=hotel.property_id,
            preferred_quote_id=None,
            direct_preferred=False,
            comparable_quotes=[],
            transit=transit,
            complete=False,
            issues=[*issues, "no comparable bookable quote"],
            reasons=reasons,
        )
    ranked = sorted(
        bookable,
        key=lambda quote: (
            quote.total or Decimal("0"),
            0 if quote.provider == "official" else 1,
            quote.quote_id,
        ),
    )
    cheapest = ranked[0]
    official = next((quote for quote in ranked if quote.provider == "official"), None)
    preferred = cheapest
    direct_preferred = False
    if official is not None and official.total is not None and cheapest.total is not None:
        if official.total <= cheapest.total:
            preferred = official
            direct_preferred = True
            reasons.append("official channel is the same price or cheaper")
        else:
            reasons.append(
                f"official channel costs {official.total - cheapest.total} {request.currency} more"
            )
    if request.maximum_total is not None and (
        preferred.total is None or preferred.total > request.maximum_total
    ):
        issues.append("preferred quote exceeds maximum total budget")
    if transit.issues:
        issues.extend(transit.issues)
    return HotelComparison(
        property_id=hotel.property_id,
        preferred_quote_id=preferred.quote_id,
        direct_preferred=direct_preferred,
        comparable_quotes=ranked,
        transit=transit,
        complete=not issues,
        issues=issues,
        reasons=reasons,
    )
