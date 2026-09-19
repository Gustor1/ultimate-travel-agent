from decimal import Decimal

import pytest
from pydantic import ValidationError

from ultimate_travel_agent.true_cost import (
    CostComponent,
    DoorToDoorOption,
    compare_door_to_door_costs,
)


def _component(component_id: str, category: str, amount: str) -> CostComponent:
    return CostComponent.model_validate(
        {
            "component_id": component_id,
            "category": category,
            "description": component_id.replace("-", " "),
            "unit_amount": amount,
            "verified": True,
            "source_id": f"source-{component_id}",
        }
    )


def _option(
    option_id: str,
    airfare: str,
    transfer: str,
    minutes: int,
    *,
    separate: bool = False,
) -> DoorToDoorOption:
    return DoorToDoorOption(
        option_id=option_id,
        label=option_id,
        currency="EUR",
        door_to_door_minutes=minutes,
        components=[
            _component(f"{option_id}-fare", "airfare", airfare),
            _component(f"{option_id}-bag", "baggage", "30"),
            _component(f"{option_id}-transfer", "airport_transfer", transfer),
        ],
        separate_tickets=separate,
        self_transfer=separate,
    )


def test_true_cost_can_reverse_the_displayed_fare_winner() -> None:
    cheap_far = _option("cheap-far", "100", "70", 600)
    direct = _option("direct", "135", "15", 300)
    result = compare_door_to_door_costs(
        [cheap_far, direct],
        required_categories=["airfare", "baggage", "airport_transfer"],
        value_of_time_per_hour=Decimal("12"),
    )
    assert result.preferred_option_id == "direct"
    assert result.results[0].true_cost == Decimal("240.00")
    assert result.results[1].true_cost == Decimal("320.00")


def test_separate_ticket_adds_explicit_risk_reserve() -> None:
    option = _option("self", "100", "20", 300, separate=True)
    result = compare_door_to_door_costs(
        [option],
        required_categories=["airfare", "baggage", "airport_transfer"],
    )
    assert result.results[0].direct_cost == Decimal("150.00")
    assert result.results[0].risk_reserve == Decimal("15.00")
    assert result.results[0].true_cost == Decimal("165.00")


def test_incomplete_cheaper_option_cannot_win() -> None:
    incomplete = _option("incomplete", "50", "10", 200)
    incomplete.components = [
        component
        for component in incomplete.components
        if component.category != "airport_transfer"
    ]
    complete = _option("complete", "100", "20", 300)
    result = compare_door_to_door_costs(
        [incomplete, complete],
        required_categories=["airfare", "baggage", "airport_transfer"],
    )
    assert result.preferred_option_id == "complete"
    assert not result.results[1].complete
    assert result.results[1].missing_categories == ["airport_transfer"]


def test_verified_component_requires_evidence_and_floats_are_rejected() -> None:
    with pytest.raises(ValidationError, match="source_id"):
        CostComponent(
            component_id="fare",
            category="airfare",
            description="Fare",
            unit_amount="100",
            verified=True,
        )
    with pytest.raises(ValidationError, match="decimal strings"):
        CostComponent(
            component_id="fare",
            category="airfare",
            description="Fare",
            unit_amount=100.1,
        )


def test_cross_currency_comparison_is_rejected() -> None:
    euro = _option("euro", "100", "20", 300)
    dollar = _option("dollar", "100", "20", 300).model_copy(
        update={"currency": "USD"}
    )
    with pytest.raises(ValueError, match="same comparison currency"):
        compare_door_to_door_costs(
            [euro, dollar],
            required_categories=["airfare", "baggage", "airport_transfer"],
        )
