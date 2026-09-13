"""Validation tests for the reference trip examples."""

import json
from pathlib import Path
import pytest
from ultimate_travel_agent.models import Trip


@pytest.mark.parametrize(
    "json_path",
    [
        Path("examples/city-trip/trip.json"),
        Path("examples/road-trip/trip.json"),
        Path("data/examples/city-trip.json"),
        Path("data/examples/road-trip.json"),
    ],
)
def test_example_trips_are_valid(json_path: Path) -> None:
    """Validate that every reference example matches the Pydantic schema cleanly."""
    assert json_path.exists(), f"Example file does not exist: {json_path}"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    trip = Trip.model_validate(data)
    assert trip.id is not None
    assert len(trip.travelers) >= 1
    assert len(trip.destinations) >= 1
    assert len(trip.transports) >= 1
    assert len(trip.accommodations) >= 1
    assert len(trip.activities) >= 1
    assert len(trip.itinerary) >= 1
    assert len(trip.checklists) >= 1
    assert len(trip.stages) >= 1
    assert len(trip.reservations) >= 1

    # Check that coherence validation returns zero errors
    issues = trip.validate_trip_coherence()
    assert issues == [], f"Validation issues found in {json_path}: {issues}"

    # Verify budget calculation
    budget = trip.calculate_budget()
    assert budget.grand_total > 0
    assert budget.safety_buffer_amount > 0


def test_official_json_schema_validation() -> None:
    """Validate that reference trip examples strictly conform to data/schemas/trip.schema.json."""
    import jsonschema

    schema_path = Path("data/schemas/trip.schema.json")
    assert schema_path.exists()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    for ex_path in [
        Path("examples/city-trip/trip.json"),
        Path("examples/road-trip/trip.json"),
        Path("data/examples/city-trip.json"),
        Path("data/examples/road-trip.json"),
    ]:
        with open(ex_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Raises jsonschema.ValidationError on schema mismatch
        jsonschema.validate(instance=data, schema=schema)
