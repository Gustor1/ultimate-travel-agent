from pathlib import Path

import yaml


def test_edge_case_catalog_covers_critical_travel_failures() -> None:
    path = Path("examples/scenarios/edge-case-regression-catalog.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    scenarios = data["scenarios"]
    identifiers = [scenario["scenario_id"] for scenario in scenarios]
    assert len(scenarios) >= 8
    assert len(identifiers) == len(set(identifiers))
    covered = {
        control
        for scenario in scenarios
        for control in scenario["required_controls"]
    }
    assert covered >= {
        "flexible_airports",
        "hotel_mobility",
        "step_free",
        "group_veto",
        "self_transfer",
        "true_cost",
        "price_alert",
        "controlled_booking",
        "adaptive_day",
        "route_windows",
        "disruption_cascade",
        "offline_mode",
    }
    assert all(scenario["expected_risk"] for scenario in scenarios)
