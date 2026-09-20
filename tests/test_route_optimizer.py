from datetime import datetime

from ultimate_travel_agent.route_optimizer import (
    RouteVisit,
    SourcedTravelTime,
    optimize_route_with_windows,
)


def _visit(
    visit_id: str,
    start: str = "2027-05-10T09:00:00+02:00",
    end: str = "2027-05-10T18:00:00+02:00",
    fixed: str | None = None,
) -> RouteVisit:
    return RouteVisit(
        visit_id=visit_id,
        title=visit_id,
        duration_minutes=60,
        window_start=start,
        window_end=end,
        fixed_start=fixed,
    )


def _leg(from_id: str, to_id: str, minutes: int) -> SourcedTravelTime:
    return SourcedTravelTime(
        from_id=from_id,
        to_id=to_id,
        minutes=minutes,
        source_id=f"route-{from_id}-{to_id}",
    )


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_route_optimizer_uses_real_travel_matrix_not_input_order() -> None:
    result = optimize_route_with_windows(
        "hotel",
        day_start=_dt("2027-05-10T09:00:00+02:00"),
        day_end=_dt("2027-05-10T18:00:00+02:00"),
        visits=[_visit("museum"), _visit("park")],
        travel_times=[
            _leg("hotel", "museum", 40),
            _leg("hotel", "park", 10),
            _leg("museum", "park", 50),
            _leg("park", "museum", 10),
        ],
    )
    assert result.complete
    assert result.ordered_visit_ids == ["park", "museum"]
    assert result.total_travel_minutes == 20


def test_route_optimizer_respects_fixed_appointment() -> None:
    result = optimize_route_with_windows(
        "hotel",
        day_start=_dt("2027-05-10T09:00:00+02:00"),
        day_end=_dt("2027-05-10T18:00:00+02:00"),
        visits=[
            _visit("lunch", fixed="2027-05-10T12:00:00+02:00"),
            _visit("museum"),
        ],
        travel_times=[
            _leg("hotel", "lunch", 15),
            _leg("hotel", "museum", 20),
            _leg("lunch", "museum", 10),
            _leg("museum", "lunch", 20),
        ],
    )
    assert result.complete
    lunch = next(item for item in result.schedule if item.visit_id == "lunch")
    assert lunch.start.isoformat() == "2027-05-10T12:00:00+02:00"


def test_route_optimizer_reports_incomplete_matrix() -> None:
    result = optimize_route_with_windows(
        "hotel",
        day_start=_dt("2027-05-10T09:00:00+02:00"),
        day_end=_dt("2027-05-10T18:00:00+02:00"),
        visits=[_visit("museum")],
        travel_times=[],
    )
    assert not result.complete
    assert result.issues == ["missing travel time: hotel -> museum"]


def test_route_optimizer_can_include_return_destination() -> None:
    result = optimize_route_with_windows(
        "hotel",
        day_start=_dt("2027-05-10T09:00:00+02:00"),
        day_end=_dt("2027-05-10T18:00:00+02:00"),
        visits=[_visit("museum"), _visit("park")],
        travel_times=[
            _leg("hotel", "museum", 10),
            _leg("hotel", "park", 20),
            _leg("museum", "park", 10),
            _leg("park", "museum", 10),
            _leg("museum", "hotel", 60),
            _leg("park", "hotel", 5),
        ],
        destination_id="hotel",
    )
    assert result.ordered_visit_ids == ["museum", "park"]
    assert result.total_travel_minutes == 25
