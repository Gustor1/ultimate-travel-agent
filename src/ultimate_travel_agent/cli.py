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
    sync_pack_mirror,
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


def sync_pack_cmd(args: argparse.Namespace) -> None:
    """Generate or verify the compatibility mirror."""
    result = sync_pack_mirror(check=args.check)
    if args.check and result["out_of_sync"]:
        print("Pack mirror is out of sync:")
        for path in result["out_of_sync"]:
            print(f"  - {path}")
        raise SystemExit(1)
    if result["changed"]:
        print(f"Synchronized {len(result['changed'])} files.")
    else:
        print("Pack mirror is synchronized.")


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
        PriceObservation,
        PriceWatch,
        assess_price_watch,
    )

    data = _load_mapping(Path(args.input).resolve())
    watch = PriceWatch.model_validate(data.get("watch"))
    observations = TypeAdapter(list[PriceObservation]).validate_python(
        data.get("observations")
    )
    print(assess_price_watch(watch, observations).model_dump_json(indent=2))


def disruption_plan_cmd(args: argparse.Namespace) -> None:
    """Build a recovery plan while preserving unaffected itinerary items."""
    from pydantic import TypeAdapter

    from ultimate_travel_agent.disruptions import (
        Disruption,
        ItineraryItem,
        RecoveryOption,
        build_recovery_plan,
    )

    data = _load_mapping(Path(args.input).resolve())
    itinerary = TypeAdapter(list[ItineraryItem]).validate_python(data.get("itinerary"))
    disruption = Disruption.model_validate(data.get("disruption"))
    options = TypeAdapter(list[RecoveryOption]).validate_python(data.get("options"))
    result = build_recovery_plan(itinerary, disruption, options)
    print(result.model_dump_json(indent=2))
    if not result.complete:
        raise SystemExit(1)


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

    sync_parser = subparsers.add_parser(
        "sync-pack", help="Generate the compatibility skill mirror from canonical .agents assets"
    )
    sync_parser.add_argument(
        "--check", action="store_true", help="Fail if the mirror is out of sync"
    )

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
    elif args.command == "sync-pack":
        sync_pack_cmd(args)
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
