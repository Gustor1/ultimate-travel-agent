"""CLI entry point for ultimate-travel-agent Skills-First pack."""

import argparse
import json
import sys
from pathlib import Path

import yaml

from ultimate_travel_agent.skills import (
    find_pack_root,
    install_pack_skills,
    list_available_skills,
    uninstall_pack_skills,
)


def _load_mapping(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw) if path.suffix.lower() == ".json" else yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level object")
    return data


def install_skills_cmd(args: argparse.Namespace) -> None:
    target = Path(args.target).resolve()
    print(f"Installing Ultimate Travel Agent pack into: {target}")
    result = install_pack_skills(
        target_dir=target,
        include_agents=getattr(args, "include_agents", False),
        include_workflows=getattr(args, "include_workflows", False),
        force=getattr(args, "force", False),
        dry_run=getattr(args, "dry_run", False),
    )

    prefix = "[DRY-RUN] " if getattr(args, "dry_run", False) else ""
    if result["installed"]:
        print(f"\n{prefix}Installed files ({len(result['installed'])}):")
        for f in result["installed"][:15]:
            print(f"   + {f}")
        if len(result["installed"]) > 15:
            print(f"   ... and {len(result['installed']) - 15} more files.")

    if result["overwritten"]:
        print(f"\n{prefix}Overwritten files (--force, {len(result['overwritten'])}):")
        for f in result["overwritten"][:10]:
            print(f"   ~ {f}")

    if result["skipped"]:
        print(
            f"\n{prefix}Skipped existing files ({len(result['skipped'])} - use --force to overwrite):"
        )
        for f in result["skipped"][:10]:
            print(f"   - {f}")

    print(
        f"\nSummary: {len(result['installed'])} files installed. Target skills: {result['skills_count']}, agents: {result['agents_count']}, workflows: {result['workflows_count']}."
    )
    if result.get("manifest_path"):
        print(f"Manifest written to: {result['manifest_path']}")


def uninstall_skills_cmd(args: argparse.Namespace) -> None:
    target = Path(args.target).resolve()
    print(f"Uninstalling Ultimate Travel Agent pack from: {target}")
    result = uninstall_pack_skills(
        target_dir=target,
        force=getattr(args, "force", False),
        clean_modified=getattr(args, "clean_modified", False),
        dry_run=getattr(args, "dry_run", False),
    )

    prefix = "[DRY-RUN] " if getattr(args, "dry_run", False) else ""
    if result["removed"]:
        print(f"\n{prefix}Removed files ({len(result['removed'])}):")
        for f in result["removed"][:15]:
            print(f"   - {f}")
        if len(result["removed"]) > 15:
            print(f"   ... and {len(result['removed']) - 15} more files.")

    if result.get("restored"):
        print(f"\nRestored pre-existing files ({len(result['restored'])}):")
        for f in result["restored"]:
            print(f"   = {f}")

    if result["skipped_modified"]:
        print(f"\n[WARNING] Skipped user-modified files ({len(result['skipped_modified'])}):")
        for f in result["skipped_modified"]:
            print(f"   ! {f} (modified after install; use --clean-modified or --force to delete)")

    if result["not_found"]:
        print(f"\nAlready removed or missing ({len(result['not_found'])} files).")

    if result.get("errors"):
        print("\n[ERROR] Uninstallation did not remove untracked or unsafe files:")
        for error in result["errors"]:
            print(f"   ! {error}")

    status = (
        "Manifest cleaned."
        if result.get("manifest_cleaned")
        else "Manifest updated with remaining files."
    )
    print(f"\nSummary: {len(result['removed'])} files removed. {status}")


def list_skills_cmd(args: argparse.Namespace) -> None:
    skills = list_available_skills()
    print(f"Available Travel Skills ({len(skills)}):")
    for s in skills:
        desc = s.get("description", "")
        print(f"  - {s['name']}: {desc}")


def validate_skills_cmd(args: argparse.Namespace) -> None:
    from ultimate_travel_agent.validator import validate_all_skills

    pack_dir = Path(args.path).resolve() if getattr(args, "path", None) else None
    passed, reports = validate_all_skills(pack_dir)
    print(f"Skill Quality Validation: {'PASSED' if passed else 'FAILED'}")
    for skill_name, issues in reports.items():
        if issues:
            print(f"  [FAIL] {skill_name}:")
            for issue in issues:
                print(f"     - {issue}")
        else:
            print(f"  [OK]   {skill_name}")
    if not passed:
        sys.exit(1)


def validate_dossier_cmd(args: argparse.Namespace) -> None:
    """Validate JSON or YAML against the TravelDossier v1 contract."""
    from ultimate_travel_agent.contracts import validate_travel_dossier

    dossier_path = Path(args.path).resolve()
    data = _load_mapping(dossier_path)
    passed, issues, dossier = validate_travel_dossier(data)
    print(f"TravelDossier v1: {'PASSED' if passed else 'FAILED'}")
    if dossier is not None:
        print(
            f"Mode: {dossier.mode}; claims: {len(dossier.claims)}; "
            f"sources: {len(dossier.sources)}; booking-ready: {dossier.readiness.booking_ready}"
        )
    for issue in issues:
        print(f"  - {issue}")
    if not passed:
        raise SystemExit(1)


def validate_handoff_cmd(args: argparse.Namespace) -> None:
    """Validate JSON or YAML against the compact-handoff/v2 contract."""
    from ultimate_travel_agent.contracts import validate_compact_handoff

    data = _load_mapping(Path(args.path).resolve())
    passed, issues, handoff = validate_compact_handoff(data)
    print(f"compact-handoff/v2: {'PASSED' if passed else 'FAILED'}")
    if handoff is not None:
        print(
            f"Stage: {handoff.stage}; status: {handoff.status}; "
            f"pending: {handoff.coverage.pending}; blockers: {len(handoff.blockers)}"
        )
    for issue in issues:
        print(f"  - {issue}")
    if not passed:
        raise SystemExit(1)


def prompt_audit_cmd(args: argparse.Namespace) -> None:
    """Report stable prompt corpus sizes without claiming provider billing usage."""
    from ultimate_travel_agent.prompt_audit import audit_prompt_corpus
    from ultimate_travel_agent.skills import find_pack_root

    root = Path(args.path).resolve() if args.path else find_pack_root()
    report = audit_prompt_corpus(root)
    print("Corpus      Files  Characters  Estimated tokens")
    for name in ("skills", "agents", "workflows", "shared"):
        values = report[name]
        print(
            f"{name:<11} {values['files']:>5}  {values['characters']:>10}  "
            f"{values['estimated_tokens']:>16}"
        )
    print("Estimated tokens use characters/4 and are not provider billing data.")


def normalize_source_url_cmd(args: argparse.Namespace) -> None:
    """Print a conservative source-deduplication URL."""
    from ultimate_travel_agent.evidence import canonicalize_source_url

    try:
        print(canonicalize_source_url(args.url))
    except ValueError as exc:
        print(f"Invalid source URL: {exc}")
        raise SystemExit(1) from exc


def profile_save_cmd(args: argparse.Namespace) -> None:
    """Validate and atomically persist a privacy-minimal traveler profile."""
    from ultimate_travel_agent.profiles import TravelerProfile, save_profile

    profile = TravelerProfile.model_validate(_load_mapping(Path(args.input).resolve()))
    path = save_profile(profile, Path(args.output))
    print(f"Traveler profile saved: {path}")


def profile_show_cmd(args: argparse.Namespace) -> None:
    """Print a validated profile as normalized JSON."""
    from ultimate_travel_agent.profiles import load_profile

    print(load_profile(Path(args.path).resolve()).model_dump_json(indent=2))


def export_dossier_cmd(args: argparse.Namespace) -> None:
    """Validate then export a dossier to a portable artifact."""
    from ultimate_travel_agent.contracts import validate_travel_dossier
    from ultimate_travel_agent.exports import serialize_export

    passed, issues, dossier = validate_travel_dossier(
        _load_mapping(Path(args.input).resolve())
    )
    if dossier is None or not passed:
        raise ValueError(f"invalid dossier: {'; '.join(issues)}")
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(serialize_export(dossier, args.format))
    print(f"Exported {args.format}: {output}")


def revalidation_plan_cmd(args: argparse.Namespace) -> None:
    """Generate a pre-departure revalidation schedule."""
    from datetime import date

    from ultimate_travel_agent.contracts import validate_travel_dossier
    from ultimate_travel_agent.monitoring import build_revalidation_plan

    passed, issues, dossier = validate_travel_dossier(
        _load_mapping(Path(args.input).resolve())
    )
    if dossier is None or not passed:
        raise ValueError(f"invalid dossier: {'; '.join(issues)}")
    tasks = build_revalidation_plan(dossier, date.fromisoformat(args.departure))
    print(json.dumps([task.model_dump(mode="json") for task in tasks], indent=2))


def flight_search_plan_cmd(args: argparse.Namespace) -> None:
    """Generate the exhaustive four-pass flight search matrix."""
    from ultimate_travel_agent.flight_flex import (
        FlightSearchRequest,
        generate_flight_search_plan,
    )

    request = FlightSearchRequest.model_validate(
        _load_mapping(Path(args.input).resolve())
    )
    plan = generate_flight_search_plan(request)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    counts = {
        number: sum(cell.pass_number == number for cell in plan.cells)
        for number in range(1, 5)
    }
    print(f"Flight search plan saved: {output}; cells by pass: {counts}")


def flight_search_coverage_cmd(args: argparse.Namespace) -> None:
    """Verify that every planned flight-search cell was attempted."""
    from ultimate_travel_agent.flight_flex import (
        FlightSearchPlan,
        assess_search_coverage,
    )

    plan = FlightSearchPlan.model_validate(_load_mapping(Path(args.input).resolve()))
    report = assess_search_coverage(
        plan, require_booking_evidence=args.booking_ready
    )
    print(report.model_dump_json(indent=2))
    if not report.complete or (args.booking_ready and not report.booking_ready):
        raise SystemExit(1)


def hotel_search_plan_cmd(args: argparse.Namespace) -> None:
    """Generate transit-first hotel comparison tasks."""
    from ultimate_travel_agent.hotel_search import (
        HotelSearchRequest,
        generate_hotel_research_plan,
    )

    request = HotelSearchRequest.model_validate(_load_mapping(Path(args.input).resolve()))
    plan = generate_hotel_research_plan(request)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    print(f"Hotel research plan saved: {output}; tasks: {len(plan.tasks)}")


def hotel_search_coverage_cmd(args: argparse.Namespace) -> None:
    """Verify hotel research source and direct-check coverage."""
    from ultimate_travel_agent.hotel_search import (
        HotelResearchPlan,
        assess_hotel_research_coverage,
    )

    plan = HotelResearchPlan.model_validate(_load_mapping(Path(args.input).resolve()))
    report = assess_hotel_research_coverage(plan)
    print(report.model_dump_json(indent=2))
    if not report.complete or (args.booking_ready and not report.booking_ready):
        raise SystemExit(1)


def hotel_compare_cmd(args: argparse.Namespace) -> None:
    """Compare normalized room quotes and transit access for one property."""
    from ultimate_travel_agent.hotel_search import (
        HotelProperty,
        HotelSearchRequest,
        compare_hotel_property,
    )

    data = _load_mapping(Path(args.input).resolve())
    request = HotelSearchRequest.model_validate(data.get("request"))
    hotel = HotelProperty.model_validate(data.get("property"))
    room_key = data.get("room_key")
    if not isinstance(room_key, str) or not room_key:
        raise ValueError("hotel comparison input requires room_key")
    print(compare_hotel_property(hotel, request, room_key).model_dump_json(indent=2))


def hotel_mobility_cmd(args: argparse.Namespace) -> None:
    """Score door-to-door transit from a hotel to important trip anchors."""
    from pydantic import TypeAdapter

    from ultimate_travel_agent.hotel_search import (
        MobilityAnchor,
        TransitJourney,
        assess_hotel_mobility,
    )

    data = _load_mapping(Path(args.input).resolve())
    anchors = TypeAdapter(list[MobilityAnchor]).validate_python(data.get("anchors"))
    journeys = TypeAdapter(list[TransitJourney]).validate_python(data.get("journeys"))
    result = assess_hotel_mobility(
        anchors,
        journeys,
        maximum_walking_minutes=args.maximum_walking_minutes,
        step_free_required=args.step_free_required,
    )
    print(result.model_dump_json(indent=2))
    if not result.complete:
        raise SystemExit(1)


def compare_total_cost_cmd(args: argparse.Namespace) -> None:
    """Compare complete travel options including time and transfer exposure."""
    from decimal import Decimal

    from pydantic import TypeAdapter

    from ultimate_travel_agent.true_cost import (
        CostCategory,
        DoorToDoorOption,
        compare_door_to_door_costs,
    )

    data = _load_mapping(Path(args.input).resolve())
    options = TypeAdapter(list[DoorToDoorOption]).validate_python(data.get("options"))
    categories = TypeAdapter(list[CostCategory]).validate_python(
        data.get("required_categories")
    )
    result = compare_door_to_door_costs(
        options,
        required_categories=categories,
        value_of_time_per_hour=Decimal(str(data.get("value_of_time_per_hour", "0"))),
        separate_ticket_reserve_percent=Decimal(
            str(data.get("separate_ticket_reserve_percent", "10"))
        ),
    )
    print(result.model_dump_json(indent=2))
    if result.preferred_option_id is None:
        raise SystemExit(1)


def price_watch_cmd(args: argparse.Namespace) -> None:
    """Assess a sourced flight or hotel price history."""
    from pydantic import TypeAdapter

    from ultimate_travel_agent.monitoring import (
        PriceAlertPolicy,
        PriceAlertState,
        PriceObservation,
        PriceWatch,
        assess_price_watch,
        schedule_price_watch,
    )

    data = _load_mapping(Path(args.input).resolve())
    watch = PriceWatch.model_validate(data.get("watch"))
    observations = TypeAdapter(list[PriceObservation]).validate_python(
        data.get("observations")
    )
    if "policy" in data or "state" in data:
        policy = PriceAlertPolicy.model_validate(data.get("policy", {}))
        state = PriceAlertState.model_validate(data.get("state", {}))
        print(schedule_price_watch(watch, observations, policy, state).model_dump_json(indent=2))
    else:
        print(assess_price_watch(watch, observations).model_dump_json(indent=2))


def disruption_plan_cmd(args: argparse.Namespace) -> None:
    """Build a recovery plan while preserving unaffected itinerary items."""
    from pydantic import TypeAdapter

    from ultimate_travel_agent.disruptions import (
        Disruption,
        ItineraryItem,
        RecoveryOption,
        build_cascading_recovery_plan,
        build_recovery_plan,
    )

    data = _load_mapping(Path(args.input).resolve())
    itinerary = TypeAdapter(list[ItineraryItem]).validate_python(data.get("itinerary"))
    disruption = Disruption.model_validate(data.get("disruption"))
    options = TypeAdapter(list[RecoveryOption]).validate_python(data.get("options"))
    result = (
        build_cascading_recovery_plan(itinerary, disruption, options)
        if args.cascade
        else build_recovery_plan(itinerary, disruption, options)
    )
    print(result.model_dump_json(indent=2))
    if not result.complete:
        raise SystemExit(1)


def connector_fetch_cmd(args: argparse.Namespace) -> None:
    """Execute one bounded live JSON connector request."""
    from ultimate_travel_agent.connectors import (
        ConnectorConfig,
        ConnectorNormalizationSpec,
        ConnectorRequest,
        execute_json_connector,
        normalize_connector_result,
    )

    data = _load_mapping(Path(args.input).resolve())
    config = ConnectorConfig.model_validate(data.get("config"))
    request = ConnectorRequest.model_validate(data.get("request"))
    result = execute_json_connector(config, request)
    if "normalization" in data:
        spec = ConnectorNormalizationSpec.model_validate(data.get("normalization"))
        print(normalize_connector_result(result, spec).model_dump_json(indent=2))
    else:
        print(result.model_dump_json(indent=2))


def adaptive_day_cmd(args: argparse.Namespace) -> None:
    """Build essential, balanced, rain, and low-energy day variants."""
    from pydantic import TypeAdapter

    from ultimate_travel_agent.adaptive import (
        ActivityCandidate,
        AdaptiveDayRequest,
        build_adaptive_day,
    )

    data = _load_mapping(Path(args.input).resolve())
    request = AdaptiveDayRequest.model_validate(data.get("request"))
    activities = TypeAdapter(list[ActivityCandidate]).validate_python(data.get("activities"))
    print(build_adaptive_day(request, activities).model_dump_json(indent=2))


def group_decide_cmd(args: argparse.Namespace) -> None:
    """Rank complete group ballots with hard vetoes."""
    from pydantic import TypeAdapter

    from ultimate_travel_agent.group_planning import (
        GroupOption,
        ParticipantBallot,
        rank_group_options,
    )

    data = _load_mapping(Path(args.input).resolve())
    options = TypeAdapter(list[GroupOption]).validate_python(data.get("options"))
    ballots = TypeAdapter(list[ParticipantBallot]).validate_python(data.get("ballots"))
    print(rank_group_options(options, ballots).model_dump_json(indent=2))


def neighborhood_score_cmd(args: argparse.Namespace) -> None:
    """Score evidence-backed neighborhood quality."""
    from datetime import date

    from ultimate_travel_agent.neighborhood import (
        NeighborhoodProfile,
        NeighborhoodRequirements,
        assess_neighborhood,
    )

    data = _load_mapping(Path(args.input).resolve())
    profile = NeighborhoodProfile.model_validate(data.get("profile"))
    requirements = NeighborhoodRequirements.model_validate(data.get("requirements", {}))
    as_of_raw = data.get("as_of")
    as_of = date.fromisoformat(as_of_raw) if isinstance(as_of_raw, str) else None
    print(assess_neighborhood(profile, requirements, as_of=as_of).model_dump_json(indent=2))


def booking_handoff_cmd(args: argparse.Namespace) -> None:
    """Prepare or explicitly confirm a user-controlled checkout handoff."""
    from datetime import datetime

    from ultimate_travel_agent.booking import (
        BookingConfirmation,
        BookingIntent,
        confirm_booking_handoff,
        prepare_booking_handoff,
    )

    data = _load_mapping(Path(args.input).resolve())
    intent = BookingIntent.model_validate(data.get("intent"))
    now_raw = data.get("now")
    if not isinstance(now_raw, str):
        raise ValueError("booking handoff input requires ISO datetime now")
    now = datetime.fromisoformat(now_raw.replace("Z", "+00:00"))
    if "confirmation" in data:
        confirmation = BookingConfirmation.model_validate(data.get("confirmation"))
        result = confirm_booking_handoff(intent, confirmation, now=now)
    else:
        result = prepare_booking_handoff(intent, now=now)
    print(result.model_dump_json(indent=2))
    if result.status == "blocked":
        raise SystemExit(1)


def trip_mode_cmd(args: argparse.Namespace) -> None:
    """Show current item, next action, and offline readiness."""
    from ultimate_travel_agent.trip_mode import TripModeRequest, build_trip_companion

    request = TripModeRequest.model_validate(_load_mapping(Path(args.input).resolve()))
    print(build_trip_companion(request).model_dump_json(indent=2))


def route_optimize_cmd(args: argparse.Namespace) -> None:
    """Optimize a day using sourced travel times and visit windows."""
    from datetime import datetime

    from pydantic import TypeAdapter

    from ultimate_travel_agent.route_optimizer import (
        RouteVisit,
        SourcedTravelTime,
        optimize_route_with_windows,
    )

    data = _load_mapping(Path(args.input).resolve())
    visits = TypeAdapter(list[RouteVisit]).validate_python(data.get("visits"))
    travel_times = TypeAdapter(list[SourcedTravelTime]).validate_python(
        data.get("travel_times")
    )
    origin_id = data.get("origin_id")
    day_start = data.get("day_start")
    day_end = data.get("day_end")
    if (
        not isinstance(origin_id, str)
        or not isinstance(day_start, str)
        or not isinstance(day_end, str)
    ):
        raise ValueError("route input requires origin_id, day_start, and day_end strings")
    destination_raw = data.get("destination_id")
    destination_id = destination_raw if isinstance(destination_raw, str) else None
    result = optimize_route_with_windows(
        origin_id,
        datetime.fromisoformat(day_start.replace("Z", "+00:00")),
        datetime.fromisoformat(day_end.replace("Z", "+00:00")),
        visits,
        travel_times,
        destination_id,
    )
    print(result.model_dump_json(indent=2))
    if not result.complete:
        raise SystemExit(1)


def notify_webhook_cmd(args: argparse.Namespace) -> None:
    """Deliver one explicitly configured signed webhook notification."""
    from ultimate_travel_agent.notifications import (
        NotificationMessage,
        WebhookNotificationConfig,
        dispatch_webhook_notification,
    )

    data = _load_mapping(Path(args.input).resolve())
    config = WebhookNotificationConfig.model_validate(data.get("config"))
    message = NotificationMessage.model_validate(data.get("message"))
    print(dispatch_webhook_notification(config, message).model_dump_json(indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Ultimate Travel Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser(
        "install-skills", help="Install travel skills into a project"
    )
    install_parser.add_argument("--target", "-t", required=True, help="Target project path")
    install_parser.add_argument("--include-agents", action="store_true", help="Include sub-agents")
    install_parser.add_argument(
        "--include-workflows", action="store_true", help="Include workflows"
    )
    install_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing files"
    )
    install_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate installation without touching files"
    )

    uninstall_parser = subparsers.add_parser(
        "uninstall-skills", help="Uninstall travel skills from a project"
    )
    uninstall_parser.add_argument("--target", "-t", required=True, help="Target project path")
    uninstall_parser.add_argument(
        "--force", "-f", action="store_true", help="Remove even if files were modified"
    )
    uninstall_parser.add_argument(
        "--clean-modified", action="store_true", help="Remove user-modified files"
    )
    uninstall_parser.add_argument("--dry-run", action="store_true", help="Simulate uninstallation")

    subparsers.add_parser("list-skills", help="List available travel skills")

    val_parser = subparsers.add_parser(
        "validate-skills", help="Validate quality and standards of travel skills"
    )
    val_parser.add_argument("--path", "-p", help="Optional path to skills folder")

    dossier_parser = subparsers.add_parser(
        "validate-dossier", help="Validate a JSON/YAML TravelDossier v1 file"
    )
    dossier_parser.add_argument("path", help="Path to a JSON or YAML dossier")

    handoff_parser = subparsers.add_parser(
        "validate-handoff", help="Validate a JSON/YAML compact-handoff/v2 file"
    )
    handoff_parser.add_argument("path", help="Path to a JSON or YAML handoff")

    prompt_audit_parser = subparsers.add_parser(
        "prompt-audit", help="Measure canonical prompt corpus size and a stable token proxy"
    )
    prompt_audit_parser.add_argument(
        "--path", help="Optional .agents or installed bundle directory"
    )

    source_url_parser = subparsers.add_parser(
        "normalize-source-url", help="Canonicalize an HTTP(S) source URL for deduplication"
    )
    source_url_parser.add_argument("url", help="Original source URL")

    profile_save_parser = subparsers.add_parser(
        "profile-save", help="Validate and save a traveler profile"
    )
    profile_save_parser.add_argument("input", help="Input JSON/YAML profile")
    profile_save_parser.add_argument("output", help="Destination JSON profile")

    profile_show_parser = subparsers.add_parser(
        "profile-show", help="Show a validated traveler profile"
    )
    profile_show_parser.add_argument("path", help="Profile JSON path")

    export_parser = subparsers.add_parser(
        "export-dossier", help="Export a valid dossier"
    )
    export_parser.add_argument("input", help="Input JSON/YAML dossier")
    export_parser.add_argument("output", help="Output artifact path")
    export_parser.add_argument(
        "--format",
        choices=["ics", "geojson", "pdf", "checklist", "offline", "html"],
        required=True,
    )

    revalidation_parser = subparsers.add_parser(
        "revalidation-plan", help="Build a pre-departure verification schedule"
    )
    revalidation_parser.add_argument("input", help="Input JSON/YAML dossier")
    revalidation_parser.add_argument("--departure", required=True, help="YYYY-MM-DD")

    flight_plan_parser = subparsers.add_parser(
        "flight-search-plan", help="Generate a four-pass flexible-flight matrix"
    )
    flight_plan_parser.add_argument("input", help="Input JSON/YAML flight request")
    flight_plan_parser.add_argument("output", help="Output JSON search plan")

    flight_coverage_parser = subparsers.add_parser(
        "flight-search-coverage", help="Validate completed flight-search coverage"
    )
    flight_coverage_parser.add_argument("input", help="Flight search plan JSON/YAML")
    flight_coverage_parser.add_argument(
        "--booking-ready",
        action="store_true",
        help="Require source evidence on every searched combination",
    )

    hotel_plan_parser = subparsers.add_parser(
        "hotel-search-plan", help="Generate transit-first hotel comparison tasks"
    )
    hotel_plan_parser.add_argument("input", help="Input JSON/YAML hotel request")
    hotel_plan_parser.add_argument("output", help="Output JSON research plan")

    hotel_coverage_parser = subparsers.add_parser(
        "hotel-search-coverage", help="Validate hotel research coverage"
    )
    hotel_coverage_parser.add_argument("input", help="Hotel research plan JSON/YAML")
    hotel_coverage_parser.add_argument(
        "--booking-ready",
        action="store_true",
        help="Require transit, two discovery sources, and official verification",
    )

    hotel_compare_parser = subparsers.add_parser(
        "hotel-compare", help="Compare final hotel prices and transit access"
    )
    hotel_compare_parser.add_argument("input", help="Comparison JSON/YAML payload")

    hotel_mobility_parser = subparsers.add_parser(
        "hotel-mobility", help="Score hotel transit to real trip anchors"
    )
    hotel_mobility_parser.add_argument("input", help="Mobility JSON/YAML payload")
    hotel_mobility_parser.add_argument(
        "--maximum-walking-minutes", type=int, default=15
    )
    hotel_mobility_parser.add_argument("--step-free-required", action="store_true")

    total_cost_parser = subparsers.add_parser(
        "compare-total-cost", help="Compare true door-to-door travel costs"
    )
    total_cost_parser.add_argument("input", help="Cost comparison JSON/YAML payload")

    price_watch_parser = subparsers.add_parser(
        "price-watch", help="Assess a sourced flight or hotel price history"
    )
    price_watch_parser.add_argument("input", help="Price watch JSON/YAML payload")

    disruption_parser = subparsers.add_parser(
        "disruption-plan", help="Replace only disrupted itinerary items"
    )
    disruption_parser.add_argument("input", help="Disruption recovery JSON/YAML payload")
    disruption_parser.add_argument(
        "--cascade",
        action="store_true",
        help="Propagate missed connections through declared dependencies",
    )

    connector_parser = subparsers.add_parser(
        "connector-fetch", help="Execute a secure live JSON connector request"
    )
    connector_parser.add_argument("input", help="Connector config and request JSON/YAML")

    adaptive_parser = subparsers.add_parser(
        "adaptive-day", help="Build weather and energy day variants"
    )
    adaptive_parser.add_argument("input", help="Adaptive day JSON/YAML payload")

    group_parser = subparsers.add_parser(
        "group-decide", help="Rank group options with hard vetoes"
    )
    group_parser.add_argument("input", help="Group decision JSON/YAML payload")

    neighborhood_parser = subparsers.add_parser(
        "neighborhood-score", help="Score evidence-backed neighborhood quality"
    )
    neighborhood_parser.add_argument("input", help="Neighborhood JSON/YAML payload")

    booking_parser = subparsers.add_parser(
        "booking-handoff", help="Prepare a user-controlled booking checkout"
    )
    booking_parser.add_argument("input", help="Booking handoff JSON/YAML payload")

    trip_mode_parser = subparsers.add_parser(
        "trip-mode", help="Show current trip state and next action"
    )
    trip_mode_parser.add_argument("input", help="Trip mode JSON/YAML payload")

    route_parser = subparsers.add_parser(
        "route-optimize", help="Optimize sourced travel times and visit windows"
    )
    route_parser.add_argument("input", help="Route optimization JSON/YAML payload")

    notify_parser = subparsers.add_parser(
        "notify-webhook", help="Deliver an explicitly configured signed alert"
    )
    notify_parser.add_argument("input", help="Webhook config and message JSON/YAML")

    args = parser.parse_args()

    if args.command == "install-skills":
        install_skills_cmd(args)
    elif args.command == "uninstall-skills":
        uninstall_skills_cmd(args)
    elif args.command == "list-skills":
        list_skills_cmd(args)
    elif args.command == "validate-skills":
        validate_skills_cmd(args)
    elif args.command == "validate-dossier":
        validate_dossier_cmd(args)
    elif args.command == "validate-handoff":
        validate_handoff_cmd(args)
    elif args.command == "prompt-audit":
        prompt_audit_cmd(args)
    elif args.command == "normalize-source-url":
        normalize_source_url_cmd(args)
    elif args.command == "profile-save":
        profile_save_cmd(args)
    elif args.command == "profile-show":
        profile_show_cmd(args)
    elif args.command == "export-dossier":
        export_dossier_cmd(args)
    elif args.command == "revalidation-plan":
        revalidation_plan_cmd(args)
    elif args.command == "flight-search-plan":
        flight_search_plan_cmd(args)
    elif args.command == "flight-search-coverage":
        flight_search_coverage_cmd(args)
    elif args.command == "hotel-search-plan":
        hotel_search_plan_cmd(args)
    elif args.command == "hotel-search-coverage":
        hotel_search_coverage_cmd(args)
    elif args.command == "hotel-compare":
        hotel_compare_cmd(args)
    elif args.command == "hotel-mobility":
        hotel_mobility_cmd(args)
    elif args.command == "compare-total-cost":
        compare_total_cost_cmd(args)
    elif args.command == "price-watch":
        price_watch_cmd(args)
    elif args.command == "disruption-plan":
        disruption_plan_cmd(args)
    elif args.command == "connector-fetch":
        connector_fetch_cmd(args)
    elif args.command == "adaptive-day":
        adaptive_day_cmd(args)
    elif args.command == "group-decide":
        group_decide_cmd(args)
    elif args.command == "neighborhood-score":
        neighborhood_score_cmd(args)
    elif args.command == "booking-handoff":
        booking_handoff_cmd(args)
    elif args.command == "trip-mode":
        trip_mode_cmd(args)
    elif args.command == "route-optimize":
        route_optimize_cmd(args)
    elif args.command == "notify-webhook":
        notify_webhook_cmd(args)


if __name__ == "__main__":
    main()

# Backward compatibility aliases for CLI functions and tests
install_skills = install_skills_cmd
uninstall_skills = uninstall_skills_cmd


def get_base_dir() -> Path:
    """Return repository or pack base directory."""
    root = find_pack_root()
    if root.name == ".agents":
        return root.parent
    return root.parent if root.name == "bundle" else root
