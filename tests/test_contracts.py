"""Regression tests for the TravelDossier v1 compatibility contract."""

from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from ultimate_travel_agent.contracts import (
    Money,
    SourceEvidence,
    upgrade_legacy_dossier,
    validate_travel_dossier,
)


def _booking_ready_dossier() -> dict:
    return {
        "schema_version": "travel-dossier/v1",
        "mode": "booking_ready",
        "status": "complete",
        "summary": "Verified direct train option.",
        "claims": [
            {
                "claim_id": "train-fare",
                "text": "The operator displayed a EUR 39 fare.",
                "status": "official_verified",
                "source_ids": ["operator"],
                "critical": True,
                "observed_at": "2026-09-19",
                "expires_at": "2026-09-20",
            }
        ],
        "sources": [
            {
                "source_id": "operator",
                "name": "Direct operator",
                "url": "https://operator.example/booking",
                "source_type": "direct_operator",
                "authority": "primary",
                "retrieved_at": "2026-09-19",
                "expires_at": "2026-09-20",
            }
        ],
        "costs": [{"amount": "39.00", "currency": "EUR", "quantity": "2"}],
        "readiness": {"booking_ready": True, "blockers": []},
    }


def test_booking_ready_dossier_passes_with_fresh_primary_evidence():
    passed, issues, dossier = validate_travel_dossier(
        _booking_ready_dossier(), today=date(2026, 9, 19)
    )
    assert passed, issues
    assert dossier is not None
    assert str(dossier.costs[0].total) == "78.00"


def test_booking_ready_dossier_rejects_expired_critical_evidence():
    passed, issues, _ = validate_travel_dossier(_booking_ready_dossier(), today=date(2026, 9, 21))
    assert not passed
    assert any("expired" in issue for issue in issues)


def test_booking_ready_dossier_rejects_unresolved_work():
    data = _booking_ready_dossier()
    data["verification_required"] = ["Recheck fare"]
    passed, issues, _ = validate_travel_dossier(data, today=date(2026, 9, 19))
    assert not passed
    assert any("requires verification" in issue for issue in issues)


def test_booking_ready_critical_claim_requires_primary_authority():
    data = _booking_ready_dossier()
    data["sources"][0]["authority"] = "secondary"
    passed, issues, _ = validate_travel_dossier(data, today=date(2026, 9, 19))
    assert not passed
    assert any("primary evidence" in issue for issue in issues)


def test_cross_checked_claim_requires_two_independent_origins():
    data = _booking_ready_dossier()
    data["claims"][0]["status"] = "cross_checked"
    data["claims"][0]["source_ids"] = ["operator", "mirror"]
    data["sources"][0]["independence_group"] = "inventory-feed"
    data["sources"].append(
        {
            **data["sources"][0],
            "source_id": "mirror",
            "name": "Inventory mirror",
            "url": "https://mirror.example/booking",
        }
    )

    passed, issues, _ = validate_travel_dossier(data, today=date(2026, 9, 19))
    assert not passed
    assert any("independent" in issue for issue in issues)

    data["sources"][1]["independence_group"] = "second-origin"
    passed, issues, _ = validate_travel_dossier(data, today=date(2026, 9, 19))
    assert passed, issues


def test_source_evidence_preserves_canonical_and_original_urls():
    source = SourceEvidence.model_validate(
        {
            "source_id": "operator",
            "name": "Direct operator",
            "url": "https://operator.example/booking?utm_source=search",
            "canonical_url": "https://operator.example/booking",
            "source_type": "direct_operator",
            "authority": "primary",
            "independence_group": "operator",
            "retrieved_at": "2026-09-19",
        }
    )
    assert str(source.canonical_url) == "https://operator.example/booking"
    assert source.independence_group == "operator"


def test_source_evidence_derives_canonical_url_when_missing():
    source = SourceEvidence.model_validate(
        {
            "source_id": "operator",
            "name": "Direct operator",
            "url": "https://operator.example/booking?utm_source=search&date=2026-10-03",
            "source_type": "direct_operator",
            "authority": "primary",
            "retrieved_at": "2026-09-19",
        }
    )
    assert str(source.url).endswith("utm_source=search&date=2026-10-03")
    assert str(source.canonical_url) == "https://operator.example/booking?date=2026-10-03"


def test_legacy_dossier_is_upgraded_without_losing_fields():
    legacy = {
        "summary": "Draft trip",
        "custom_extension": {"keep": True},
        "source_log": [
            {
                "name": "Tourism board",
                "url": "https://tourism.example/info",
                "tier": 3,
                "verification_date": "2026-09-18",
            }
        ],
    }
    upgraded = upgrade_legacy_dossier(legacy, today=date(2026, 9, 19))
    passed, issues, dossier = validate_travel_dossier(upgraded, today=date(2026, 9, 19))
    assert passed, issues
    assert dossier is not None
    assert dossier.model_extra["custom_extension"] == {"keep": True}
    assert dossier.sources[0].source_type == "tourism_institution"
    assert dossier.readiness.booking_ready is False


def test_money_rejects_binary_float_and_incorrect_total():
    with pytest.raises(ValidationError):
        Money(amount=19.99, currency="EUR")
    with pytest.raises(ValidationError):
        Money(amount="19.99", quantity="2", total="50.00", currency="EUR")


def test_documented_example_is_a_valid_inspiration_dossier():
    example_path = (
        Path(__file__).resolve().parent.parent / "examples" / "travel-dossier-v1.example.yaml"
    )
    data = yaml.safe_load(example_path.read_text(encoding="utf-8"))
    passed, issues, dossier = validate_travel_dossier(data, today=date(2026, 9, 19))
    assert passed, issues
    assert dossier is not None
    assert dossier.mode == "inspiration"
    assert dossier.readiness.booking_ready is False
