"""Tests for inter-city route options and recommendation engine."""

from ultimate_travel_agent.engine.route_optimizer import (
    evaluate_all_preferences,
    recommend_route_option,
)
from ultimate_travel_agent.models import (
    InterCityRoute,
    RouteOption,
    RouteOptionStatus,
    RoutePreference,
    RouteTransportMode,
    VerificationLevel,
)


def _build_sample_route() -> InterCityRoute:
    """Build a multi-modal route between Lyon and Marseille."""
    opt_train = RouteOption(
        id="opt-train",
        origin="Lyon Part-Dieu",
        destination="Marseille Saint-Charles",
        mode=RouteTransportMode.TRAIN,
        carrier="TGV INOUI",
        estimated_duration_minutes=100,
        transfers_count=0,
        estimated_cost=45.0,
        currency="EUR",
        comfort_level=4,
        carbon_footprint_kg=6.5,
        booking_required=True,
        confidence_level=VerificationLevel.OFFICIAL_VERIFIED,
        status=RouteOptionStatus.CONFIRMED,
    )
    opt_bus = RouteOption(
        id="opt-bus",
        origin="Lyon Perrache",
        destination="Marseille Saint-Charles",
        mode=RouteTransportMode.BUS,
        carrier="FlixBus",
        estimated_duration_minutes=240,
        transfers_count=0,
        estimated_cost=18.0,
        currency="EUR",
        comfort_level=2,
        carbon_footprint_kg=14.0,
        booking_required=True,
        confidence_level=VerificationLevel.CROSS_CHECKED,
        status=RouteOptionStatus.ESTIMATED,
    )
    opt_car = RouteOption(
        id="opt-car",
        origin="Lyon",
        destination="Marseille",
        mode=RouteTransportMode.CAR,
        estimated_duration_minutes=190,
        transfers_count=0,
        estimated_cost=65.0,  # Péage + essence
        currency="EUR",
        comfort_level=3,
        carbon_footprint_kg=55.0,
        booking_required=False,
        confidence_level=VerificationLevel.CROSS_CHECKED,
        status=RouteOptionStatus.ESTIMATED,
    )
    opt_flight = RouteOption(
        id="opt-flight",
        origin="Lyon Saint-Exupéry",
        destination="Marseille Provence",
        mode=RouteTransportMode.FLIGHT,
        carrier="Air France",
        estimated_duration_minutes=160,  # Porte-à-porte
        transfers_count=1,
        estimated_cost=120.0,
        currency="EUR",
        comfort_level=4,
        carbon_footprint_kg=110.0,
        booking_required=True,
        confidence_level=VerificationLevel.CROSS_CHECKED,
        status=RouteOptionStatus.ESTIMATED,
    )

    return InterCityRoute(
        id="route-lyon-marseille",
        origin="Lyon",
        destination="Marseille",
        options=[opt_train, opt_bus, opt_car, opt_flight],
    )


def test_route_recommendation_cheapest() -> None:
    """Verify cheapest recommendation picks the lowest financial cost."""
    route = _build_sample_route()
    chosen, reason = recommend_route_option(route, RoutePreference.CHEAPEST)
    assert chosen is not None
    assert chosen.id == "opt-bus"
    assert chosen.estimated_cost == 18.0
    assert "Cheapest option" in reason


def test_route_recommendation_fastest() -> None:
    """Verify fastest recommendation picks the minimal transit duration."""
    route = _build_sample_route()
    chosen, reason = recommend_route_option(route, RoutePreference.FASTEST)
    assert chosen is not None
    assert chosen.id == "opt-train"
    assert chosen.estimated_duration_minutes == 100
    assert "Fastest" in reason


def test_route_recommendation_fewest_transfers() -> None:
    """Verify fewest transfers preference."""
    route = _build_sample_route()
    chosen, reason = recommend_route_option(route, RoutePreference.FEWEST_TRANSFERS)
    assert chosen is not None
    assert chosen.transfers_count == 0


def test_route_recommendation_most_comfortable() -> None:
    """Verify most comfortable preference selects highest comfort score."""
    route = _build_sample_route()
    chosen, reason = recommend_route_option(route, RoutePreference.MOST_COMFORTABLE)
    assert chosen is not None
    assert chosen.comfort_level >= 4


def test_route_recommendation_most_eco_friendly() -> None:
    """Verify most eco-friendly recommendation picks the minimal carbon footprint."""
    route = _build_sample_route()
    chosen, reason = recommend_route_option(route, RoutePreference.MOST_ECO_FRIENDLY)
    assert chosen is not None
    assert chosen.id == "opt-train"
    assert chosen.carbon_footprint_kg == 6.5
    assert "Lowest environmental footprint" in reason


def test_route_recommendation_relaxed() -> None:
    """Verify relaxed preference favors high comfort, low transfers."""
    route = _build_sample_route()
    chosen, reason = recommend_route_option(route, RoutePreference.RELAXED)
    assert chosen is not None
    assert chosen.transfers_count <= 1
    assert chosen.comfort_level >= 3
    assert "relaxed" in reason.lower()


def test_route_recommendation_packed() -> None:
    """Verify packed preference favors fastest transit."""
    route = _build_sample_route()
    chosen, reason = recommend_route_option(route, RoutePreference.PACKED)
    assert chosen is not None
    assert chosen.estimated_duration_minutes == 100


def test_evaluate_all_preferences() -> None:
    """Verify evaluate_all_preferences returns evaluation dictionary for all 7 profiles."""
    route = _build_sample_route()
    evals = evaluate_all_preferences(route)
    expected_keys = {
        "cheapest",
        "fastest",
        "fewest_transfers",
        "most_comfortable",
        "most_eco_friendly",
        "relaxed",
        "packed",
    }
    assert expected_keys.issubset(evals.keys())
    assert evals["cheapest"]["option_id"] == "opt-bus"
    assert evals["fastest"]["option_id"] == "opt-train"
    assert evals["most_eco_friendly"]["option_id"] == "opt-train"


def test_route_empty_options() -> None:
    """Verify handling when an InterCityRoute has zero options."""
    empty_route = InterCityRoute(id="r-empty", origin="A", destination="B", options=[])
    chosen, reason = recommend_route_option(empty_route, RoutePreference.CHEAPEST)
    assert chosen is None
    assert "No route options" in reason
