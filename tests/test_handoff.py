import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ultimate_travel_agent.contracts import CompactHandoffV2, validate_compact_handoff


def _valid_handoff() -> dict[str, object]:
    return {
        "schema": "compact-handoff/v2",
        "run_id": "run-20260921",
        "stage": "flight-search",
        "status": "complete",
        "artifacts": ["research/flight-search/agent-1.jsonl"],
        "new_ids": ["flight.ref"],
        "changed_ids": [],
        "decision_ids": ["flight.choice"],
        "blockers": [],
        "coverage": {
            "expected": 4,
            "searched": 3,
            "unavailable": 1,
            "skipped": 0,
            "pending": 0,
        },
        "gates": {
            "coverage_complete": True,
            "evidence_sufficient": True,
            "recommendation_ready": True,
            "booking_ready": False,
        },
    }


def test_compact_handoff_v2_accepts_consistent_gates_and_coverage() -> None:
    handoff = CompactHandoffV2.model_validate(_valid_handoff())
    assert handoff.coverage.expected == 4
    assert handoff.gates.recommendation_ready


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda value: value["coverage"].update(expected=5), "coverage expected"),
        (lambda value: value["coverage"].update(pending=1, searched=2), "coverage_complete"),
        (
            lambda value: value["gates"].update(
                evidence_sufficient=False, recommendation_ready=True
            ),
            "recommendation_ready",
        ),
        (lambda value: value.update(status="blocked"), "blocked status"),
        (lambda value: value["new_ids"].append("flight.ref"), "unique"),
    ],
)
def test_compact_handoff_v2_rejects_inconsistent_state(mutate, message: str) -> None:
    value = _valid_handoff()
    mutate(value)
    with pytest.raises(ValidationError, match=message):
        CompactHandoffV2.model_validate(value)


def test_compact_handoff_validator_returns_actionable_issues() -> None:
    value = _valid_handoff()
    value["gates"]["booking_ready"] = True
    value["blockers"] = ["fare is stale"]

    passed, issues, handoff = validate_compact_handoff(value)

    assert not passed
    assert handoff is None
    assert any("booking_ready" in issue for issue in issues)


def test_compact_handoff_json_schema_is_packaged_and_current() -> None:
    root = Path(__file__).resolve().parents[1]
    schema_path = root / "src" / "ultimate_travel_agent" / "schemas" / "compact_handoff_v2.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["$id"].endswith("compact-handoff-v2.schema.json")
    assert schema["properties"]["schema"]["const"] == "compact-handoff/v2"
