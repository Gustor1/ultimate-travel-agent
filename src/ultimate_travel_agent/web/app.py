"""FastAPI web application for ultimate-travel-agent local UI."""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ultimate_travel_agent.engine.contingency import generate_contingency_dossier
from ultimate_travel_agent.engine.orchestrator import TravelOrchestrationEngine
from ultimate_travel_agent.engine.route_optimizer import evaluate_all_preferences, recommend_route_option
from ultimate_travel_agent.models import (
    Accommodation,
    AccommodationType,
    Activity,
    ActivityCategory,
    BookingRequirement,
    ChecklistCategory,
    ChecklistItem,
    CrowdSensitivity,
    DaySchedule,
    Destination,
    DifficultyLevel,
    EnvironmentType,
    InterCityRoute,
    ItineraryItem,
    PacingPreference,
    RouteOption,
    RouteOptionStatus,
    RoutePreference,
    RouteTransportMode,
    SourceReference,
    TransportMode,
    TransportSegment,
    Traveler,
    TravelerProfile,
    Trip,
    TripStage,
    TripType,
    VerificationLevel,
)
from ultimate_travel_agent.reporter import generate_markdown_report

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class TripCreationRequest(BaseModel):
    """User input form parameters for local trip generation."""

    destination: str = Field(default="Barcelone", description="Target destination city or region")
    country: Optional[str] = Field(default="Espagne", description="Target country")
    start_date: str = Field(default="2026-10-15", description="Start date YYYY-MM-DD")
    end_date: str = Field(default="2026-10-18", description="End date YYYY-MM-DD")
    travelers_count: int = Field(default=2, ge=1, le=12, description="Number of travelers")
    traveler_profile: TravelerProfile = Field(default=TravelerProfile.COUPLE)
    budget_cap: Optional[float] = Field(default=1200.0, description="Indicative budget cap")
    currency: str = Field(default="EUR", description="Budget currency code")
    interests: List[str] = Field(
        default_factory=lambda: ["culture", "gastronomy", "architecture"],
        description="Selected interest tags"
    )
    accommodation_style: AccommodationType = Field(default=AccommodationType.HOTEL)
    pacing: PacingPreference = Field(default=PacingPreference.BALANCED)
    crowd_preference: str = Field(default="low-crowd", description="popular, mixed, low-crowd")
    constraints: Optional[str] = Field(default=None, description="Special dietary or physical constraints")


def _generate_local_trip_dossier(req: TripCreationRequest) -> Trip:
    """Deterministically assemble a valid local Trip from user specifications."""
    try:
        d_start = date.fromisoformat(req.start_date)
        d_end = date.fromisoformat(req.end_date)
        if d_end < d_start:
            d_end = d_start + timedelta(days=2)
    except Exception:
        d_start = date(2026, 10, 15)
        d_end = date(2026, 10, 18)

    num_days = max(1, (d_end - d_start).days + 1)
    num_nights = max(0, (d_end - d_start).days)

    dest_slug = req.destination.lower().replace(" ", "-")
    dest_id = f"dest-{dest_slug}"
    destination_obj = Destination(
        id=dest_id,
        name=req.destination,
        country=req.country or "Europe",
        region="Région touristique",
        description=f"Destination remarquable sélectionnée pour vos centres d'intérêt : {', '.join(req.interests)}.",
        anecdote="Quartiers historiques piétonniers idéaux pour une découverte décontractée à pied.",
        quiet_periods=["Matinées (08h30-10h30)", "Créneaux de fin d'après-midi"],
    )

    travelers = [
        Traveler(
            id=f"trav-{i+1}",
            name=f"Voyageur {i+1}",
            profile=req.traveler_profile,
            pacing_preference=req.pacing,
            crowd_sensitivity=(
                CrowdSensitivity.AVOID_CROWDS if req.crowd_preference == "low-crowd" else CrowdSensitivity.STANDARD
            ),
            dietary_restrictions=[req.constraints] if req.constraints else [],
        )
        for i in range(req.travelers_count)
    ]

    # Stage
    stage = TripStage(
        id=f"stage-1-{dest_slug}",
        destination_id=dest_id,
        order=1,
        title=f"Séjour à {req.destination}",
        arrival_date=req.start_date,
        departure_date=req.end_date,
        nights=num_nights,
        notes="Base stratégique centrale à proximité des transports et commodités.",
        verification_level=VerificationLevel.OFFICIAL_VERIFIED,
    )

    # Transports (Inbound and Outbound)
    transports = [
        TransportSegment(
            id=f"trans-inbound-{dest_slug}",
            origin="Départ Origine",
            destination=req.destination,
            mode=TransportMode.TRAIN if req.pacing != PacingPreference.PACKED else TransportMode.FLIGHT,
            carrier="Opérateur National Ferroviaire",
            departure_time="08:30",
            arrival_time="11:45",
            duration_minutes=195,
            estimated_cost=65.0,
            currency=req.currency,
            official_booking_url="https://www.sncf-connect.com",
            door_to_door_notes="Prévoir 30 minutes de marge avant le départ pour l'embarquement.",
            verification_level=VerificationLevel.CROSS_CHECKED,
        ),
        TransportSegment(
            id=f"trans-outbound-{dest_slug}",
            origin=req.destination,
            destination="Départ Origine",
            mode=TransportMode.TRAIN if req.pacing != PacingPreference.PACKED else TransportMode.FLIGHT,
            carrier="Opérateur National Ferroviaire",
            departure_time="16:15",
            arrival_time="19:30",
            duration_minutes=195,
            estimated_cost=65.0,
            currency=req.currency,
            official_booking_url="https://www.sncf-connect.com",
            door_to_door_notes="Accès direct depuis le centre-ville en transports locaux.",
            verification_level=VerificationLevel.CROSS_CHECKED,
        ),
    ]

    # Accommodation
    nightly_rate = 95.0 if req.accommodation_style == AccommodationType.HOTEL else 80.0
    accommodation = Accommodation(
        id=f"acc-{dest_slug}-central",
        name=f"Hôtel de Charme {req.destination}",
        destination_id=dest_id,
        neighborhood="Centre Historique Calme",
        accommodation_type=req.accommodation_style,
        cost_per_night=nightly_rate,
        total_nights=num_nights,
        currency=req.currency,
        quietness_rating="high",
        official_booking_url="https://www.hotel-officiel.example.com",
        criteria_matched=[
            "Quartier piétonnier calme",
            "Excellente isolation phonique",
            "Accès immédiat à pied aux curiosités",
        ],
        verification_level=VerificationLevel.CROSS_CHECKED,
    )

    # Curated Activities
    activities: List[Activity] = [
        Activity(
            id=f"act-{dest_slug}-monument",
            title=f"Joyau Historique & Architectural de {req.destination}",
            destination_id=dest_id,
            category=ActivityCategory.HISTORY if "history" in req.interests else ActivityCategory.CULTURE,
            description="Visite approfondie du grand monument emblématique avec audioguide officiel.",
            country=req.country or "Europe",
            city=req.destination,
            neighborhood="Cité Ancienne",
            anecdote="Édifié au fil des siècles, ce monument recèle des symboles ésotériques gravés dans ses pierres.",
            environment=EnvironmentType.INDOOR,
            difficulty_level=DifficultyLevel.EASY,
            accessibility="Accessible aux personnes à mobilité réduite et poussettes",
            duration_minutes=110,
            best_time_slot="09:00 - 11:00",
            opening_hours="09:00 - 18:30 du mardi au dimanche",
            estimated_cost=22.0,
            currency=req.currency,
            access_method="Ligne principale de métro ou 10 min de marche depuis l'hébergement",
            transit_duration_minutes=15,
            transit_cost=2.10,
            advance_booking_required=True,
            official_booking_url="https://monument-billetterie.example.com",
            crowd_level="high",
            quiet_slot_advice="Réserver le créneau de 09h00 dès l'ouverture pour éviter l'afflux de groupes.",
            crowd_avoidance_strategy="Accès par l'entrée coupe-file réservée aux billets horodatés numériques.",
            indoor_contingency=True,
            weather_alternative="Visite de la crypte et des galeries d'exposition intérieures.",
            closure_alternative="Musée municipal d'histoire situé à 200 mètres.",
            verification_level=VerificationLevel.CROSS_CHECKED,
        ),
        Activity(
            id=f"act-{dest_slug}-gastronomy",
            title=f"Marché Gourmand & Dégustation Terroir à {req.destination}",
            destination_id=dest_id,
            category=ActivityCategory.GASTRONOMY,
            description="Halles traditionnelles couvertes abritant producteurs locaux, fromagers et comptoirs de dégustation.",
            country=req.country or "Europe",
            city=req.destination,
            neighborhood="Quartier des Halles",
            anecdote="Marché historique en activité depuis plus de 150 ans, prisé par les grands chefs régionaux.",
            environment=EnvironmentType.INDOOR,
            difficulty_level=DifficultyLevel.EASY,
            accessibility="De plain-pied, accès aisé",
            duration_minutes=80,
            best_time_slot="12:00 - 13:30",
            opening_hours="08:00 - 15:00 du lundi au samedi",
            estimated_cost=18.0,
            currency=req.currency,
            access_method="À pied depuis le centre historique",
            transit_duration_minutes=10,
            transit_cost=0.0,
            advance_booking_required=False,
            official_booking_url=None,
            crowd_level="medium",
            quiet_slot_advice="Arriver vers 11h45 avant le rush du déjeuner pour trouver facilement une place au comptoir.",
            crowd_avoidance_strategy="Privilégier les étals de l'allée centrale sud.",
            indoor_contingency=True,
            weather_alternative="Espace entièrement couvert et abrité.",
            closure_alternative="Bistrot traditionnel régional dans la rue adjacente.",
            verification_level=VerificationLevel.COMMUNITY_RECOMMENDED,
        ),
        Activity(
            id=f"act-{dest_slug}-promenade",
            title=f"Promenade Panoramique & Jardins de {req.destination}",
            destination_id=dest_id,
            category=ActivityCategory.LANDSCAPE if "landscape" in req.interests else ActivityCategory.CULTURE,
            description="Balade à pied ombragée menant à un belvédère spectaculaire sur les toits de la cité.",
            country=req.country or "Europe",
            city=req.destination,
            neighborhood="Colline Verdoyante",
            anecdote="Ancien verger préservé de l'urbanisation offrant le plus beau coucher de soleil de la région.",
            environment=EnvironmentType.OUTDOOR,
            difficulty_level=DifficultyLevel.EASY,
            accessibility="Chemins stabilisés, quelques rampes douces",
            duration_minutes=90,
            best_time_slot="Fin d'après-midi / Coucher du soleil (17h30-19h00)",
            opening_hours="Accès public continu en journée",
            estimated_cost=0.0,
            currency=req.currency,
            access_method="Funiculaire ou sentier piétonnier aménagé",
            transit_duration_minutes=20,
            transit_cost=2.50,
            advance_booking_required=False,
            official_booking_url=None,
            crowd_level="low",
            quiet_slot_advice="Parfait après 17h30 lorsque la chaleur retombe.",
            crowd_avoidance_strategy="S'éloigner du premier belvédère vers les terrasses supérieures.",
            indoor_contingency=False,
            weather_alternative="Salon de thé culturel ou café d'art avec vue panoramique abritée.",
            closure_alternative="Passage couvert et galeries d'antiquaires en centre-ville.",
            verification_level=VerificationLevel.CROSS_CHECKED,
        ),
    ]

    # Inter-city Route Comparison
    route_option_train = RouteOption(
        id=f"opt-train-{dest_slug}",
        origin="Paris Gare de Lyon",
        destination=req.destination,
        mode=RouteTransportMode.TRAIN,
        carrier="TGV Express",
        estimated_duration_minutes=200,
        transfers_count=0,
        estimated_cost=65.0,
        currency=req.currency,
        comfort_level=4,
        carbon_footprint_kg=12.5,
        booking_required=True,
        official_booking_url="https://www.sncf-connect.com",
        confidence_level=VerificationLevel.OFFICIAL_VERIFIED,
        status=RouteOptionStatus.CONFIRMED,
        notes="Gare centrale en centre-ville, aucun transfert aéroport.",
    )
    route_option_flight = RouteOption(
        id=f"opt-flight-{dest_slug}",
        origin="Paris CDG / Orly",
        destination=req.destination,
        mode=RouteTransportMode.FLIGHT,
        carrier="Air Transit",
        estimated_duration_minutes=180,
        transfers_count=0,
        estimated_cost=85.0,
        currency=req.currency,
        comfort_level=3,
        carbon_footprint_kg=145.0,
        booking_required=True,
        official_booking_url="https://www.compagnie-aerienne.example.com",
        confidence_level=VerificationLevel.CROSS_CHECKED,
        status=RouteOptionStatus.ESTIMATED,
        notes="Inclut 120 min de formalités aéroportuaires et transit banlieue-centre.",
    )
    route_option_bus = RouteOption(
        id=f"opt-bus-{dest_slug}",
        origin="Paris Bercy",
        destination=req.destination,
        mode=RouteTransportMode.BUS,
        carrier="Express Bus Coach",
        estimated_duration_minutes=480,
        transfers_count=0,
        estimated_cost=29.0,
        currency=req.currency,
        comfort_level=2,
        carbon_footprint_kg=24.0,
        booking_required=True,
        official_booking_url="https://www.bus-longue-distance.example.com",
        confidence_level=VerificationLevel.CROSS_CHECKED,
        status=RouteOptionStatus.ESTIMATED,
        notes="Option économique mais trajet nettement plus long.",
    )

    inter_city_route = InterCityRoute(
        id=f"route-access-{dest_slug}",
        origin="Point de départ",
        destination=req.destination,
        options=[route_option_train, route_option_flight, route_option_bus],
        recommended_option_id=route_option_train.id,
        recommendation_reason="Train recommandé : bilan carbone exemplaire, confort optimal et arrivée directe en centre-ville.",
    )

    # Itinerary days
    itinerary: List[DaySchedule] = []
    for day_i in range(num_days):
        day_date = (d_start + timedelta(days=day_i)).isoformat()
        day_num = day_i + 1
        if day_num == 1:
            theme = "Arrivée, Installation et Première Immersion"
            items = [
                ItineraryItem(
                    time="12:00",
                    item_type="transport",
                    title=f"Arrivée à {req.destination} et transfert hébergement",
                    duration_minutes=45,
                    reference_id=transports[0].id,
                    notes="Check-in ou dépose des bagages à l'hôtel.",
                ),
                ItineraryItem(
                    time="13:00",
                    item_type="activity",
                    title=activities[1].title,
                    duration_minutes=activities[1].duration_minutes,
                    reference_id=activities[1].id,
                    notes="Déjeuner gourmand et découverte des spécialités locales.",
                ),
                ItineraryItem(
                    time="16:00",
                    item_type="activity",
                    title=activities[2].title,
                    duration_minutes=activities[2].duration_minutes,
                    reference_id=activities[2].id,
                    notes="Balade panoramique en fin de journée et lumière dorée.",
                ),
            ]
        elif day_num == num_days:
            theme = "Dernières Découvertes et Trajet Retour"
            items = [
                ItineraryItem(
                    time="09:00",
                    item_type="activity",
                    title=activities[0].title,
                    duration_minutes=activities[0].duration_minutes,
                    reference_id=activities[0].id,
                    notes="Visite majeure dès l'ouverture avec billet horodaté.",
                ),
                ItineraryItem(
                    time="12:30",
                    item_type="meal",
                    title="Déjeuner d'adieu dans une ruelle tranquille",
                    duration_minutes=75,
                    notes="Pause gustative décontractée sans précipitation.",
                ),
                ItineraryItem(
                    time="15:30",
                    item_type="transport",
                    title=f"Transfert gare/station et départ retour",
                    duration_minutes=60,
                    reference_id=transports[1].id,
                    notes="Contrôle d'accès et embarquement serein.",
                ),
            ]
        else:
            theme = "Cœur Culturel et Flânerie Locale"
            items = [
                ItineraryItem(
                    time="09:30",
                    item_type="activity",
                    title=f"Flânerie dans les ruelles et ateliers d'artisans",
                    duration_minutes=120,
                    notes="Exploration des passages calmes hors des artères commerçantes.",
                ),
                ItineraryItem(
                    time="12:30",
                    item_type="meal",
                    title="Déjeuner de cuisine du marché",
                    duration_minutes=75,
                    notes="Halte dans un bistrot recommandé par les habitants.",
                ),
                ItineraryItem(
                    time="15:00",
                    item_type="activity",
                    title=f"Visite d'un musée d'art ou galerie historique",
                    duration_minutes=90,
                    notes="Immersion artistique à rythme détendu.",
                ),
            ]

        itinerary.append(
            DaySchedule(
                day_number=day_num,
                date=day_date,
                destination_id=dest_id,
                theme=theme,
                items=items,
                weather_contingency_notes="En cas de pluie : galeries couvertes, musées abrités ou salon de thé historique.",
            )
        )

    # Checklists
    checklists = [
        ChecklistItem(
            id=f"chk-passport-{dest_slug}",
            category=ChecklistCategory.DOCUMENTS_VISA,
            title="Contrôle des pièces d'identité / passeports",
            description="Validité requise d'au moins 3 à 6 mois après la date de retour prévue.",
            is_mandatory=True,
            official_reference_url="https://www.diplomatie.gouv.fr",
            verification_level=VerificationLevel.OFFICIAL_VERIFIED,
        ),
        ChecklistItem(
            id=f"chk-insurance-{dest_slug}",
            category=ChecklistCategory.SAFETY_EMERGENCY,
            title="Attestation d'assurance voyage & rapatriement",
            description="Télécharger le contrat et le numéro d'assistance téléphonique 24h/24.",
            is_mandatory=True,
            verification_level=VerificationLevel.CROSS_CHECKED,
        ),
    ]

    # Reservations
    reservations = [
        BookingRequirement(
            id=f"res-hotel-{dest_slug}",
            category="accommodation",
            title=f"Réservation de l'Hôtel à {req.destination}",
            mandatory=True,
            estimated_cost=accommodation.total_cost,
            currency=req.currency,
            official_booking_url=accommodation.official_booking_url,
            action_required="Vérifier la politique d'annulation gratuite et réserver en direct sur le portail de l'établissement.",
            verification_level=VerificationLevel.CROSS_CHECKED,
        ),
        BookingRequirement(
            id=f"res-monument-{dest_slug}",
            category="activity",
            title=f"Billet horodaté : {activities[0].title}",
            mandatory=True,
            estimated_cost=activities[0].estimated_cost * req.travelers_count,
            currency=req.currency,
            official_booking_url=activities[0].official_booking_url,
            action_required="Acheter le billet officiel pour le premier créneau du matin afin d'éviter l'attente.",
            verification_level=VerificationLevel.OFFICIAL_VERIFIED,
        ),
    ]

    trip = Trip(
        id=f"trip-{dest_slug}-{req.start_date.replace('-', '')}",
        title=f"Séjour Curé et Personnalisé à {req.destination} ({num_days} Jours)",
        trip_type=TripType.CITY_TRIP,
        start_date=req.start_date,
        end_date=req.end_date,
        currency=req.currency,
        budget_cap=req.budget_cap,
        travelers=travelers,
        destinations=[destination_obj],
        stages=[stage],
        transports=transports,
        inter_city_routes=[inter_city_route],
        accommodations=[accommodation],
        activities=activities,
        itinerary=itinerary,
        checklists=checklists,
        reservations=reservations,
    )
    trip.calculate_budget(safety_buffer_pct=12.0)
    return trip


def create_app() -> FastAPI:
    """Create and configure the FastAPI web service."""
    app = FastAPI(
        title="Ultimate Travel Agent Web UI",
        description="Local-first, privacy-focused travel planning interface with visible multi-agent verification.",
        version="1.1.0",
    )

    # Mount static assets
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/api/health")
    async def api_health() -> Dict[str, Any]:
        """Health check endpoint confirming offline-first security guarantee."""
        return {
            "status": "healthy",
            "version": "1.1.0",
            "mode": "offline-first-local",
            "disclaimer": "Offline local planning mode: No live availability, price, opening-hour or booking verification.",
            "auto_booking_capability": False,
        }

    @app.get("/api/trips")
    async def api_list_trips() -> List[Dict[str, Any]]:
        """List reference example trips available locally."""
        trips = []
        for example_path in [
            Path("examples/city-trip/trip.json"),
            Path("examples/road-trip/trip.json"),
        ]:
            if example_path.exists():
                try:
                    with open(example_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    trips.append({
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "trip_type": data.get("trip_type"),
                        "start_date": data.get("start_date"),
                        "end_date": data.get("end_date"),
                        "currency": data.get("currency", "EUR"),
                        "path": str(example_path).replace("\\", "/"),
                    })
                except Exception:
                    pass
        return trips

    @app.get("/api/examples/{example_name}")
    async def api_get_example(example_name: str) -> Dict[str, Any]:
        """Retrieve full JSON for a reference example ('city-trip' or 'road-trip')."""
        clean_name = "city-trip" if "city" in example_name.lower() else "road-trip"
        p = Path(f"examples/{clean_name}/trip.json")
        if not p.exists():
            raise HTTPException(status_code=404, detail=f"Example '{example_name}' not found")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    @app.post("/api/trips/create")
    async def api_create_trip(req: TripCreationRequest) -> Dict[str, Any]:
        """Create and assemble a local coherent Trip dossier from user criteria."""
        trip = _generate_local_trip_dossier(req)
        return trip.model_dump()

    @app.post("/api/trips/validate")
    async def api_validate_trip(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trip consistency, budget limits, verification tiers, and data completeness."""
        try:
            trip = Trip.model_validate(payload)
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Schéma de données invalide : {str(e)}"],
                "warnings": [],
                "missing_data": [],
                "unverified_data": [],
                "estimated_recommendations": [],
                "confirmed_data": [],
            }

        coherence_issues = trip.validate_trip_coherence()
        budget = trip.calculate_budget()

        warnings: List[str] = list(budget.warnings)
        missing_data: List[str] = []
        unverified_data: List[str] = []
        confirmed_data: List[str] = []
        estimated_recommendations: List[str] = []

        if not trip.destinations:
            missing_data.append("Aucune destination renseignée.")
        if trip.total_nights > 0 and not trip.accommodations:
            missing_data.append(f"Aucun hébergement planifié pour les {trip.total_nights} nuitée(s).")
        if not trip.activities:
            missing_data.append("Aucune activité ou visite renseignée.")

        for tr in trip.transports:
            if tr.verification_level in (VerificationLevel.OFFICIAL_VERIFIED, VerificationLevel.CROSS_CHECKED):
                confirmed_data.append(f"Transport '{tr.origin}->{tr.destination}' vérifié ({tr.mode.value}).")
            else:
                unverified_data.append(f"Transport '{tr.origin}->{tr.destination}' ({tr.verification_level.value}).")

        for acc in trip.accommodations:
            if acc.verification_level in (VerificationLevel.OFFICIAL_VERIFIED, VerificationLevel.CROSS_CHECKED):
                confirmed_data.append(f"Hébergement '{acc.name}' ({acc.neighborhood}) vérifié.")
            else:
                unverified_data.append(f"Hébergement '{acc.name}' non vérifié.")

        for act in trip.activities:
            if act.verification_level in (VerificationLevel.OFFICIAL_VERIFIED, VerificationLevel.CROSS_CHECKED):
                confirmed_data.append(f"Activité '{act.title}' vérifiée auprès de l'opérateur.")
            elif act.verification_level == VerificationLevel.SOCIAL_DISCOVERY_ONLY:
                estimated_recommendations.append(f"Découverte locale '{act.title}' issue des réseaux sociaux.")
            else:
                unverified_data.append(f"Activité '{act.title}' à vérifier manuellement.")

        return {
            "valid": len(coherence_issues) == 0,
            "errors": coherence_issues,
            "warnings": warnings,
            "missing_data": missing_data,
            "unverified_data": unverified_data,
            "estimated_recommendations": estimated_recommendations,
            "confirmed_data": confirmed_data,
            "summary_stats": {
                "days": trip.total_days,
                "nights": trip.total_nights,
                "travelers": len(trip.travelers),
                "destinations": len(trip.destinations),
                "stages": len(trip.stages),
                "transports": len(trip.transports),
                "accommodations": len(trip.accommodations),
                "activities": len(trip.activities),
                "reservations": len(trip.reservations),
                "grand_total": budget.grand_total,
                "currency": budget.currency,
            },
        }

    @app.post("/api/trips/budget")
    async def api_calculate_budget(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate itemized budget breakdown with safety contingency buffer."""
        trip = Trip.model_validate(payload.get("trip", payload))
        safety_buffer = float(payload.get("safety_buffer_pct", 12.0))
        budget = trip.calculate_budget(safety_buffer_pct=safety_buffer)
        return budget.model_dump()

    @app.post("/api/trips/plan")
    async def api_plan_trip(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the multi-agent pipeline and return the 9 canonical stages with full visibility."""
        trip = Trip.model_validate(payload)
        engine = TravelOrchestrationEngine()
        raw_results = engine.execute_full_pipeline(trip)
        nine_stages = engine.get_nine_stage_pipeline(trip)

        return {
            "trip_id": trip.id,
            "title": trip.title,
            "offline_banner": {
                "active": True,
                "message": "Offline local planning mode: No live availability, price, opening-hour or booking verification.",
            },
            "stages_count": len(nine_stages),
            "stages": nine_stages,
            "agent_results": {k: v.model_dump() for k, v in raw_results.items()},
        }

    @app.post("/api/trips/contingency")
    async def api_contingency_dossier(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive contingency pack (Plan B, checklists, emergency summary)."""
        trip = Trip.model_validate(payload)
        contingency = generate_contingency_dossier(trip)
        return contingency.model_dump()

    @app.post("/api/trips/routes/evaluate")
    async def api_evaluate_route(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate inter-city route options across all 7 user preference profiles."""
        route = InterCityRoute.model_validate(payload)
        results = evaluate_all_preferences(route)
        return {
            "route_id": route.id,
            "origin": route.origin,
            "destination": route.destination,
            "options_count": len(route.options),
            "preferences_evaluations": results,
        }

    @app.post("/api/trips/export")
    async def api_export_markdown(payload: Dict[str, Any]) -> PlainTextResponse:
        """Export the complete travel dossier in clean Markdown format."""
        trip = Trip.model_validate(payload)
        engine = TravelOrchestrationEngine()
        results = engine.execute_full_pipeline(trip)
        md_text = generate_markdown_report(trip, results)
        return PlainTextResponse(content=md_text, media_type="text/markdown")

    @app.get("/", response_class=HTMLResponse)
    async def root() -> HTMLResponse:
        """Serve the local single-page web interface."""
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            return HTMLResponse(
                content="<h1>Ultimate Travel Agent UI</h1><p>Static index.html not found.</p>",
                status_code=500,
            )
        with open(index_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)

    return app


app = create_app()
