"""Deterministic flexible-flight search matrices and result evaluation."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from itertools import product
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


class GatewayTransfer(BaseModel):
    """Onward connection from an alternative gateway to the real destination."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["high_speed_rail", "regional_rail", "flight", "bus", "ferry", "mixed"]
    destination: str = Field(min_length=1)
    duration_minutes: int = Field(gt=0, le=1440)
    likely_cost: Decimal = Field(ge=0)
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    separate_ticket: bool = False
    cross_border: bool = False
    bags_recheck: bool = False
    minimum_buffer_minutes: int = Field(default=90, ge=45, le=720)
    visa_or_entry_check_required: bool = False
    last_departure_local: time | None = None

    @field_validator("likely_cost", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("transfer costs must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def validate_risk_controls(self) -> "GatewayTransfer":
        if self.cross_border and not self.visa_or_entry_check_required:
            raise ValueError("cross-border transfers require an entry/visa check")
        if self.separate_ticket and self.minimum_buffer_minutes < 120:
            raise ValueError("separate-ticket transfers require at least a 120-minute buffer")
        if self.mode == "flight" and self.separate_ticket and not self.bags_recheck:
            raise ValueError("separate domestic flights must state that bags require recheck")
        return self


class AlternativeGateway(BaseModel):
    model_config = ConfigDict(extra="forbid")

    airport_code: str = Field(pattern=r"^[A-Z]{3}$")
    city: str = Field(min_length=1)
    country: str = Field(min_length=2)
    transfer: GatewayTransfer

    @field_validator("airport_code", mode="before")
    @classmethod
    def uppercase_code(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value


class FlightSearchRequest(BaseModel):
    """Bounded search request matching the four progressive passes."""

    model_config = ConfigDict(extra="forbid")

    search_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    trip_type: Literal["one_way", "round_trip"] = "round_trip"
    origin_airport: str = Field(pattern=r"^[A-Z]{3}$")
    alternative_origin_airports: list[str] = Field(default_factory=list, max_length=3)
    departure_airports_flexible: bool = False
    destination_city: str = Field(min_length=1)
    principal_airport: str = Field(pattern=r"^[A-Z]{3}$")
    alternative_gateways: list[AlternativeGateway] = Field(default_factory=list, max_length=5)
    arrival_airports_flexible: bool = True
    outbound_date: date
    return_date: date | None = None
    dates_fixed: bool = False
    flex_days: int = Field(default=3, ge=0, le=3)
    passengers: int = Field(default=1, ge=1, le=30)
    checked_bags: int = Field(default=0, ge=0, le=30)
    comparison_currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    max_flight_stops: int = Field(default=2, ge=0, le=2)
    include_domestic_connections: bool = True

    @field_validator(
        "origin_airport", "principal_airport", "alternative_origin_airports", mode="before"
    )
    @classmethod
    def uppercase_codes(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.upper()
        if isinstance(value, list):
            return [item.upper() if isinstance(item, str) else item for item in value]
        return value

    @model_validator(mode="after")
    def validate_search_shape(self) -> "FlightSearchRequest":
        if self.trip_type == "round_trip":
            if self.return_date is None:
                raise ValueError("round-trip searches require return_date")
            if self.return_date <= self.outbound_date:
                raise ValueError("return_date must be after outbound_date")
        elif self.return_date is not None:
            raise ValueError("one-way searches cannot include return_date")
        if self.dates_fixed and self.flex_days != 0:
            raise ValueError("fixed-date searches require flex_days=0")
        if not self.arrival_airports_flexible and self.alternative_gateways:
            raise ValueError("alternative gateways require arrival_airports_flexible=true")
        if not self.departure_airports_flexible and self.alternative_origin_airports:
            raise ValueError(
                "alternative origins require departure_airports_flexible=true"
            )
        codes = [gateway.airport_code for gateway in self.alternative_gateways]
        if self.principal_airport in codes:
            raise ValueError("principal airport cannot also be an alternative gateway")
        if len(codes) != len(set(codes)):
            raise ValueError("alternative gateway airport codes must be unique")
        origins = [self.origin_airport, *self.alternative_origin_airports]
        if len(origins) != len(set(origins)):
            raise ValueError("origin airport codes must be unique")
        return self


CellStatus = Literal["pending", "searched", "unavailable", "skipped"]


class FlightSearchCell(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cell_id: str
    pass_number: Literal[1, 2, 3, 4]
    origin_airport: str
    arrival_airport: str
    outbound_date: date
    return_date: date | None = None
    outbound_shift_days: int
    return_shift_days: int | None = None
    transfer_required: bool = False
    separate_ticket: bool = False
    cross_border: bool = False
    max_flight_stops: int = Field(default=2, ge=0, le=2)
    include_domestic_connections: bool = True
    status: CellStatus = "pending"
    source_ids: list[str] = Field(default_factory=list)
    result_ids: list[str] = Field(default_factory=list)
    note: str | None = None


class FlightSearchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: FlightSearchRequest
    cells: list[FlightSearchCell]


def _date_variants(request: FlightSearchRequest) -> list[tuple[int, int | None, date, date | None]]:
    offsets = range(-request.flex_days, request.flex_days + 1)
    variants: list[tuple[int, int | None, date, date | None]] = []
    if request.trip_type == "one_way":
        for outbound_shift in offsets:
            if outbound_shift == 0:
                continue
            variants.append(
                (
                    outbound_shift,
                    None,
                    request.outbound_date + timedelta(days=outbound_shift),
                    None,
                )
            )
        return variants
    assert request.return_date is not None
    for outbound_shift, return_shift in product(offsets, repeat=2):
        if outbound_shift == 0 and return_shift == 0:
            continue
        outbound = request.outbound_date + timedelta(days=outbound_shift)
        returning = request.return_date + timedelta(days=return_shift)
        if returning > outbound:
            variants.append((outbound_shift, return_shift, outbound, returning))
    return variants


def _cell(
    request: FlightSearchRequest,
    pass_number: Literal[1, 2, 3, 4],
    origin: str,
    arrival: str,
    outbound: date,
    returning: date | None,
    outbound_shift: int,
    return_shift: int | None,
) -> FlightSearchCell:
    gateway = next(
        (item for item in request.alternative_gateways if item.airport_code == arrival), None
    )
    return_text = returning.isoformat() if returning else "one-way"
    return FlightSearchCell(
        cell_id=(
            f"p{pass_number}-{origin}-{arrival}-{outbound.isoformat()}-{return_text}"
        ),
        pass_number=pass_number,
        origin_airport=origin,
        arrival_airport=arrival,
        outbound_date=outbound,
        return_date=returning,
        outbound_shift_days=outbound_shift,
        return_shift_days=return_shift,
        transfer_required=gateway is not None,
        separate_ticket=gateway.transfer.separate_ticket if gateway else False,
        cross_border=gateway.transfer.cross_border if gateway else False,
        max_flight_stops=request.max_flight_stops,
        include_domestic_connections=request.include_domestic_connections,
    )


def generate_flight_search_plan(request: FlightSearchRequest) -> FlightSearchPlan:
    """Generate every required cell for all applicable passes, without network access."""

    cells = [
        _cell(
            request,
            1,
            request.origin_airport,
            request.principal_airport,
            request.outbound_date,
            request.return_date,
            0,
            0 if request.return_date else None,
        )
    ]
    origins = [request.origin_airport]
    if request.departure_airports_flexible:
        origins.extend(request.alternative_origin_airports)
    arrivals = [request.principal_airport]
    if request.arrival_airports_flexible:
        arrivals.extend(item.airport_code for item in request.alternative_gateways)
    alternative_routes = [
        (origin, arrival)
        for origin, arrival in product(origins, arrivals)
        if (origin, arrival) != (request.origin_airport, request.principal_airport)
    ]
    cells.extend(
        _cell(
            request,
            2,
            origin,
            arrival,
            request.outbound_date,
            request.return_date,
            0,
            0 if request.return_date else None,
        )
        for origin, arrival in alternative_routes
    )
    if request.flex_days:
        variants = _date_variants(request)
        cells.extend(
            _cell(
                request,
                3,
                request.origin_airport,
                request.principal_airport,
                outbound,
                returning,
                outbound_shift,
                return_shift,
            )
            for outbound_shift, return_shift, outbound, returning in variants
        )
        cells.extend(
            _cell(
                request,
                4,
                origin,
                arrival,
                outbound,
                returning,
                outbound_shift,
                return_shift,
            )
            for origin, arrival in alternative_routes
            for outbound_shift, return_shift, outbound, returning in variants
        )
    return FlightSearchPlan(request=request, cells=cells)


class CoverageReport(BaseModel):
    expected_by_pass: dict[int, int]
    searched_by_pass: dict[int, int]
    unavailable: int
    skipped: int
    pending: int
    complete: bool
    booking_ready: bool
    issues: list[str]


def assess_search_coverage(
    plan: FlightSearchPlan, require_booking_evidence: bool = False
) -> CoverageReport:
    """Prove whether every generated combination was attempted and documented."""

    expected = {number: 0 for number in range(1, 5)}
    searched = {number: 0 for number in range(1, 5)}
    issues: list[str] = []
    ids: set[str] = set()
    has_booking_evidence = True
    for cell in plan.cells:
        expected[cell.pass_number] += 1
        if cell.cell_id in ids:
            issues.append(f"duplicate cell_id: {cell.cell_id}")
        ids.add(cell.cell_id)
        if cell.status == "searched":
            searched[cell.pass_number] += 1
            if not cell.source_ids or not cell.result_ids:
                has_booking_evidence = False
                if require_booking_evidence:
                    issues.append(
                        f"searched cell lacks source evidence or result IDs: {cell.cell_id}"
                    )
        elif cell.status in {"unavailable", "skipped"} and not cell.note:
            issues.append(f"{cell.status} cell lacks reason: {cell.cell_id}")
    pending = sum(cell.status == "pending" for cell in plan.cells)
    unavailable = sum(cell.status == "unavailable" for cell in plan.cells)
    skipped = sum(cell.status == "skipped" for cell in plan.cells)
    if pending:
        issues.append(f"{pending} search combinations remain pending")
    for number, count in expected.items():
        if count and searched[number] == 0:
            issues.append(f"pass {number} has no successful search")
    complete = pending == 0 and not any("lacks reason" in issue for issue in issues)
    booking_ready = complete and not issues and searched[1] > 0 and has_booking_evidence
    return CoverageReport(
        expected_by_pass=expected,
        searched_by_pass=searched,
        unavailable=unavailable,
        skipped=skipped,
        pending=pending,
        complete=complete,
        booking_ready=booking_ready,
        issues=issues,
    )


class FlightSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment_id: str
    carrier: str = Field(min_length=1)
    flight_number: str = Field(min_length=2)
    departure_airport: str = Field(pattern=r"^[A-Z]{3}$")
    arrival_airport: str = Field(pattern=r"^[A-Z]{3}$")
    departure_at: datetime
    arrival_at: datetime

    @model_validator(mode="after")
    def validate_times(self) -> "FlightSegment":
        if self.departure_at.tzinfo is None or self.arrival_at.tzinfo is None:
            raise ValueError("flight segment timestamps must be timezone-aware")
        if self.arrival_at <= self.departure_at:
            raise ValueError("flight segment arrival must follow departure")
        return self


class FlightOffer(BaseModel):
    """Verified offer with exact door-to-door arithmetic and transfer safeguards."""

    model_config = ConfigDict(extra="forbid")

    offer_id: str
    cell_id: str
    airline: str = Field(min_length=1)
    direct_url: HttpUrl
    booking_instructions: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    verified_at: datetime
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    segments: list[FlightSegment] = Field(min_length=1, max_length=8)
    flight_price: Decimal = Field(ge=0)
    baggage_cost: Decimal = Field(default=Decimal("0"), ge=0)
    origin_access_cost: Decimal = Field(default=Decimal("0"), ge=0)
    onward_transfer_cost: Decimal = Field(default=Decimal("0"), ge=0)
    overnight_cost: Decimal = Field(default=Decimal("0"), ge=0)
    additional_fees: Decimal = Field(default=Decimal("0"), ge=0)
    time_penalty: Decimal = Field(default=Decimal("0"), ge=0)
    door_to_door_total: Decimal | None = Field(default=None, ge=0)
    separate_tickets: bool = False
    bags_recheck: bool = False
    connection_minutes: int | None = Field(default=None, ge=0)
    minimum_buffer_minutes: int | None = Field(default=None, ge=0)
    visa_or_entry_check_required: bool = False

    @field_validator(
        "flight_price",
        "baggage_cost",
        "origin_access_cost",
        "onward_transfer_cost",
        "overnight_cost",
        "additional_fees",
        "time_penalty",
        "door_to_door_total",
        mode="before",
    )
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("offer costs must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def calculate_and_validate(self) -> "FlightOffer":
        expected = sum(
            (
                self.flight_price,
                self.baggage_cost,
                self.origin_access_cost,
                self.onward_transfer_cost,
                self.overnight_cost,
                self.additional_fees,
                self.time_penalty,
            ),
            Decimal("0"),
        ).quantize(Decimal("0.01"))
        if self.door_to_door_total is None:
            self.door_to_door_total = expected
        elif abs(self.door_to_door_total - expected) > Decimal("0.01"):
            raise ValueError(
                f"door_to_door_total {self.door_to_door_total} does not equal {expected}"
            )
        if self.separate_tickets:
            if self.connection_minutes is None or self.minimum_buffer_minutes is None:
                raise ValueError("separate tickets require connection and minimum buffer times")
            if self.connection_minutes < self.minimum_buffer_minutes:
                raise ValueError("separate-ticket connection is below the minimum buffer")
        if self.verified_at.tzinfo is None:
            raise ValueError("verified_at must be timezone-aware")
        for previous, current in zip(self.segments, self.segments[1:], strict=False):
            if current.departure_airport != previous.arrival_airport:
                raise ValueError("flight segments do not form a continuous route")
            if current.departure_at < previous.arrival_at:
                raise ValueError("flight segments overlap")
        from ultimate_travel_agent.validator import validate_flight_option

        valid_link, link_issues = validate_flight_option(
            {
                "direct_url": str(self.direct_url),
                "verification_date": self.verified_at.date().isoformat(),
            }
        )
        if not valid_link:
            raise ValueError("; ".join(link_issues))
        return self


class EvaluatedFlightOffer(BaseModel):
    offer: FlightOffer
    saving_amount: Decimal
    saving_percent: Decimal
    retained: bool
    reasons: list[str]


def evaluate_flight_offers(
    offers: list[FlightOffer], baseline_offer_id: str
) -> list[EvaluatedFlightOffer]:
    """Rank offers and apply the €50-or-20% alternative retention rule."""

    baseline = next((offer for offer in offers if offer.offer_id == baseline_offer_id), None)
    if baseline is None or baseline.door_to_door_total is None:
        raise ValueError("baseline offer is missing or incomplete")
    if any(offer.currency != baseline.currency for offer in offers):
        raise ValueError("all offers must be converted to the same comparison currency")
    evaluated: list[EvaluatedFlightOffer] = []
    for offer in offers:
        assert offer.door_to_door_total is not None
        saving = (baseline.door_to_door_total - offer.door_to_door_total).quantize(
            Decimal("0.01")
        )
        percent = (
            saving / baseline.door_to_door_total * Decimal("100")
            if baseline.door_to_door_total
            else Decimal("0")
        ).quantize(Decimal("0.1"))
        retained = offer.offer_id == baseline_offer_id or saving >= 50 or percent >= 20
        reasons: list[str] = []
        if offer.separate_tickets:
            reasons.append("separate-ticket self-transfer")
        if offer.bags_recheck:
            reasons.append("baggage reclaim and recheck required")
        if offer.visa_or_entry_check_required:
            reasons.append("entry or transit rules require verification")
        if not retained:
            reasons.append("saving below €50 and 20% thresholds")
        evaluated.append(
            EvaluatedFlightOffer(
                offer=offer,
                saving_amount=saving,
                saving_percent=percent,
                retained=retained,
                reasons=reasons,
            )
        )
    return sorted(
        evaluated,
        key=lambda item: (item.offer.door_to_door_total or Decimal("0"), item.offer.offer_id),
    )


def requires_overnight(
    arrival_local: datetime, transfer: GatewayTransfer, exit_buffer_minutes: int = 45
) -> bool:
    """Return whether the verified last onward departure is no longer reachable."""

    if transfer.last_departure_local is None:
        return False
    if arrival_local.tzinfo is None:
        raise ValueError("arrival_local must be timezone-aware")
    ready = arrival_local + timedelta(
        minutes=max(exit_buffer_minutes, transfer.minimum_buffer_minutes)
    )
    last_departure = datetime.combine(
        ready.date(), transfer.last_departure_local, tzinfo=ready.tzinfo
    )
    return ready > last_departure
