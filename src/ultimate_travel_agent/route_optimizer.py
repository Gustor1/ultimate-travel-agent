"""Time-window route optimization using sourced door-to-door travel minutes."""

from __future__ import annotations

from datetime import datetime, timedelta
from itertools import permutations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RouteVisit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visit_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    title: str = Field(min_length=1)
    duration_minutes: int = Field(gt=0, le=720)
    window_start: datetime
    window_end: datetime
    fixed_start: datetime | None = None

    @model_validator(mode="after")
    def valid_window(self) -> "RouteVisit":
        values = [self.window_start, self.window_end]
        if self.fixed_start is not None:
            values.append(self.fixed_start)
        if any(value.tzinfo is None for value in values):
            raise ValueError("route visit timestamps must be timezone-aware")
        if self.window_end <= self.window_start:
            raise ValueError("window_end must follow window_start")
        if self.fixed_start is not None and not (
            self.window_start <= self.fixed_start <= self.window_end
        ):
            raise ValueError("fixed_start must be inside the visit window")
        return self


class SourcedTravelTime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_id: str
    to_id: str
    minutes: int = Field(ge=0, le=1440)
    source_id: str = Field(min_length=1)


class ScheduledVisit(BaseModel):
    visit_id: str
    arrival: datetime
    start: datetime
    end: datetime
    travel_minutes: int
    waiting_minutes: int


class OptimizedRoute(BaseModel):
    ordered_visit_ids: list[str]
    schedule: list[ScheduledVisit]
    total_travel_minutes: int
    total_waiting_minutes: int
    issues: list[str]
    complete: bool


def optimize_route_with_windows(
    origin_id: str,
    day_start: datetime,
    day_end: datetime,
    visits: list[RouteVisit],
    travel_times: list[SourcedTravelTime],
    destination_id: str | None = None,
) -> OptimizedRoute:
    """Find the lowest travel+waiting route for up to eight time-window visits."""

    if day_start.tzinfo is None or day_end.tzinfo is None:
        raise ValueError("day boundaries must be timezone-aware")
    if day_end <= day_start:
        raise ValueError("day_end must follow day_start")
    if not 1 <= len(visits) <= 8:
        raise ValueError("route optimization supports between one and eight visits")
    visit_ids = [visit.visit_id for visit in visits]
    if len(visit_ids) != len(set(visit_ids)) or origin_id in visit_ids:
        raise ValueError("origin and visit IDs must be unique")
    leg_map = {(leg.from_id, leg.to_id): leg for leg in travel_times}
    if len(leg_map) != len(travel_times):
        raise ValueError("travel-time legs must be unique")

    visit_map = {visit.visit_id: visit for visit in visits}
    best: tuple[int, int, tuple[str, ...], list[ScheduledVisit]] | None = None
    missing_legs: set[tuple[str, str]] = set()
    for order in permutations(visit_ids):
        current_id = origin_id
        current_time = day_start
        schedule: list[ScheduledVisit] = []
        travel_total = 0
        waiting_total = 0
        feasible = True
        for visit_id in order:
            leg = leg_map.get((current_id, visit_id))
            if leg is None:
                missing_legs.add((current_id, visit_id))
                feasible = False
                break
            visit = visit_map[visit_id]
            arrival = current_time + timedelta(minutes=leg.minutes)
            start = max(arrival, visit.window_start)
            if visit.fixed_start is not None:
                if arrival > visit.fixed_start:
                    feasible = False
                    break
                start = visit.fixed_start
            end = start + timedelta(minutes=visit.duration_minutes)
            if end > visit.window_end or end > day_end:
                feasible = False
                break
            waiting = int((start - arrival).total_seconds() // 60)
            schedule.append(
                ScheduledVisit(
                    visit_id=visit_id,
                    arrival=arrival,
                    start=start,
                    end=end,
                    travel_minutes=leg.minutes,
                    waiting_minutes=waiting,
                )
            )
            travel_total += leg.minutes
            waiting_total += waiting
            current_id = visit_id
            current_time = end
        if feasible and destination_id is not None:
            final_leg = leg_map.get((current_id, destination_id))
            if final_leg is None:
                missing_legs.add((current_id, destination_id))
                feasible = False
            elif current_time + timedelta(minutes=final_leg.minutes) > day_end:
                feasible = False
            else:
                travel_total += final_leg.minutes
        if feasible:
            candidate = (travel_total + waiting_total, travel_total, order, schedule)
            if best is None or candidate[:3] < best[:3]:
                best = candidate
    if best is None:
        issues = [
            f"missing travel time: {from_id} -> {to_id}"
            for from_id, to_id in sorted(missing_legs)
        ]
        if not issues:
            issues.append("no route satisfies all visit windows and fixed appointments")
        return OptimizedRoute(
            ordered_visit_ids=[],
            schedule=[],
            total_travel_minutes=0,
            total_waiting_minutes=0,
            issues=issues,
            complete=False,
        )
    _, travel_total, order, schedule = best
    return OptimizedRoute(
        ordered_visit_ids=list(order),
        schedule=schedule,
        total_travel_minutes=travel_total,
        total_waiting_minutes=sum(item.waiting_minutes for item in schedule),
        issues=[],
        complete=True,
    )
