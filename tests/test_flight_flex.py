from __future__ import annotations

from datetime import datetime, time, timezone
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from ultimate_travel_agent.flight_flex import (
    AlternativeGateway,
    FlightOffer,
    FlightSearchRequest,
    FlightSegment,
    GatewayTransfer,
    assess_search_coverage,
    evaluate_flight_offers,
    generate_flight_search_plan,
    requires_overnight,
)


def _load_request(name: str) -> FlightSearchRequest:
    data = yaml.safe_load(
        Path(f"examples/flight-search/{name}.yaml").read_text(encoding="utf-8")
    )
    return FlightSearchRequest.model_validate(data)


def test_hong_kong_generates_complete_four_pass_matrix() -> None:
    plan = generate_flight_search_plan(_load_request("hong-kong-flexible"))
    counts = {
        number: sum(cell.pass_number == number for cell in plan.cells)
        for number in range(1, 5)
    }
    assert counts == {1: 1, 2: 2, 3: 48, 4: 96}
    assert len(plan.cells) == len({cell.cell_id for cell in plan.cells}) == 147
    assert {cell.arrival_airport for cell in plan.cells if cell.pass_number == 2} == {
        "SZX",
        "CAN",
    }
    assert all(cell.cross_border for cell in plan.cells if cell.pass_number in {2, 4})
    assert max(abs(cell.outbound_shift_days) for cell in plan.cells) == 3
    assert max(
        abs(cell.return_shift_days or 0) for cell in plan.cells
    ) == 3


def test_shanghai_gateways_use_real_airport_codes_and_full_grid() -> None:
    plan = generate_flight_search_plan(_load_request("shanghai-flexible"))
    assert {cell.arrival_airport for cell in plan.cells if cell.pass_number == 2} == {
        "HGH",
        "NKG",
        "WUX",
    }
    assert sum(cell.pass_number == 4 for cell in plan.cells) == 144


def test_fixed_dates_generate_only_passes_one_and_two() -> None:
    raw = _load_request("hong-kong-flexible").model_dump()
    raw.update({"dates_fixed": True, "flex_days": 0})
    plan = generate_flight_search_plan(FlightSearchRequest.model_validate(raw))
    assert [cell.pass_number for cell in plan.cells] == [1, 2, 2]


def test_one_way_flex_three_generates_six_date_cells() -> None:
    request = FlightSearchRequest(
        search_id="one-way",
        trip_type="one_way",
        origin_airport="CDG",
        destination_city="Tokyo",
        principal_airport="HND",
        outbound_date="2027-03-10",
        arrival_airports_flexible=False,
        flex_days=3,
    )
    plan = generate_flight_search_plan(request)
    assert sum(cell.pass_number == 3 for cell in plan.cells) == 6
    assert not any(cell.pass_number in {2, 4} for cell in plan.cells)


def test_alternative_departure_is_opt_in() -> None:
    with pytest.raises(ValidationError):
        FlightSearchRequest(
            search_id="bad-origin",
            origin_airport="CDG",
            alternative_origin_airports=["ORY"],
            destination_city="Lisbon",
            principal_airport="LIS",
            outbound_date="2027-03-10",
            return_date="2027-03-17",
        )
    request = FlightSearchRequest(
        search_id="origin-flex",
        origin_airport="CDG",
        alternative_origin_airports=["ORY"],
        departure_airports_flexible=True,
        destination_city="Lisbon",
        principal_airport="LIS",
        outbound_date="2027-03-10",
        return_date="2027-03-17",
        arrival_airports_flexible=False,
        flex_days=1,
    )
    plan = generate_flight_search_plan(request)
    assert any(cell.origin_airport == "ORY" for cell in plan.cells if cell.pass_number == 2)


def test_gateway_safety_controls_are_enforced() -> None:
    with pytest.raises(ValidationError, match="entry/visa"):
        GatewayTransfer(
            mode="high_speed_rail",
            destination="Hong Kong",
            duration_minutes=90,
            likely_cost="30",
            cross_border=True,
        )
    with pytest.raises(ValidationError, match="bags require recheck"):
        GatewayTransfer(
            mode="flight",
            destination="Shanghai",
            duration_minutes=120,
            likely_cost="80",
            separate_ticket=True,
            minimum_buffer_minutes=180,
        )


def test_maximum_five_alternative_gateways() -> None:
    gateways = [
        AlternativeGateway(
            airport_code=code,
            city=code,
            country="Test",
            transfer=GatewayTransfer(
                mode="bus", destination="Target", duration_minutes=60, likely_cost="10"
            ),
        )
        for code in ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF"]
    ]
    with pytest.raises(ValidationError):
        FlightSearchRequest(
            search_id="too-many",
            origin_airport="CDG",
            destination_city="Target",
            principal_airport="TTT",
            alternative_gateways=gateways,
            outbound_date="2027-03-10",
            return_date="2027-03-17",
        )


def test_coverage_report_proves_every_combination() -> None:
    plan = generate_flight_search_plan(_load_request("hong-kong-flexible"))
    pending = assess_search_coverage(plan)
    assert not pending.complete
    assert pending.pending == 147
    for cell in plan.cells:
        cell.status = "searched"
        cell.source_ids = ["google-flights", "airline-direct"]
        cell.result_ids = [f"result-{cell.cell_id}"]
    report = assess_search_coverage(plan, require_booking_evidence=True)
    assert report.complete and report.booking_ready
    assert report.searched_by_pass == {1: 1, 2: 2, 3: 48, 4: 96}


def test_unavailable_cells_require_reasons() -> None:
    plan = generate_flight_search_plan(_load_request("hong-kong-flexible"))
    for cell in plan.cells:
        cell.status = "searched"
    plan.cells[0].status = "unavailable"
    report = assess_search_coverage(plan)
    assert not report.complete
    assert any("lacks reason" in issue for issue in report.issues)
    plan.cells[0].note = "Comparison engine blocked this route"
    assert assess_search_coverage(plan).complete


def test_offer_arithmetic_ranking_and_self_transfer_risks() -> None:
    direct_segment = FlightSegment(
        segment_id="direct",
        carrier="Direct Air",
        flight_number="DA100",
        departure_airport="CDG",
        arrival_airport="HKG",
        departure_at="2027-03-10T10:00:00+01:00",
        arrival_at="2027-03-11T06:00:00+08:00",
    )
    baseline = FlightOffer(
        offer_id="baseline",
        cell_id="p1",
        airline="Direct Air",
        direct_url="https://airline.example/booking/search",
        booking_instructions="Select CDG to HKG on the requested dates",
        source_ids=["airline-direct"],
        verified_at="2026-09-19T10:00:00Z",
        segments=[direct_segment],
        flight_price="500",
    )
    connecting_segments = [
        FlightSegment(
            segment_id="leg-1",
            carrier="Regional Air",
            flight_number="RA200",
            departure_airport="CDG",
            arrival_airport="CAN",
            departure_at="2027-03-10T10:00:00+01:00",
            arrival_at="2027-03-11T05:00:00+08:00",
        ),
        FlightSegment(
            segment_id="leg-2",
            carrier="Regional Air",
            flight_number="RA201",
            departure_airport="CAN",
            arrival_airport="SZX",
            departure_at="2027-03-11T09:00:00+08:00",
            arrival_at="2027-03-11T10:00:00+08:00",
        ),
    ]
    alternative = FlightOffer(
        offer_id="alternative",
        cell_id="p4",
        airline="Regional Air",
        direct_url="https://regional.example/booking/search",
        booking_instructions="Select CDG to SZX and verify both segments",
        source_ids=["regional-direct"],
        verified_at="2026-09-19T10:00:00Z",
        segments=connecting_segments,
        flight_price="300",
        baggage_cost="40",
        onward_transfer_cost="50",
        origin_access_cost="20",
        separate_tickets=True,
        bags_recheck=True,
        connection_minutes=240,
        minimum_buffer_minutes=180,
        visa_or_entry_check_required=True,
    )
    assert alternative.door_to_door_total == Decimal("410.00")
    ranked = evaluate_flight_offers([baseline, alternative], "baseline")
    assert ranked[0].offer.offer_id == "alternative"
    assert ranked[0].retained
    assert "baggage reclaim and recheck required" in ranked[0].reasons
    with pytest.raises(ValidationError, match="below the minimum"):
        alternative.model_copy(
            update={"connection_minutes": 60}
        ).__class__.model_validate(
            {**alternative.model_dump(), "connection_minutes": 60}
        )


def test_last_onward_departure_can_trigger_overnight() -> None:
    transfer = GatewayTransfer(
        mode="high_speed_rail",
        destination="Hong Kong",
        duration_minutes=90,
        likely_cost="35",
        minimum_buffer_minutes=120,
        last_departure_local=time(22, 0),
    )
    late_arrival = datetime(2027, 3, 10, 21, 0, tzinfo=timezone.utc)
    early_arrival = datetime(2027, 3, 10, 18, 0, tzinfo=timezone.utc)
    assert requires_overnight(late_arrival, transfer)
    assert not requires_overnight(early_arrival, transfer)


def test_cli_generates_and_checks_search_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from ultimate_travel_agent.cli import main

    output = tmp_path / "plan.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ultimate-travel-agent",
            "flight-search-plan",
            "examples/flight-search/hong-kong-flexible.yaml",
            str(output),
        ],
    )
    main()
    assert output.exists()
    assert '"pass_number": 4' in output.read_text(encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["ultimate-travel-agent", "flight-search-coverage", str(output)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert "147 search combinations remain pending" in capsys.readouterr().out
