from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from ultimate_travel_agent.contracts import TravelDossierV1, validate_travel_dossier
from ultimate_travel_agent.exports import (
    export_checklist,
    export_geojson,
    export_ics,
    export_mobile_html,
    export_offline_bundle,
    export_pdf,
)
from ultimate_travel_agent.monitoring import (
    PriceObservation,
    PriceWatch,
    assess_price_watch,
    build_revalidation_plan,
    due_tasks,
)
from ultimate_travel_agent.planning import (
    CostEstimate,
    DecisionRecord,
    ExchangeRate,
    OptionMetrics,
    Place,
    PlannedStop,
    PlanScenario,
    ScoreWeights,
    analyze_route,
    calculate_budget,
    compare_scenarios,
    connection_is_safe,
    jet_lag_recovery_days,
    optimize_stop_order,
    score_options,
    upsert_decision,
)
from ultimate_travel_agent.profiles import (
    TravelerProfile,
    load_profile,
    merge_profile,
    save_profile,
)
from ultimate_travel_agent.research import ResearchState, advance_research, next_research_actions
from ultimate_travel_agent.uncertainty import assess_uncertainty


def _dossier() -> TravelDossierV1:
    return TravelDossierV1.model_validate(
        {
            "summary": "Lisbon plan",
            "recommendations": ["Use the metro"],
            "claims": [
                {
                    "claim_id": "metro.hours",
                    "text": "Metro runs late",
                    "status": "estimated",
                    "source_ids": [],
                    "critical": True,
                    "fallback": "Use a licensed taxi",
                }
            ],
            "itinerary": [
                {
                    "item_id": "arrive",
                    "title": "Arrival",
                    "start": "2027-04-15T10:00:00+01:00",
                    "end": "2027-04-15T11:00:00+01:00",
                    "location": "Lisbon",
                }
            ],
            "locations": [
                {"place_id": "lis", "name": "Lisbon", "latitude": 38.72, "longitude": -9.14}
            ],
            "verification_required": ["Metro timetable"],
            "readiness": {"booking_ready": False, "blockers": ["Fare not verified"]},
        }
    )


def test_profile_corpus_and_atomic_round_trip(tmp_path: Path) -> None:
    raw = yaml.safe_load(Path("tests/fixtures/planning_profiles.yaml").read_text(encoding="utf-8"))
    profiles = [TravelerProfile.model_validate(item) for item in raw]
    assert len(profiles) == 9
    assert {profile.mobility for profile in profiles} >= {"standard", "wheelchair"}
    path = save_profile(profiles[0], tmp_path / "nested" / "profile.json")
    assert load_profile(path) == profiles[0]
    assert merge_profile(profiles[0], {"pacing": "relaxed"}).pacing == "relaxed"
    with pytest.raises(ValidationError):
        TravelerProfile(profile_id="bad", daily_walking_km=1.2)


def test_scoring_is_stable_explainable_and_exact() -> None:
    options = [
        OptionMetrics(option_id="train", cost=70, duration=80, fatigue=90, reliability=85, flexibility=75, safety=95, carbon=100),
        OptionMetrics(option_id="flight", cost=80, duration=95, fatigue=45, reliability=70, flexibility=50, safety=95, carbon=10),
    ]
    ranked = score_options(options)
    assert ranked[0].option_id == "train"
    assert sum(ranked[0].breakdown.values()) == ranked[0].total
    with pytest.raises(ValidationError):
        ScoreWeights(cost="0.5")


def test_uncertainty_detects_conflicts_and_critical_gaps() -> None:
    dossier = _dossier()
    dossier.claims[0].confidence = 0
    dossier.claims.append(
        dossier.claims[0].model_copy(
            update={"claim_id": "metro.closed", "conflicts_with": ["metro.hours"], "critical": False}
        )
    )
    dossier.claims[0].conflicts_with = ["metro.closed"]
    report = assess_uncertainty(dossier, date(2026, 9, 19))
    assert report.overall_confidence <= 20
    assert report.claims[0].confidence == 0
    assert report.contradictions == [("metro.closed", "metro.hours")]
    assert any("critical claim" in blocker for blocker in report.blockers)


def test_geography_time_and_profile_limits() -> None:
    lisbon = Place(place_id="lis", name="Lisbon", latitude=38.7223, longitude=-9.1393, timezone="Europe/Lisbon")
    sintra = Place(place_id="sin", name="Sintra", latitude=38.8029, longitude=-9.3817, timezone="Europe/Lisbon")
    cascais = Place(place_id="cas", name="Cascais", latitude=38.6979, longitude=-9.4215, timezone="Europe/Lisbon")
    stops = [
        PlannedStop(stop_id="a", place=lisbon, start=datetime(2027, 4, 15, 9, tzinfo=timezone.utc), end=datetime(2027, 4, 15, 11, tzinfo=timezone.utc), walking_km="3"),
        PlannedStop(stop_id="b", place=sintra, start=datetime(2027, 4, 15, 11, tzinfo=timezone.utc), end=datetime(2027, 4, 15, 15, tzinfo=timezone.utc), walking_km="4"),
        PlannedStop(stop_id="c", place=cascais, start=datetime(2027, 4, 15, 16, tzinfo=timezone.utc), end=datetime(2027, 4, 15, 19, tzinfo=timezone.utc), walking_km="3"),
    ]
    assert len(optimize_stop_order(stops)) == 3
    analysis = analyze_route(stops, TravelerProfile(profile_id="slow", daily_walking_km="5", max_daily_activity_hours="7"))
    assert len(analysis.issues) >= 2
    assert connection_is_safe(stops[0].end, stops[1].start, 0)
    assert jet_lag_recovery_days("Europe/Paris", "Asia/Tokyo", date(2027, 4, 15)) == 3


def test_progressive_research_gates() -> None:
    state = ResearchState()
    blocked = advance_research(state, "dates")
    assert blocked.current_stage == "brief"
    assert blocked.pending_questions == ["select destination"]
    ready = state.model_copy(update={"completed_stages": ["brief"], "destination": "Lisbon"})
    assert advance_research(ready, "dates").current_stage == "dates"
    assert "complete" in next_research_actions(advance_research(ready, "dates"))[0]


def test_budget_scenarios_and_decisions() -> None:
    estimates = [
        CostEstimate(item_id="hotel", category="lodging", currency="EUR", low="400", likely="500", high="650"),
        CostEstimate(item_id="train", category="transport", currency="GBP", low="80", likely="100", high="140"),
    ]
    rate = ExchangeRate(from_currency="GBP", to_currency="EUR", rate="1.20", observed_at="2026-09-19T10:00:00Z", source="ECB")
    summary = calculate_budget(estimates, "EUR", [rate], category_caps={"lodging": Decimal("450")})
    assert summary.likely == Decimal("620.00")
    assert summary.likely_with_reserve == Decimal("713.00")
    assert summary.issues
    rows = compare_scenarios(
        [
            PlanScenario(scenario_id="comfort", style="comfort", option_ids=["hotel"], cost="900", duration_hours="5", fatigue=20, quality=95),
            PlanScenario(scenario_id="economy", style="economy", option_ids=["hostel"], cost="300", duration_hours="7", fatigue=60, quality=60),
        ]
    )
    assert [row["scenario_id"] for row in rows] == ["economy", "comfort"]
    decision = DecisionRecord(decision_id="lodging", topic="Hotel", chosen="A", reasons=["quiet"], decided_at="2026-09-19T10:00:00Z")
    assert upsert_decision([], decision) == [decision]


def test_exports_and_revalidation_are_portable() -> None:
    dossier = _dossier()
    assert "BEGIN:VEVENT" in export_ics(dossier)
    assert export_geojson(dossier)["features"][0]["geometry"]["coordinates"] == [-9.14, 38.72]
    assert "Metro timetable" in export_checklist(dossier)
    assert export_pdf(dossier).startswith(b"%PDF-1.4")
    assert '<meta name="viewport"' in export_mobile_html(dossier)
    assert json.dumps(export_offline_bundle(dossier))
    tasks = build_revalidation_plan(dossier, date(2027, 4, 15), date(2027, 4, 1))
    assert {task.category for task in tasks} >= {"claim", "formalities", "weather", "disruptions"}
    assert due_tasks(tasks, date(2027, 4, 1))


def test_contract_extensions_preserve_legacy_compatibility() -> None:
    passed, issues, dossier = validate_travel_dossier({"summary": "Legacy", "source_log": []})
    assert passed, issues
    assert dossier is not None and dossier.traveler_profile is None


def test_price_watch_detects_target_drop_and_stale_data() -> None:
    watch = PriceWatch(
        watch_id="flight-par-hkg",
        subject="flight",
        currency="EUR",
        target_price="500",
        change_threshold_percent="5",
        maximum_age_hours=24,
    )
    observations = [
        PriceObservation(
            watch_id=watch.watch_id,
            amount="600",
            currency="EUR",
            observed_at="2026-09-18T08:00:00Z",
            source_id="flight-source-1",
        ),
        PriceObservation(
            watch_id=watch.watch_id,
            amount="490",
            currency="EUR",
            observed_at="2026-09-19T08:00:00Z",
            source_id="flight-source-2",
        ),
    ]
    reached = assess_price_watch(
        watch, observations, now=datetime(2026, 9, 19, 9, tzinfo=timezone.utc)
    )
    assert reached.status == "target_reached"
    assert reached.change_from_first_percent == Decimal("-18.33")
    stale = assess_price_watch(
        watch, observations, now=datetime(2026, 9, 21, 9, tzinfo=timezone.utc)
    )
    assert stale.status == "stale"


def test_price_watch_rejects_mixed_or_future_observations() -> None:
    watch = PriceWatch(
        watch_id="hotel-paris", subject="hotel", currency="EUR", target_price="400"
    )
    wrong = PriceObservation(
        watch_id="other",
        amount="450",
        currency="EUR",
        observed_at="2026-09-19T10:00:00Z",
        source_id="hotel-source",
    )
    with pytest.raises(ValueError, match="must match"):
        assess_price_watch(
            watch, [wrong], now=datetime(2026, 9, 19, 11, tzinfo=timezone.utc)
        )
