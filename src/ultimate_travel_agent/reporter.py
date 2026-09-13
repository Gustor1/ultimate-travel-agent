"""Markdown report generation for ultimate-travel-agent."""

from typing import Dict, Optional
from ultimate_travel_agent.models import AgentResult, Trip


def generate_markdown_report(trip: Trip, agent_results: Optional[Dict[str, AgentResult]] = None) -> str:
    """Render a comprehensive, human-readable Markdown travel dossier."""
    lines = []
    lines.append(f"# Dossier de Voyage : {trip.title}")
    lines.append("")
    lines.append(f"- **Dates :** Du {trip.start_date} au {trip.end_date} ({trip.total_nights} nuitées, {trip.total_days} jours)")
    lines.append(f"- **Style de séjour :** `{trip.trip_type.value}`")
    lines.append(f"- **Devise de référence :** `{trip.currency}`")
    if trip.budget_cap:
        lines.append(f"- **Plafond budgétaire indicatif :** {trip.budget_cap:.2f} {trip.currency}")
    lines.append("")

    # Travelers
    lines.append("## 1. Voyageurs")
    for t in trip.travelers:
        diet = f" (Régime : {', '.join(t.dietary_restrictions)})" if t.dietary_restrictions else ""
        lines.append(f"- **{t.name}** [{t.profile.value}] — Rythme : `{t.pacing_preference.value}`, Affluence : `{t.crowd_sensitivity.value}`{diet}")
    lines.append("")

    # Destinations
    lines.append("## 2. Destinations & Contexte")
    for d in trip.destinations:
        lines.append(f"### {d.name} ({d.country})")
        if d.description:
            lines.append(f"{d.description}")
        if d.anecdote:
            lines.append(f"> *Note locale / Anecdote : {d.anecdote}*")
        if d.quiet_periods:
            lines.append(f"- **Périodes calmes recommandées :** {', '.join(d.quiet_periods)}")
        lines.append("")

    # Stages (if modeled)
    if trip.stages:
        lines.append("### Étapes & Itinérance")
        for s in trip.stages:
            dates = f" ({s.arrival_date} -> {s.departure_date})" if s.arrival_date else ""
            lines.append(f"- **Étape {s.order} : {s.title or s.id}**{dates} — {s.nights} nuitée(s) `[{s.verification_level.value}]`")
            if s.notes:
                lines.append(f"  - *Notes :* {s.notes}")
        lines.append("")

    # Transports
    lines.append("## 3. Transports & Mobilité")
    for tr in trip.transports:
        carrier = f" via {tr.carrier}" if tr.carrier else ""
        dep_arr = f" ({tr.departure_time or '?'} -> {tr.arrival_time or '?'})" if tr.departure_time else ""
        booking = f" — [Billetterie Officielle]({tr.official_booking_url})" if tr.official_booking_url else ""
        pricing_note = " (par passager)" if tr.effective_is_per_person else " (par véhicule)"
        lines.append(f"- **[{tr.mode.value.upper()}]** {tr.origin} -> {tr.destination}{carrier}{dep_arr} — Durée : {tr.duration_minutes} min — Coût estimé : {tr.estimated_cost:.2f} {tr.currency}{pricing_note} `[{tr.verification_level.value}]`{booking}")
        if tr.door_to_door_notes:
            lines.append(f"  - *Conseil transit :* {tr.door_to_door_notes}")
    lines.append("")

    # Accommodations
    lines.append("## 4. Hébergements Vrais & Stratégiques")
    for acc in trip.accommodations:
        booking = f" — [Lien Direct Hôtel]({acc.official_booking_url})" if acc.official_booking_url else ""
        lines.append(f"- **{acc.name}** ({acc.neighborhood}) — {acc.total_nights} nuit(s) à {acc.cost_per_night:.2f} {acc.currency}/nuit (Total : {acc.total_cost:.2f} {acc.currency}) `[{acc.verification_level.value}]`{booking}")
        if acc.criteria_matched:
            lines.append(f"  - *Points forts :* {', '.join(acc.criteria_matched)}")
    lines.append("")

    # Itinerary Day-by-day
    lines.append("## 5. Itinéraire Détaillé Jour par Jour")
    for day in trip.itinerary:
        date_str = f" ({day.date})" if day.date else ""
        lines.append(f"### Jour {day.day_number}{date_str} — {day.theme or 'Journée'}")
        if day.weather_contingency_notes:
            lines.append(f"> ☔ *Plan de secours météo :* {day.weather_contingency_notes}")
        for item in day.items:
            notes = f" ({item.notes})" if item.notes else ""
            lines.append(f"- **{item.time}** `[{item.item_type}]` : {item.title} ({item.duration_minutes} min){notes}")
        lines.append("")

    # Budget
    lines.append("## 6. Budget Prévisionnel Consolidé")
    budget = trip.budget or trip.calculate_budget()
    lines.append(f"- **Dépenses estimées poste par poste :** {budget.total_estimated_cost:.2f} {budget.currency}")
    lines.append(f"- **Marge de sécurité ({budget.safety_buffer_percentage}%) :** +{budget.safety_buffer_amount:.2f} {budget.currency}")
    lines.append(f"- **TOTAL GÉNÉRAL CONSOLIDÉ :** **{budget.grand_total:.2f} {budget.currency}**")
    lines.append("")
    lines.append("| Poste de dépense | Montant estimé | Niveau de vérification |")
    lines.append("| :--- | :--- | :--- |")
    for cat_name, breakdown in budget.categories.items():
        lines.append(f"| {cat_name.capitalize()} | {breakdown.amount:.2f} {breakdown.currency} | `{breakdown.verification_level.value}` |")
    lines.append("")
    if budget.warnings:
        lines.append("### ⚠️ Alertes Budgétaires")
        for w in budget.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Reservations / Bookings
    if trip.reservations:
        lines.append("## 7. Réservations & Actions Manuelles Requises")
        lines.append("> 🔒 *Rappel éthique et sécurité : Ce système n'effectue aucun paiement automatique.*")
        for r in trip.reservations:
            mandatory = "*(Obligatoire)*" if r.mandatory else "*(Optionnel)*"
            url = f" — [Lien Réservation Officiel]({r.official_booking_url})" if r.official_booking_url else ""
            cost = f" — Coût estimé : {r.estimated_cost:.2f} {r.currency}" if r.estimated_cost > 0 else ""
            lines.append(f"- `[{r.status.upper()}]` **{r.title}** {mandatory}{cost} `[{r.verification_level.value}]`{url}")
            if r.action_required:
                lines.append(f"  - *Action :* {r.action_required}")
        lines.append("")

    # Checklist
    chk_header = "## 8. Checklist Préparation & Sécurité" if trip.reservations else "## 7. Checklist Préparation & Sécurité"
    lines.append(chk_header)
    for chk in trip.checklists:
        status_box = "[x]" if chk.completed else "[ ]"
        mandatory = "*(Obligatoire)*" if chk.is_mandatory else "*(Optionnel)*"
        ref = f" — [Lien Officiel]({chk.official_reference_url})" if chk.official_reference_url else ""
        lines.append(f"- {status_box} **{chk.title}** {mandatory} : {chk.description} `[{chk.verification_level.value}]`{ref}")
    lines.append("")

    # Multi-agent wave audit summary
    audit_header = "## 9. Bilan d'Exécution Multi-Agents" if trip.reservations else "## 8. Bilan d'Exécution Multi-Agents"
    if agent_results:
        lines.append(audit_header)
        for agent_name, res in agent_results.items():
            icon = "✅" if res.status.value == "complete" else ("⚠️" if res.status.value == "partial" else "❌")
            lines.append(f"- {icon} **`{agent_name}`** : {res.summary} `[{res.verification_level.value}]`")
            for risk in res.risks:
                lines.append(f"  - ⚠️ *{risk}*")
        lines.append("")

    lines.append("---")
    lines.append("*Rapport généré de manière 100% autonome et déterministe par `ultimate-travel-agent`.*")
    return "\n".join(lines)
