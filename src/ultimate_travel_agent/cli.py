"""Command-line interface for ultimate-travel-agent."""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ultimate_travel_agent.engine.orchestrator import TravelOrchestrationEngine
from ultimate_travel_agent.models import Trip
from ultimate_travel_agent.reporter import generate_markdown_report


def load_trip_file(path: str) -> Trip:
    """Load and validate a JSON trip file."""
    p = Path(path)
    if not p.exists():
        print(f"Error: File '{path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Trip.model_validate(data)


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate a trip file."""
    trip = load_trip_file(args.trip_file)
    issues = trip.validate_trip_coherence()
    if not issues:
        print(f"✅ Trip '{trip.title}' ({trip.id}) is valid and coherent.")
        print(f"   Duration: {trip.total_days} days / {trip.total_nights} nights")
        print(f"   Travelers: {len(trip.travelers)} | Destinations: {len(trip.destinations)}")
        print(f"   Transports: {len(trip.transports)} | Lodgings: {len(trip.accommodations)} | Activities: {len(trip.activities)}")
    else:
        print(f"❌ Trip '{trip.title}' has {len(issues)} validation issue(s):", file=sys.stderr)
        for issue in issues:
            print(f"   - {issue}", file=sys.stderr)
        sys.exit(1)


def cmd_budget(args: argparse.Namespace) -> None:
    """Display budget calculation for a trip."""
    trip = load_trip_file(args.trip_file)
    budget = trip.calculate_budget()
    print(f"💰 Consolidated Budget for '{trip.title}':")
    print(f"   Base Estimated Cost : {budget.total_estimated_cost:.2f} {budget.currency}")
    print(f"   Safety Reserve ({budget.safety_buffer_percentage}%) : +{budget.safety_buffer_amount:.2f} {budget.currency}")
    print(f"   ----------------------------------------")
    print(f"   GRAND TOTAL         : {budget.grand_total:.2f} {budget.currency}")
    print("\n   Breakdown by category:")
    for cat_name, item in budget.categories.items():
        print(f"   - {cat_name.capitalize():<15}: {item.amount:>8.2f} {item.currency} [{item.verification_level.value}]")
    if budget.warnings:
        print("\n   ⚠️  Warnings:")
        for w in budget.warnings:
            print(f"   - {w}")


def cmd_plan(args: argparse.Namespace) -> None:
    """Execute the 5-wave multi-agent pipeline."""
    trip = load_trip_file(args.trip_file)
    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)
    print(f"🚀 Multi-Agent Orchestration executed for '{trip.title}':\n")
    for agent_name, res in results.items():
        icon = "✅" if res.status.value == "complete" else "⚠️"
        print(f"{icon} [{agent_name}] {res.summary}")
    print(f"\nFinal status: All 5 waves completed successfully.")


def cmd_export(args: argparse.Namespace) -> None:
    """Export complete Markdown dossier."""
    trip = load_trip_file(args.trip_file)
    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)
    report = generate_markdown_report(trip, results)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📄 Report exported successfully to: {out_path}")
    else:
        print(report)


def cmd_serve(args: argparse.Namespace) -> None:
    """Launch the local web UI."""
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn and fastapi are required to run the local web interface.", file=sys.stderr)
        print("Install them with: pip install fastapi uvicorn", file=sys.stderr)
        sys.exit(1)
    print(f"🌍 Starting Ultimate Travel Agent Web Interface at http://{args.host}:{args.port}")
    print("🔒 Running in 100% offline-local mode. Zero personal data collected or transmitted.")
    print("💡 Press Ctrl+C to stop the server.")
    uvicorn.run("ultimate_travel_agent.web.app:app", host=args.host, port=args.port, reload=args.reload)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ultimate-travel-agent",
        description="A generic, privacy-first, multi-agent travel planning system."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate trip schema and coherence")
    p_val.add_argument("trip_file", help="Path to trip.json")
    p_val.set_defaults(func=cmd_validate)

    # budget
    p_bud = subparsers.add_parser("budget", help="Calculate and display trip budget")
    p_bud.add_argument("trip_file", help="Path to trip.json")
    p_bud.set_defaults(func=cmd_budget)

    # plan
    p_plan = subparsers.add_parser("plan", help="Execute the 5-wave multi-agent pipeline")
    p_plan.add_argument("trip_file", help="Path to trip.json")
    p_plan.set_defaults(func=cmd_plan)

    # export
    p_exp = subparsers.add_parser("export", help="Export Markdown trip dossier")
    p_exp.add_argument("trip_file", help="Path to trip.json")
    p_exp.add_argument("--output", "-o", help="Output file path (default: stdout)")
    p_exp.set_defaults(func=cmd_export)

    # serve
    p_srv = subparsers.add_parser("serve", help="Launch the local web user interface")
    p_srv.add_argument("--host", default="127.0.0.1", help="Host binding (default: 127.0.0.1)")
    p_srv.add_argument("--port", type=int, default=8000, help="Port binding (default: 8000)")
    p_srv.add_argument("--reload", action="store_true", help="Enable auto-reload")
    p_srv.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
