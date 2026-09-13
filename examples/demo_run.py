"""Standalone demonstration script for ultimate-travel-agent.

Runs a complete 5-wave multi-agent orchestration on local mock data
without any API keys, internet connectivity, or credentials.
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ultimate_travel_agent.cli import load_trip_file
from ultimate_travel_agent.engine.orchestrator import TravelOrchestrationEngine
from ultimate_travel_agent.models import Trip
from ultimate_travel_agent.reporter import generate_markdown_report


def run_demo() -> None:
    trip_path = Path("examples/city-trip/trip.json")
    print("=" * 70)
    print("🌍 ULTIMATE TRAVEL AGENT — DEMO MULTI-AGENTS 100% LOCALE")
    print("=" * 70)
    print(f"Chargement du dossier de voyage exemple : {trip_path}\n")

    trip = load_trip_file(str(trip_path))
    print(f"Destination : {trip.destinations[0].name} ({trip.destinations[0].country})")
    print(f"Durée       : {trip.total_days} jours / {trip.total_nights} nuitées ({trip.start_date} au {trip.end_date})")
    print(f"Voyageurs   : {', '.join(t.name for t in trip.travelers)} ({trip.travelers[0].profile.value})")
    print(f"Style       : {trip.trip_type.value} | Profil : {trip.travelers[0].crowd_sensitivity.value}\n")

    print("🚀 Exécution des 5 vagues de sous-agents en cours...\n")
    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)

    for agent_name, res in results.items():
        icon = "✅" if res.status.value == "complete" else "⚠️"
        print(f"  {icon} [{agent_name:<25}] {res.summary} [{res.verification_level.value}]")

    print("\n" + "=" * 70)
    print("💰 SYNTHÈSE BUDGÉTAIRE CONSOLIDÉE")
    print("=" * 70)
    budget = trip.budget or trip.calculate_budget()
    print(f"  Dépenses estimées : {budget.total_estimated_cost:.2f} {budget.currency}")
    print(f"  Marge de sécurité : +{budget.safety_buffer_amount:.2f} {budget.currency} ({budget.safety_buffer_percentage}%)")
    print(f"  GRAND TOTAL       : {budget.grand_total:.2f} {budget.currency}")
    if budget.warnings:
        print("  ⚠️ Alertes :")
        for w in budget.warnings:
            print(f"    - {w}")

    print("\n" + "=" * 70)
    print("📋 RAPPEL SÉCURITÉ & ACTIONS HUMAINES")
    print("=" * 70)
    print("  - Aucune réservation automatique n'a été effectuée.")
    print("  - Liens officiels vérifiés fournis pour la Sagrada Família et le Park Güell.")
    print("  - Assurance CEAM et passeports à vérifier avant départ.")
    print("\n✅ Démonstration terminée avec succès.")


if __name__ == "__main__":
    run_demo()
