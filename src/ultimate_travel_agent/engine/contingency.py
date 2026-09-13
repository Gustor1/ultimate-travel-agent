"""Contingency, backup planning, and travel preparation engine for ultimate-travel-agent."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import ActivityCategory, EnvironmentType, TransportMode
from ultimate_travel_agent.models.trip import Trip

_OFFICIAL_NOTICE = "Requires official source verification."


class ContingencyDossier(BaseModel):
    """Structured preparation and contingency pack for a journey."""

    trip_id: str
    trip_title: str
    pre_departure_checklist: List[Dict[str, Any]] = Field(default_factory=list)
    booking_checklist: List[Dict[str, Any]] = Field(default_factory=list)
    document_verification_list: List[Dict[str, Any]] = Field(default_factory=list)
    weather_contingency_plan: List[Dict[str, Any]] = Field(default_factory=list)
    activity_closure_plan: List[Dict[str, Any]] = Field(default_factory=list)
    pre_booking_confirmation_items: List[Dict[str, Any]] = Field(default_factory=list)
    generic_emergency_summary: Dict[str, Any] = Field(default_factory=dict)


def generate_contingency_dossier(trip: Trip) -> ContingencyDossier:
    """Generate comprehensive contingency plans and preparation checklists for a trip."""
    # 1. Pre-departure Checklist
    pre_dep = [
        {
            "id": "chk-prep-passport",
            "category": "documents",
            "title": "Vérifier la validité des passeports / CNI",
            "action": "S'assurer d'une validité d'au moins 3 à 6 mois après la date de retour prévue.",
            "deadline": "30 jours avant le départ",
            "mandatory": True,
            "verification_note": _OFFICIAL_NOTICE,
        },
        {
            "id": "chk-prep-insurance",
            "category": "insurance",
            "title": "Souscrire ou vérifier l'assurance voyage & rapatriement",
            "action": "Télécharger l'attestation d'assurance avec le numéro d'assistance 24/7 et plafond de couverture médicale.",
            "deadline": "15 jours avant le départ",
            "mandatory": True,
            "verification_note": _OFFICIAL_NOTICE,
        },
        {
            "id": "chk-prep-payments",
            "category": "finance",
            "title": "Prévenir la banque et vérifier les plafonds bancaires",
            "action": f"Activer les paiements à l'étranger sans frais et vérifier l'acceptation de la devise ({trip.currency}).",
            "deadline": "7 jours avant le départ",
            "mandatory": True,
            "verification_note": "Consulter votre espace bancaire en ligne.",
        },
        {
            "id": "chk-prep-connectivity",
            "category": "connectivity",
            "title": "Organiser la connectivité locale (eSIM / Forfait)",
            "action": "Vérifier l'itinérance data incluse ou commander une eSIM locale compatible avec le pays de destination.",
            "deadline": "3 jours avant le départ",
            "mandatory": False,
            "verification_note": "Consulter les offres opérateurs officiels.",
        },
        {
            "id": "chk-prep-offline-maps",
            "category": "navigation",
            "title": "Télécharger les cartes hors-ligne",
            "action": "Télécharger la zone géographique sur Google Maps / Organic Maps / OSM pour navigation sans réseau.",
            "deadline": "2 jours avant le départ",
            "mandatory": True,
            "verification_note": "Application locale sur smartphone.",
        },
        {
            "id": "chk-prep-gear",
            "category": "gear",
            "title": "Préparer l'équipement adapté au climat",
            "action": "Adapter la garde-robe aux prévisions météo (vêtements imperméables, chaussures de marche éprouvées).",
            "deadline": "48h avant le départ",
            "mandatory": False,
            "verification_note": "Vérifier le bulletin météo local.",
        },
    ]

    # Incorporate any explicit trip checklists
    for c in trip.checklists:
        pre_dep.append({
            "id": c.id,
            "category": c.category.value,
            "title": c.title,
            "action": c.description,
            "deadline": "Avant le départ",
            "mandatory": c.is_mandatory,
            "verification_note": c.official_reference_url or _OFFICIAL_NOTICE,
        })

    # 2. Booking Checklist
    booking_items: List[Dict[str, Any]] = []

    for tr in trip.transports:
        if tr.mode in (TransportMode.FLIGHT, TransportMode.TRAIN, TransportMode.CAR_RENTAL, TransportMode.FERRY):
            booking_items.append({
                "type": "transport",
                "title": f"Billet de transport : {tr.origin} -> {tr.destination} ({tr.mode.value})",
                "estimated_cost": tr.estimated_cost,
                "currency": tr.currency,
                "booking_url": tr.official_booking_url,
                "mandatory": True,
                "timing_advice": "Réserver au plus tôt pour garantir le créneau et limiter le surcoût.",
                "verification_level": tr.verification_level.value,
            })

    for acc in trip.accommodations:
        booking_items.append({
            "type": "accommodation",
            "title": f"Hébergement : {acc.name} ({acc.neighborhood})",
            "estimated_cost": acc.total_cost,
            "currency": acc.currency,
            "booking_url": acc.official_booking_url,
            "mandatory": True,
            "timing_advice": "Confirmer les conditions d'annulation gratuite et la taxe de séjour locale.",
            "verification_level": acc.verification_level.value,
        })

    for act in trip.activities:
        if act.advance_booking_required:
            booking_items.append({
                "type": "activity_ticket",
                "title": f"Billet horodaté : {act.title}",
                "estimated_cost": act.estimated_cost,
                "currency": act.currency,
                "booking_url": act.official_booking_url,
                "mandatory": True,
                "timing_advice": act.quiet_slot_advice or "Réservation anticipée obligatoire pour éviter de faire la queue ou d'être refusé.",
                "verification_level": act.verification_level.value,
            })

    for r in trip.reservations:
        booking_items.append({
            "type": f"reservation_{r.category}",
            "title": r.title,
            "estimated_cost": r.estimated_cost,
            "currency": r.currency,
            "booking_url": r.official_booking_url,
            "mandatory": r.mandatory,
            "timing_advice": r.action_required or "Effectuer la démarche sur le portail officiel.",
            "verification_level": r.verification_level.value,
        })

    # 3. Document Verification List
    dest_countries = ", ".join({d.country for d in trip.destinations if d.country}) or "Pays de destination"
    doc_list = [
        {
            "document": "Passeport ou Carte Nationale d'Identité",
            "requirement": f"Validité requise pour l'entrée dans {dest_countries} (généralement 3 à 6 mois post-séjour).",
            "rule": "Document original obligatoire, non détérioré. Faire des photocopies et sauvegardes numériques chiffrées.",
            "status": _OFFICIAL_NOTICE,
        },
        {
            "document": "Visa / Autorisation Électronique de Voyage (ETA / ESTA / ETIAS)",
            "requirement": f"Vérifier si votre nationalité est soumise à visa ou autorisation préalable pour {dest_countries}.",
            "rule": "Démarche à effectuer exclusivement sur les sites consulaires ou ministériels officiels (se méfier des intermédiaires surfacturés).",
            "status": _OFFICIAL_NOTICE,
        },
        {
            "document": "Carte Européenne d'Assurance Maladie (CEAM) ou Attestation Privée",
            "requirement": "Prise en charge des soins d'urgence lors d'un séjour en Europe ou couverture internationale.",
            "rule": "À commander au moins 3 semaines avant le départ auprès de votre caisse d'assurance maladie.",
            "status": _OFFICIAL_NOTICE,
        },
        {
            "document": "Permis de Conduire (National et/ou International)",
            "requirement": "Obligatoire si une location de véhicule ou conduite est prévue.",
            "rule": "Vérifier la nécessité du permis international selon le pays de destination et l'âge minimum requis par le loueur.",
            "status": _OFFICIAL_NOTICE,
        },
        {
            "document": "Vaccinations et exigences sanitaires",
            "requirement": f"Vérifier les recommandations de l'Institut Pasteur / OMS pour {dest_countries}.",
            "rule": "Vaccins universels à jour (DTP) et vaccins spécifiques éventuels.",
            "status": _OFFICIAL_NOTICE,
        },
    ]

    # 4. Weather Contingency Plan
    weather_plan: List[Dict[str, Any]] = []
    for day in trip.itinerary:
        outdoor_items = []
        for it in day.items:
            # find corresponding activity
            matching_act = next((a for a in trip.activities if a.id == it.reference_id or a.title == it.title), None)
            if matching_act and (matching_act.environment in (EnvironmentType.OUTDOOR, EnvironmentType.HYBRID) or not matching_act.indoor_contingency):
                outdoor_items.append({
                    "activity": matching_act.title,
                    "backup": matching_act.weather_alternative or day.weather_contingency_notes or "Visite d'un musée couvert ou marché local abrité",
                    "indoor_contingency": matching_act.indoor_contingency,
                })
        
        weather_plan.append({
            "day_number": day.day_number,
            "date": day.date,
            "theme": day.theme or f"Jour {day.day_number}",
            "general_contingency_notes": day.weather_contingency_notes or "Activité en intérieur ou repli culturel abrité recommandé en cas de pluie.",
            "outdoor_contingencies": outdoor_items,
        })

    # 5. Activity Closure Contingency Plan
    closure_plan: List[Dict[str, Any]] = []
    for act in trip.activities:
        closure_backup = act.closure_alternative or (
            f"Alternative à proximité : visiter un site culturel ou quartier voisin dans {act.neighborhood or 'la ville'}"
        )
        closure_plan.append({
            "activity_id": act.id,
            "activity_title": act.title,
            "category": act.category.value,
            "potential_trigger": "Fermeture hebdomadaire inattendue, jour férié local, grève ou jauge complète",
            "recommended_alternative": closure_backup,
            "action_advice": "Vérifier les horaires sur le site officiel le matin même avant le départ.",
            "official_url": act.official_booking_url,
        })

    # 6. Pre-Booking Confirmation Items (Things to verify before paying)
    pre_booking_confirmations = [
        {
            "category": "Hébergement",
            "item": "Conditions d'annulation et taxes de séjour",
            "checklist_point": "Vérifier la date limite d'annulation sans frais et si les taxes locales sont incluses ou payables sur place en espèces.",
            "risk_if_unconfirmed": "Frais non remboursables en cas d'imprévu ou surcoût inattendu au check-in.",
        },
        {
            "category": "Transport",
            "item": "Franchise bagages et gares/terminaux exacts",
            "checklist_point": "Vérifier le nombre et dimensions des bagages inclus (cabine vs soute) et identifier précisément la gare ou le terminal de départ/arrivée.",
            "risk_if_unconfirmed": "Surcoûts prohibitifs à l'aéroport ou retard lié à une confusion de terminal/gare.",
        },
        {
            "category": "Billetterie Activités",
            "item": "Créneaux horaires et politique de retard",
            "checklist_point": "Contrôler la tolérance d'entrée en cas de retard sur le billet coupe-file et les pièces d'identité demandées au contrôle.",
            "risk_if_unconfirmed": "Billet annulé sans remboursement en cas de retard de 15 minutes.",
        },
        {
            "category": "Location de Véhicule",
            "item": "Caution, carte de crédit vs débit, et état des lieux",
            "checklist_point": "S'assurer que la carte bancaire présentée au loueur est bien reconnue comme carte de CRÉDIT (mention inscrite sur la carte) avec un plafond suffisant pour la caution.",
            "risk_if_unconfirmed": "Refus de remise du véhicule au guichet par le loueur.",
        },
    ]

    # 7. Generic Emergency Summary (Zero fake hospitals or embassies)
    dest_name = trip.destinations[0].name if trip.destinations else "Destination"
    country_name = trip.destinations[0].country if trip.destinations else "Pays d'accueil"

    generic_emergency = {
        "destination": f"{dest_name} ({country_name})",
        "notice": _OFFICIAL_NOTICE,
        "emergency_dispatch_reminder": (
            f"Numéro d'appel d'urgence : {_OFFICIAL_NOTICE} "
            "(Rappels généraux : 112 dans l'Union Européenne, 911 en Amérique du Nord, 110/119 au Japon. "
            "Enregistrer le numéro officiel précis du pays d'accueil avant le voyage)."
        ),
        "consular_support_reminder": (
            f"Coordonnées de l'Ambassade / Consulat national : {_OFFICIAL_NOTICE} "
            "(S'inscrire sur le registre officiel des voyageurs de votre ministère des affaires étrangères — ex: Ariane en France, Smart Traveler aux USA — et noter l'adresse exacte du consulat le plus proche)."
        ),
        "medical_assistance_reminder": (
            f"Hôpital de référence et urgences médicales : {_OFFICIAL_NOTICE} "
            "(Appeler en priorité le numéro d'assistance 24/7 de votre assurance voyage, qui vous orientera vers un établissement hospitalier agréé conventionné sans avance de frais)."
        ),
        "lost_payment_cards_hotline": (
            "Numéro d'opposition carte bancaire : Noter le numéro d'opposition international de votre banque avant le départ (accessible 24h/24)."
        ),
        "incident_procedure": [
            "1. En cas d'urgence vitale : composer le numéro d'urgence local officiel.",
            "2. En cas de sinistre ou problème de santé : contacter l'assistance de votre assurance voyage.",
            "3. En cas de perte/vol de passeport : déposer plainte auprès de la police locale et contacter votre consulat avec les photocopies de vos documents.",
            "4. En cas de perte de carte : faire opposition immédiatement via votre application bancaire.",
        ],
        "zero_fabrication_guarantee": "Ce résumé ne fabrique aucun faux numéro de téléphone, clinique privée ou nom de diplomate. Toutes les démarches reposent sur les canaux officiels.",
    }

    return ContingencyDossier(
        trip_id=trip.id,
        trip_title=trip.title,
        pre_departure_checklist=pre_dep,
        booking_checklist=booking_items,
        document_verification_list=doc_list,
        weather_contingency_plan=weather_plan,
        activity_closure_plan=closure_plan,
        pre_booking_confirmation_items=pre_booking_confirmations,
        generic_emergency_summary=generic_emergency,
    )
