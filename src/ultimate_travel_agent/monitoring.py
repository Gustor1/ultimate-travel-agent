"""Pre-departure revalidation schedules and due-task selection."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ultimate_travel_agent.contracts import TravelDossierV1

PriceAlertStatus = Literal["target_reached", "price_drop", "price_rise", "stale"]


def _default_price_alert_statuses() -> list[PriceAlertStatus]:
    return ["target_reached", "price_drop", "price_rise", "stale"]


class RevalidationTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    category: Literal["claim", "formalities", "weather", "disruptions"]
    due_on: date
    reason: str
    claim_id: str | None = None
    status: Literal["pending", "complete", "failed"] = "pending"


def _not_before_today(value: date, today: date) -> date:
    return max(value, today)


def build_revalidation_plan(
    dossier: TravelDossierV1, departure_date: date, today: date | None = None
) -> list[RevalidationTask]:
    """Build a stable verification calendar without performing external writes."""

    current = today or date.today()
    tasks: list[RevalidationTask] = []
    for claim in dossier.claims:
        due = departure_date - timedelta(days=7 if claim.critical else 14)
        if claim.expires_at is not None:
            due = min(due, claim.expires_at)
        if claim.status in {"unverified", "estimated", "outdated"}:
            due = current
        tasks.append(
            RevalidationTask(
                task_id=f"claim-{claim.claim_id}",
                category="claim",
                due_on=_not_before_today(due, current),
                reason=f"Revalidate {claim.status} claim before departure",
                claim_id=claim.claim_id,
            )
        )
    recurring: tuple[
        tuple[Literal["formalities", "weather", "disruptions"], int, str], ...
    ] = (
        ("formalities", 30, "Recheck entry, health, and document rules"),
        ("weather", 3, "Refresh forecast and packing advice"),
        ("disruptions", 1, "Check transport and local disruptions"),
    )
    for category, days, reason in recurring:
        tasks.append(
            RevalidationTask(
                task_id=f"system-{category}",
                category=category,
                due_on=_not_before_today(departure_date - timedelta(days=days), current),
                reason=reason,
            )
        )
    return sorted(tasks, key=lambda task: (task.due_on, task.task_id))


def due_tasks(tasks: list[RevalidationTask], on_date: date | None = None) -> list[RevalidationTask]:
    """Select pending tasks due by the requested day."""

    current = on_date or date.today()
    return [task for task in tasks if task.status == "pending" and task.due_on <= current]


class PriceWatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    watch_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    subject: Literal["flight", "hotel", "package"]
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    target_price: Decimal = Field(gt=0)
    change_threshold_percent: Decimal = Field(default=Decimal("5"), gt=0, le=100)
    maximum_age_hours: int = Field(default=24, ge=1, le=168)

    @field_validator("target_price", "change_threshold_percent", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("price watch values must use decimal strings or integers")
        return value


class PriceObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    watch_id: str
    amount: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    observed_at: datetime
    source_id: str = Field(min_length=1)

    @field_validator("amount", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("observed prices must use decimal strings or integers")
        return value

    @model_validator(mode="after")
    def timezone_is_required(self) -> "PriceObservation":
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        return self


class PriceWatchAssessment(BaseModel):
    watch_id: str
    status: Literal["target_reached", "price_drop", "price_rise", "monitor", "stale"]
    current_price: Decimal
    lowest_price: Decimal
    change_from_first_percent: Decimal
    observed_at: datetime
    message: str


class PriceAlertPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    check_interval_hours: int = Field(default=12, ge=1, le=168)
    cooldown_hours: int = Field(default=24, ge=1, le=720)
    notify_on: list[PriceAlertStatus] = Field(default_factory=_default_price_alert_statuses)


class PriceAlertState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    last_status: str | None = None
    last_notified_at: datetime | None = None

    @model_validator(mode="after")
    def timezone_is_required(self) -> "PriceAlertState":
        if self.last_notified_at is not None and self.last_notified_at.tzinfo is None:
            raise ValueError("last_notified_at must be timezone-aware")
        return self


class PriceAlertEvent(BaseModel):
    event_id: str
    watch_id: str
    status: str
    created_at: datetime
    current_price: Decimal
    currency: str
    message: str


class PriceMonitoringDecision(BaseModel):
    assessment: PriceWatchAssessment
    next_check_at: datetime
    alert: PriceAlertEvent | None
    state: PriceAlertState


def assess_price_watch(
    watch: PriceWatch,
    observations: list[PriceObservation],
    *,
    now: datetime | None = None,
) -> PriceWatchAssessment:
    """Classify a sourced price history without predicting future prices."""

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if any(
        item.watch_id != watch.watch_id or item.currency != watch.currency
        for item in observations
    ):
        raise ValueError("all observations must match watch_id and currency")
    if not observations:
        raise ValueError("price watch requires at least one matching observation")
    ordered = sorted(observations, key=lambda item: item.observed_at)
    if ordered[-1].observed_at > current_time:
        raise ValueError("price observations cannot be in the future")
    first = ordered[0]
    latest = ordered[-1]
    change = ((latest.amount - first.amount) / first.amount * Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    age = current_time - latest.observed_at
    threshold = watch.change_threshold_percent
    if age > timedelta(hours=watch.maximum_age_hours):
        status: Literal["target_reached", "price_drop", "price_rise", "monitor", "stale"] = (
            "stale"
        )
        message = "latest price is stale; refresh before making a decision"
    elif latest.amount <= watch.target_price:
        status = "target_reached"
        message = "price is at or below the configured target"
    elif change <= -threshold:
        status = "price_drop"
        message = "price dropped beyond the configured change threshold"
    elif change >= threshold:
        status = "price_rise"
        message = "price rose beyond the configured change threshold"
    else:
        status = "monitor"
        message = "no configured alert threshold has been reached"
    return PriceWatchAssessment(
        watch_id=watch.watch_id,
        status=status,
        current_price=latest.amount.quantize(Decimal("0.01")),
        lowest_price=min(item.amount for item in ordered).quantize(Decimal("0.01")),
        change_from_first_percent=change,
        observed_at=latest.observed_at,
        message=message,
    )


def schedule_price_watch(
    watch: PriceWatch,
    observations: list[PriceObservation],
    policy: PriceAlertPolicy | None = None,
    state: PriceAlertState | None = None,
    *,
    now: datetime | None = None,
) -> PriceMonitoringDecision:
    """Create a deduplicated alert event and the next scheduler deadline."""

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    active_policy = policy or PriceAlertPolicy()
    previous = state or PriceAlertState()
    assessment = assess_price_watch(watch, observations, now=current_time)
    alert: PriceAlertEvent | None = None
    cooldown_passed = (
        previous.last_notified_at is None
        or current_time - previous.last_notified_at
        >= timedelta(hours=active_policy.cooldown_hours)
    )
    should_notify = assessment.status in active_policy.notify_on and (
        assessment.status != previous.last_status or cooldown_passed
    )
    updated_state = previous.model_copy(deep=True)
    if should_notify:
        alert = PriceAlertEvent(
            event_id=f"{watch.watch_id}-{assessment.status}-{int(current_time.timestamp())}",
            watch_id=watch.watch_id,
            status=assessment.status,
            created_at=current_time,
            current_price=assessment.current_price,
            currency=watch.currency,
            message=assessment.message,
        )
        updated_state.last_status = assessment.status
        updated_state.last_notified_at = current_time
    return PriceMonitoringDecision(
        assessment=assessment,
        next_check_at=current_time + timedelta(hours=active_policy.check_interval_hours),
        alert=alert,
        state=updated_state,
    )
