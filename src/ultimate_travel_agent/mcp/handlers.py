"""Validated, direct Python dispatch for MCP tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel

from ultimate_travel_agent.mcp.schemas import get_input_model, get_output_model


class ToolDispatcher:
    """Invoke registered operations without shelling out or exposing arbitrary paths."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def resolve_path(self, value: str) -> Path:
        candidate = (self.root / value).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("path is outside the configured MCP root") from exc
        return candidate

    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        request = get_input_model(name).model_validate(arguments)
        result = self._dispatch(name, request)
        return get_output_model(name).model_validate(result).model_dump(mode="json")

    def _dispatch(self, name: str, request: BaseModel) -> object:
        data = dict(request)
        if name == "install-skills":
            from ultimate_travel_agent.skills import install_pack_skills

            result = install_pack_skills(
                self.resolve_path(data["target"]),
                include_agents=data["include_agents"],
                include_workflows=data["include_workflows"],
                force=data["force"],
                dry_run=data["dry_run"],
            )
            return _normalize_paths(result)
        if name == "uninstall-skills":
            from ultimate_travel_agent.skills import uninstall_pack_skills

            return uninstall_pack_skills(
                self.resolve_path(data["target"]),
                force=data["force"],
                clean_modified=data["clean_modified"],
                dry_run=data["dry_run"],
            )
        if name == "list-skills":
            from ultimate_travel_agent.skills import list_available_skills

            return {"skills": list_available_skills()}
        if name == "validate-skills":
            from ultimate_travel_agent.validator import validate_all_skills

            skill_path = self.resolve_path(data["path"]) if data["path"] else None
            passed, reports = validate_all_skills(skill_path)
            return {"passed": passed, "reports": reports}
        if name == "validate-dossier":
            from ultimate_travel_agent.contracts import validate_travel_dossier

            passed, issues, dossier = validate_travel_dossier(data["dossier"])
            return {
                "passed": passed,
                "issues": issues,
                "normalized": dossier.model_dump(mode="json") if dossier else None,
            }
        if name == "validate-handoff":
            from ultimate_travel_agent.contracts import validate_compact_handoff

            passed, issues, handoff = validate_compact_handoff(data["handoff"])
            return {
                "passed": passed,
                "issues": issues,
                "normalized": handoff.model_dump(mode="json") if handoff else None,
            }
        if name == "prompt-audit":
            from ultimate_travel_agent.prompt_audit import audit_prompt_corpus
            from ultimate_travel_agent.skills import find_pack_root

            root = self.resolve_path(data["path"]) if data["path"] else find_pack_root()
            return audit_prompt_corpus(root)
        if name == "normalize-source-url":
            from ultimate_travel_agent.evidence import canonicalize_source_url

            return {"url": canonicalize_source_url(str(data["url"]))}
        if name == "profile-save":
            from ultimate_travel_agent.profiles import save_profile

            path = save_profile(data["profile"], self.resolve_path(data["output_path"]))
            return {"profile": data["profile"], "path": str(path)}
        if name == "profile-show":
            from ultimate_travel_agent.profiles import load_profile

            path = self.resolve_path(data["path"])
            return {"profile": load_profile(path), "path": str(path)}
        if name == "export-dossier":
            from ultimate_travel_agent.contracts import validate_travel_dossier
            from ultimate_travel_agent.exports import serialize_export

            passed, issues, dossier = validate_travel_dossier(data["dossier"])
            if dossier is None or not passed:
                raise ValueError(f"invalid dossier: {'; '.join(issues)}")
            output = self.resolve_path(data["output_path"])
            output.parent.mkdir(parents=True, exist_ok=True)
            payload = serialize_export(dossier, data["format"])
            output.write_bytes(payload)
            return {"path": str(output), "format": data["format"], "bytes_written": len(payload)}
        if name == "revalidation-plan":
            from ultimate_travel_agent.contracts import validate_travel_dossier
            from ultimate_travel_agent.monitoring import build_revalidation_plan

            passed, issues, dossier = validate_travel_dossier(data["dossier"])
            if dossier is None or not passed:
                raise ValueError(f"invalid dossier: {'; '.join(issues)}")
            return {"tasks": build_revalidation_plan(dossier, data["departure"])}
        if name == "price-watch":
            from ultimate_travel_agent.monitoring import assess_price_watch, schedule_price_watch

            if data["policy"] is not None or data["state"] is not None:
                if data["policy"] is None or data["state"] is None:
                    raise ValueError("policy and state must be supplied together")
                decision = schedule_price_watch(
                    data["watch"], data["observations"], data["policy"], data["state"]
                )
                return {"mode": "scheduled", "decision": decision}
            return {
                "mode": "assessment",
                "assessment": assess_price_watch(data["watch"], data["observations"]),
            }
        if name == "flight-search-plan":
            from ultimate_travel_agent.flight_flex import generate_flight_search_plan

            flight_plan = generate_flight_search_plan(data["request"])
            if data["output_path"]:
                output = self.resolve_path(data["output_path"])
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(flight_plan.model_dump_json(indent=2), encoding="utf-8")
            return flight_plan
        if name == "flight-search-coverage":
            from ultimate_travel_agent.flight_flex import assess_search_coverage

            return assess_search_coverage(
                data["plan"], require_booking_evidence=data["booking_ready"]
            )
        if name == "hotel-search-plan":
            from ultimate_travel_agent.hotel_search import generate_hotel_research_plan

            hotel_plan = generate_hotel_research_plan(data["request"])
            if data["output_path"]:
                output = self.resolve_path(data["output_path"])
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(hotel_plan.model_dump_json(indent=2), encoding="utf-8")
            return hotel_plan
        if name == "hotel-search-coverage":
            from ultimate_travel_agent.hotel_search import assess_hotel_research_coverage

            return assess_hotel_research_coverage(data["plan"])
        if name == "hotel-compare":
            from ultimate_travel_agent.hotel_search import compare_hotel_property

            return compare_hotel_property(data["property"], data["request"], data["room_key"])
        if name == "hotel-mobility":
            from ultimate_travel_agent.hotel_search import assess_hotel_mobility

            return assess_hotel_mobility(
                data["anchors"],
                data["journeys"],
                maximum_walking_minutes=data["maximum_walking_minutes"],
                step_free_required=data["step_free_required"],
            )
        if name == "compare-total-cost":
            from ultimate_travel_agent.true_cost import compare_door_to_door_costs

            return compare_door_to_door_costs(
                data["options"],
                required_categories=data["required_categories"],
                value_of_time_per_hour=data["value_of_time_per_hour"],
                separate_ticket_reserve_percent=data["separate_ticket_reserve_percent"],
            )
        if name == "disruption-plan":
            from ultimate_travel_agent.disruptions import (
                build_cascading_recovery_plan,
                build_recovery_plan,
            )

            function = build_cascading_recovery_plan if data["cascade"] else build_recovery_plan
            return function(data["itinerary"], data["disruption"], data["options"])
        if name in {"connector-fetch", "connector-read"}:
            from ultimate_travel_agent.connectors import (
                execute_json_connector,
                normalize_connector_result,
            )

            connector_result = execute_json_connector(data["config"], data["request"])
            if data["normalization"] is not None:
                return {
                    "normalized": True,
                    "result": normalize_connector_result(
                        connector_result, data["normalization"]
                    ),
                }
            return {"normalized": False, "result": connector_result}
        if name == "adaptive-day":
            from ultimate_travel_agent.adaptive import build_adaptive_day

            return build_adaptive_day(data["request"], data["activities"])
        if name == "route-optimize":
            from ultimate_travel_agent.route_optimizer import optimize_route_with_windows

            return optimize_route_with_windows(
                data["origin_id"],
                data["day_start"],
                data["day_end"],
                data["visits"],
                data["travel_times"],
                data["destination_id"],
            )
        if name == "group-decide":
            from ultimate_travel_agent.group_planning import rank_group_options

            return rank_group_options(data["options"], data["ballots"])
        if name == "neighborhood-score":
            from ultimate_travel_agent.neighborhood import assess_neighborhood

            return assess_neighborhood(
                data["profile"], data["requirements"], as_of=data["as_of"]
            )
        if name == "booking-handoff":
            from ultimate_travel_agent.booking import (
                confirm_booking_handoff,
                prepare_booking_handoff,
            )

            if data["confirmation"] is not None:
                return confirm_booking_handoff(
                    data["intent"], data["confirmation"], now=data["now"]
                )
            return prepare_booking_handoff(data["intent"], now=data["now"])
        if name == "trip-mode":
            from ultimate_travel_agent.trip_mode import TripModeRequest, build_trip_companion

            return build_trip_companion(cast(TripModeRequest, request))
        if name == "notify-webhook":
            from ultimate_travel_agent.notifications import dispatch_webhook_notification

            return dispatch_webhook_notification(data["config"], data["message"])
        raise KeyError(f"unknown MCP tool: {name}")


def _normalize_paths(result: dict[str, object]) -> dict[str, object]:
    return {
        key: str(value) if isinstance(value, Path) else value
        for key, value in result.items()
    }


__all__ = ["ToolDispatcher"]
