"""Markdown report generation for ultimate-travel-agent."""

from typing import Dict, Optional
from ultimate_travel_agent.engine.contingency import generate_contingency_dossier
from ultimate_travel_agent.engine.route_optimizer import evaluate_all_preferences, recommend_route_option
from ultimate_travel_agent.models import AgentResult, Trip


def generate_markdown_report(trip: Trip, agent_results: Optional[Dict[str, AgentResult]] = None) -> str:
    """Render a comprehensive, human-readable Markdown travel dossier."""
    lines = []
    lines.append(f"# Dossier de Voyage : {trip.title}")
    lines.append("")
    lines.append("> ⚠️ **Mode Planification Locale Hors-Ligne** :")
    lines.append("> Offline local planning mode:")
    lines.append("> No live availability, price, opening-hour or booking verification.")
    lines.append("")
    lines.append(f"- **Dates :** Du {trip.start_date} au {trip.end_date} ({trip.total_nights} nuitées, {trip.total_days} jours)")
    lines.append(f"- **Style de séjour :** `{trip.trip_type.value}`")
    lines.append(f"- **Devise de référence :** `{trip.currency}`")
    if trip.budget_cap:
        lines.append(f"- **Plafond budgétaire indicatif :** {trip.budget_cap:.2f} {trip.currency}")
    lines.append("")

    # 1. Travelers
    lines.append("## 1. Voyageurs")
    for t in trip.travelers:
        diet = f" (Régime : {', '.join(t.dietary_restrictions)})" if t.dietary_restrictions else ""
        lines.append(f"- **{t.name}** [{t.profile.value}] — Rythme : `{t.pacing_preference.value}`, Affluence : `{t.crowd_sensitivity.value}`{diet}")
    lines.append("")

    # 2. Destinations & Stages
    lines.append("## 2. Destinations & Contexte Géographique")
    for d in trip.destinations:
        lines.append(f"### {d.name} ({d.country})")
        if d.description:
            lines.append(f"{d.description}")
        if d.anecdote:
            lines.append(f"> *Note locale / Anecdote : {d.anecdote}*")
        if d.quiet_periods:
            lines.append(f"- **Périodes calmes recommandées :** {', '.join(d.quiet_periods)}")
        lines.append("")

    if trip.stages:
        lines.append("### Étapes & Itinérance")
        for s in trip.stages:
            dates = f" ({s.arrival_date} -> {s.departure_date})" if s.arrival_date else ""
            lines.append(f"- **Étape {s.order} : {s.title or s.id}**{dates} — {s.nights} nuitée(s) `[{s.verification_level.value}]`")
            if s.notes:
                lines.append(f"  - *Notes :* {s.notes}")
        lines.append("")

    # 3. Transports & Inter-City Routes
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

    if trip.inter_city_routes:
        lines.append("### Comparateur d'Itinéraires Inter-Villes Multi-Options")
        for route in trip.inter_city_routes:
            lines.append(f"#### Trajet : {route.origin} ➔ {route.destination}")
            evals = evaluate_all_preferences(route)
            lines.append("| Option | Mode | Durée | Coût | Confort | Empreinte CO2 | Statut |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for opt in route.options:
                lines.append(f"| **{opt.id}** | {opt.mode.value} | {opt.estimated_duration_minutes} min | {opt.estimated_cost:.2f} {opt.currency} | {opt.comfort_level}/5 | {opt.carbon_footprint_kg or '?'} kg | `{opt.status.value}` |")
            lines.append("")
            lines.append("**Recommandations selon votre profil :**")
            for pref_key, val in evals.items():
                lines.append(f"- `{pref_key}` : {val['reason']}")
            lines.append("")

    # 4. Accommodations
    lines.append("## 4. Hébergements Vrais & Stratégiques")
    for acc in trip.accommodations:
        booking = f" — [Lien Direct Hôtel]({acc.official_booking_url})" if acc.official_booking_url else ""
        lines.append(f"- **{acc.name}** ({acc.neighborhood}) — {acc.total_nights} nuit(s) à {acc.cost_per_night:.2f} {acc.currency}/nuit (Total : {acc.total_cost:.2f} {acc.currency}) `[{acc.verification_level.value}]`{booking}")
        if acc.criteria_matched:
            lines.append(f"  - *Points forts :* {', '.join(acc.criteria_matched)}")
    lines.append("")

    # 5. Activities & POIs
    if trip.activities:
        lines.append("## 5. Activités & Points d'Intérêt Curationnés")
        for act in trip.activities:
            booking = f" — [Billetterie]({act.official_booking_url})" if act.official_booking_url else ""
            lines.append(f"### {act.title} `[{act.category.value}]` `[{act.verification_level.value}]`{booking}")
            lines.append(f"- **Localisation :** {act.neighborhood or ''} {act.city or ''} {act.country or ''}".strip())
            lines.append(f"- **Durée & Coût :** {act.duration_minutes} min — {act.estimated_cost:.2f} {act.currency}/pers")
            lines.append(f"- **Description :** {act.description}")
            if act.anecdote:
                lines.append(f"> 💡 *Contexte local :* {act.anecdote}")
            if act.best_time_slot:
                lines.append(f"- **Meilleur créneau :** {act.best_time_slot}")
            if act.effective_crowd_strategy:
                lines.append(f"- **Stratégie anti-foule :** {act.effective_crowd_strategy}")
            if act.weather_alternative:
                lines.append(f"- ☔ **Alternative mauvais temps :** {act.weather_alternative}")
            if act.closure_alternative:
                lines.append(f"- 🚪 **Alternative si fermeture :** {act.closure_alternative}")
            lines.append("")

    # 6. Itinerary Day-by-day
    lines.append("## 6. Itinéraire Détaillé Jour par Jour")
    for day in trip.itinerary:
        date_str = f" ({day.date})" if day.date else ""
        lines.append(f"### Jour {day.day_number}{date_str} — {day.theme or 'Journée'}")
        if day.weather_contingency_notes:
            lines.append(f"> ☔ *Plan de secours météo :* {day.weather_contingency_notes}")
        for item in day.items:
            notes = f" ({item.notes})" if item.notes else ""
            lines.append(f"- **{item.time}** `[{item.item_type}]` : {item.title} ({item.duration_minutes} min){notes}")
        lines.append("")

    # 7. Budget
    lines.append("## 7. Budget Prévisionnel Consolidé")
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

    # 8. Contingency & Preparation Dossier
    contingency = generate_contingency_dossier(trip)
    lines.append("## 8. Plans B et Trousse de Préparation")
    lines.append("")
    lines.append("### A. Checklist Avant Départ")
    for chk in contingency.pre_departure_checklist:
        req = "*(Obligatoire)*" if chk["mandatory"] else "*(Conseillé)*"
        lines.append(f"- [ ] **{chk['title']}** {req} — Délai : `{chk['deadline']}`")
        lines.append(f"  - Action : {chk['action']} `[{chk['verification_note']}]`")
    lines.append("")

    lines.append("### B. Checklist de Réservations")
    lines.append("> 🔒 *Rappel de sécurité : Ce système n'effectue aucun paiement automatique.*")
    for b in contingency.booking_checklist:
        cost = f" ({b['estimated_cost']:.2f} {b['currency']})" if b.get('estimated_cost', 0) > 0 else ""
        url = f" — [Portail Officiel]({b['booking_url']})" if b.get("booking_url") else ""
        lines.append(f"- [ ] **{b['title']}**{cost} `[{b['verification_level']}]`{url}")
        lines.append(f"  - Conseil : {b['timing_advice']}")
    lines.append("")

    lines.append("### C. Documents à Vérifier Avant Départ")
    for doc in contingency.document_verification_list:
        lines.append(f"- **{doc['document']}** : {doc['requirement']}")
        lines.append(f"  - Règle : {doc['rule']}")
        lines.append(f"  - Statut de vérification : *`{doc['status']}`*")
    lines.append("")

    lines.append("### D. Plan B Météo")
    for w in contingency.weather_contingency_plan:
        lines.append(f"- **Jour {w['day_number']} ({w['date'] or 'Date libre'}) :** {w['general_contingency_notes']}")
        for out in w["outdoor_contingencies"]:
            lines.append(f"  - 🌧️ Repli pour *{out['activity']}* : {out['backup']}")
    lines.append("")

    lines.append("### E. Plan B Fermeture d'Activité")
    for cl in contingency.activity_closure_plan:
        lines.append(f"- En cas de fermeture de **{cl['activity_title']}** : {cl['recommended_alternative']}")
    lines.append("")

    lines.append("### F. Informations à Confirmer Avant Réservation Définitive")
    for conf in contingency.pre_booking_confirmation_items:
        lines.append(f"- **[{conf['category']}] {conf['item']}** : {conf['checklist_point']}")
        lines.append(f"  - *Risque si non vérifié :* {conf['risk_if_unconfirmed']}")
    lines.append("")

    lines.append("### G. Fiche d'Urgence Générique")
    lines.append("> 🛡️ *Garantie de non-fabrication : Aucun hôpital, médecin ou numéro fictif n'est inventé.*")
    em = contingency.generic_emergency_summary
    lines.append(f"- **Destination :** {em.get('destination')}")
    lines.append(f"- **Numéro d'appel d'urgence :** {em.get('emergency_dispatch_reminder')}")
    lines.append(f"- **Assistance Consulaire :** {em.get('consular_support_reminder')}")
    lines.append(f"- **Assistance Médicale :** {em.get('medical_assistance_reminder')}")
    lines.append(f"- **Perte de Cartes Bancaires :** {em.get('lost_payment_cards_hotline')}")
    lines.append("- **Protocole d'urgence recommandé :**")
    for step in em.get("incident_procedure", []):
        lines.append(f"  {step}")
    lines.append("")

    # 9. Multi-Agent Wave & Pipeline Audit Summary
    lines.append("## 9. Visibilité et Bilan d'Exécution Multi-Agents (9 Étapes Déterministes)")
    lines.append("")
    lines.append("> *Transparence algorithmique du moteur d'orchestration :*")
    lines.append("")
    if agent_results:
        # Numbered 9-step mapping
        step_mapping = [
            ("1. Destination research", "destination-researcher"),
            ("2. Transport planning", "transport-planner"),
            ("3. Accommodation research", "accommodation-researcher"),
            ("4. Activity curation", "activity-curator"),
            ("5. Local discovery", "local-discovery-agent"),
            ("6. Travel preparation", "travel-preparation-agent"),
            ("7. Budget analysis", "budget-analyst"),
            ("8. Itinerary optimization", "itinerary-optimizer"),
            ("9. Quality control", "quality-controller"),
        ]
        for step_label, agent_key in step_mapping:
            res = agent_results.get(agent_key)
            if res:
                icon = "✅" if res.status.value == "complete" else ("⚠️" if res.status.value == "partial" else "❌")
                lines.append(f"### {icon} {step_label} (`{res.agent}`)")
                lines.append(f"- **Statut :** `{res.status.value.upper()}` | **Niveau de preuve :** `[{res.verification_level.value}]`")
                lines.append(f"- **Résumé :** {res.summary}")
                if res.assumptions:
                    lines.append(f"- **Hypothèses :** {', '.join(res.assumptions)}")
                if res.missing_information:
                    lines.append(f"- **Informations manquantes :** {', '.join(res.missing_information)}")
                if res.risks:
                    lines.append(f"- **Risques identifiés :** {', '.join(res.risks)}")
                if res.sources:
                    src_titles = [f"[{s.title}]({s.url})" if s.url else s.title for s in res.sources]
                    lines.append(f"- **Sources :** {', '.join(src_titles)}")
                lines.append("")

    lines.append("---")
    lines.append("*Rapport généré de manière 100% autonome et déterministe par `ultimate-travel-agent` v1.1.*")
    return "\n".join(lines)
