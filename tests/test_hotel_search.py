from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from ultimate_travel_agent.hotel_search import (
    CancellationPolicy,
    HotelProperty,
    HotelRateQuote,
    HotelSearchRequest,
    MobilityAnchor,
    TransitJourney,
    TransitStop,
    assess_hotel_mobility,
    assess_hotel_research_coverage,
    assess_transit_access,
    compare_hotel_property,
    generate_hotel_research_plan,
)
from ultimate_travel_agent.validator import validate_accommodation_search_skill_file


def _request() -> HotelSearchRequest:
    data = yaml.safe_load(
        Path("examples/hotel-search/paris-transit.yaml").read_text(encoding="utf-8")
    )
    return HotelSearchRequest.model_validate(data)


def _cancellation() -> CancellationPolicy:
    return CancellationPolicy(
        refundable=True,
        free_until="2027-05-08T18:00:00+02:00",
        details="Free cancellation until two days before arrival",
    )


def _quote(
    quote_id: str,
    provider: str,
    url: str,
    nightly_rate: str,
    taxes: str = "0",
) -> HotelRateQuote:
    return HotelRateQuote.model_validate(
        {
            "quote_id": quote_id,
            "property_id": "hotel-1",
            "provider": provider,
            "property_url": url,
            "observed_at": "2026-09-19T10:00:00Z",
            "room_key": "double-refundable",
            "room_name": "Double room",
            "nights": 3,
            "rooms": 1,
            "guests": 2,
            "currency": "EUR",
            "nightly_rate": nightly_rate,
            "taxes": taxes,
            "breakfast_included": True,
            "cancellation": _cancellation().model_dump(),
        }
    )


def _stops() -> list[TransitStop]:
    return [
        TransitStop(
            name="Bus Stop",
            mode="bus",
            lines=["91"],
            walking_minutes=1,
            step_free=True,
            source_url="https://www.ratp.fr/lignes/bus/91",
            verified_at=date(2026, 9, 19),
        ),
        TransitStop(
            name="Bastille",
            mode="metro",
            lines=["1", "5", "8"],
            walking_minutes=8,
            step_free=True,
            source_url="https://www.ratp.fr/decouvrir/coulisses/metro/bastille",
            verified_at=date(2026, 9, 19),
        ),
        TransitStop(
            name="Tram Test",
            mode="tram",
            lines=["T3"],
            walking_minutes=4,
            step_free=True,
            source_url="https://www.ratp.fr/lignes/tramway/t3",
            verified_at=date(2026, 9, 19),
        ),
    ]


def _hotel(official_nightly: str = "110") -> HotelProperty:
    return HotelProperty(
        property_id="hotel-1",
        name="Transit Hotel",
        city="Paris",
        neighborhood="Bastille",
        official_url="https://hotel.example.com/book",
        transit_stops=_stops(),
        quotes=[
            _quote(
                "google",
                "google_hotels",
                "https://www.google.com/travel/hotels/entity/hotel-1",
                "105",
                "15",
            ),
            _quote(
                "booking",
                "booking",
                "https://www.booking.com/hotel/fr/transit-hotel.html",
                "110",
                "20",
            ),
            _quote(
                "agoda",
                "agoda",
                "https://www.agoda.com/transit-hotel/hotel/paris-fr.html",
                "115",
                "15",
            ),
            _quote(
                "official",
                "official",
                "https://hotel.example.com/book/double-refundable",
                official_nightly,
                "20",
            ),
        ],
    )


def test_research_plan_covers_transit_comparators_and_official() -> None:
    plan = generate_hotel_research_plan(_request())
    assert len(plan.tasks) == 6
    assert [task.provider for task in plan.tasks] == [
        "official_transit",
        "google_hotels",
        "booking",
        "agoda",
        "trip_com",
        "official",
    ]
    assert not assess_hotel_research_coverage(plan).complete
    for task in plan.tasks:
        task.status = "searched"
        task.source_ids = [f"source-{task.task_id}"]
    assert assess_hotel_research_coverage(plan).booking_ready


def test_accommodation_skill_contains_extended_methodology() -> None:
    passed, issues = validate_accommodation_search_skill_file(
        Path(".agents/skills/accommodation-research/SKILL.md")
    )
    assert passed, issues


def test_unavailable_provider_requires_reason() -> None:
    plan = generate_hotel_research_plan(_request())
    for task in plan.tasks:
        task.status = "searched"
        task.source_ids = ["source"]
    plan.tasks[3].status = "unavailable"
    plan.tasks[3].source_ids = []
    assert not assess_hotel_research_coverage(plan).complete
    plan.tasks[3].note = "Provider blocked automated access"
    assert assess_hotel_research_coverage(plan).complete


def test_metro_and_tram_rank_before_closer_bus() -> None:
    assessment = assess_transit_access(_stops(), _request())
    assert assessment.preferred_stop is not None
    assert assessment.preferred_stop.mode == "metro"
    assert [stop.mode for stop in assessment.ranked_stops] == ["metro", "tram", "bus"]


def test_bus_fallback_is_visible_but_not_blocking() -> None:
    request = _request()
    bus_only = [_stops()[0]]
    assessment = assess_transit_access(bus_only, request)
    assert not assessment.issues
    assert assessment.warnings == ["no nearby metro or tram; using lower-priority transport"]


def test_step_free_and_walking_limits_are_hard_constraints() -> None:
    request = _request().model_copy(
        update={"step_free_required": True, "maximum_transit_walk_minutes": 5}
    )
    inaccessible = _stops()[1].model_copy(update={"step_free": False})
    assessment = assess_transit_access([inaccessible], request)
    assert assessment.preferred_stop is None
    assert "step-free access is not verified" in assessment.issues


def test_final_price_includes_every_fee() -> None:
    quote = HotelRateQuote.model_validate(
        {
            **_quote(
                "fees",
                "official",
                "https://hotel.example.com/book/fees",
                "100",
            ).model_dump(exclude={"total"}),
            "taxes": "20",
            "city_tax": "12",
            "resort_fee": "5",
            "cleaning_fee": "6",
            "service_fee": "7",
            "breakfast_cost": "30",
            "other_fees": "4",
        }
    )
    assert quote.total == Decimal("384.00")


def test_official_channel_wins_when_same_price() -> None:
    comparison = compare_hotel_property(_hotel(), _request(), "double-refundable")
    assert comparison.complete
    assert comparison.preferred_quote_id == "official"
    assert comparison.direct_preferred
    assert comparison.transit.preferred_stop is not None
    assert comparison.transit.preferred_stop.mode == "metro"


def test_cheaper_third_party_wins_with_exact_difference() -> None:
    comparison = compare_hotel_property(
        _hotel(official_nightly="120"), _request(), "double-refundable"
    )
    assert comparison.preferred_quote_id == "booking"
    assert not comparison.direct_preferred
    assert any("30.00 EUR more" in reason for reason in comparison.reasons)


def test_google_hotels_is_never_selected_as_booking_channel() -> None:
    hotel = _hotel()
    hotel.quotes[0] = _quote(
        "google",
        "google_hotels",
        "https://www.google.com/travel/hotels/entity/hotel-1",
        "50",
    )
    comparison = compare_hotel_property(hotel, _request(), "double-refundable")
    assert comparison.preferred_quote_id != "google"


def test_provider_urls_must_be_property_specific_and_match_provider() -> None:
    with pytest.raises(ValidationError, match="property-specific"):
        _quote("root", "booking", "https://www.booking.com", "100")
    with pytest.raises(ValidationError, match="must use agoda.com"):
        _quote(
            "wrong",
            "agoda",
            "https://www.booking.com/hotel/fr/test.html",
            "100",
        )


def test_mismatched_room_or_missing_provider_is_not_complete() -> None:
    hotel = _hotel()
    hotel.quotes = [quote for quote in hotel.quotes if quote.provider != "agoda"]
    comparison = compare_hotel_property(hotel, _request(), "double-refundable")
    assert not comparison.complete
    assert "Agoda or Trip.com comparison quote missing" in comparison.issues


def test_hotel_cli_generates_and_checks_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from ultimate_travel_agent.cli import main

    output = tmp_path / "hotel-plan.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ultimate-travel-agent",
            "hotel-search-plan",
            "examples/hotel-search/paris-transit.yaml",
            str(output),
        ],
    )
    main()
    assert output.exists()
    assert '"provider": "official_transit"' in output.read_text(encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["ultimate-travel-agent", "hotel-search-coverage", str(output)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert "6 hotel research tasks remain pending" in capsys.readouterr().out


def _journey(anchor_id: str, **updates: object) -> TransitJourney:
    data: dict[str, object] = {
        "anchor_id": anchor_id,
        "total_minutes": 25,
        "walking_minutes": 7,
        "transfers": 0,
        "modes": ["metro"],
        "frequency_minutes": 5,
        "first_departure_local": "05:30",
        "last_departure_local": "00:30",
        "step_free": True,
        "source_url": "https://www.ratp.fr/itineraires",
        "verified_at": "2026-09-19",
    }
    data.update(updates)
    return TransitJourney.model_validate(data)


def test_hotel_mobility_scores_real_weighted_destinations() -> None:
    anchors = [
        MobilityAnchor(
            anchor_id="airport",
            name="Airport",
            category="airport",
            weight="3",
            needed_departure_local="06:00",
        ),
        MobilityAnchor(
            anchor_id="museum", name="Museum", category="activity", weight="1"
        ),
    ]
    assessment = assess_hotel_mobility(
        anchors,
        [_journey("airport"), _journey("museum", total_minutes=45, transfers=1)],
    )
    assert assessment.complete
    assert assessment.score == 68
    assert [result.anchor_id for result in assessment.anchor_results] == [
        "airport",
        "museum",
    ]


def test_hotel_mobility_blocks_uncovered_hours_and_accessibility() -> None:
    anchors = [
        MobilityAnchor(
            anchor_id="airport",
            name="Airport",
            category="airport",
            needed_departure_local="04:30",
        )
    ]
    assessment = assess_hotel_mobility(
        anchors,
        [_journey("airport", step_free=None)],
        step_free_required=True,
    )
    assert not assessment.complete
    assert "service to airport does not cover required time" in assessment.issues
    assert "step-free journey to airport is not verified" in assessment.issues


def test_hotel_mobility_flags_missing_required_anchor() -> None:
    anchor = MobilityAnchor(
        anchor_id="center", name="Center", category="city_center"
    )
    assessment = assess_hotel_mobility([anchor], [])
    assert not assessment.complete
    assert assessment.score == 0
    assert assessment.issues == ["missing journey to center"]
