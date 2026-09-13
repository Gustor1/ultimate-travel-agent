"""Core tool implementations for the local MCP server."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.engine.orchestrator import TravelOrchestrationEngine
from ultimate_travel_agent.models import Trip
from ultimate_travel_agent.reporter import generate_markdown_report


def _resolve_trip(trip_path: str) -> Trip:
    """Helper to resolve and load a Trip from a file path."""
    p = Path(trip_path)
    if not p.exists():
        raise FileNotFoundError(f"Trip file not found: {trip_path}")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Trip.model_validate(data)


def list_trips(directory: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all available trips in the workspace or specified directory.

    Args:
        directory: Optional directory path to search. Defaults to 'examples' and 'data/examples'.

    Returns:
        List of summarized trip records.
    """
    search_dirs = [Path(directory)] if directory else [Path("examples"), Path("data/examples")]
    results: List[Dict[str, Any]] = []
    seen_ids = set()

    for base_dir in search_dirs:
        if not base_dir.exists():
            continue
        for file_path in base_dir.glob("**/*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "trip_type" in data and "start_date" in data:
                    trip_id = data.get("id", str(file_path))
                    if trip_id not in seen_ids:
                        seen_ids.add(trip_id)
                        results.append({
                            "id": trip_id,
                            "title": data.get("title", "Untitled Trip"),
                            "trip_type": data.get("trip_type"),
                            "start_date": data.get("start_date"),
                            "end_date": data.get("end_date"),
                            "currency": data.get("currency", "EUR"),
                            "file_path": str(file_path).replace("\\", "/"),
                        })
            except Exception:
                continue

    return results


def get_trip(trip_path: str) -> Dict[str, Any]:
    """Retrieve full details of a specific trip.

    Args:
        trip_path: Path to the trip JSON file.

    Returns:
        Complete trip data dictionary.
    """
    trip = _resolve_trip(trip_path)
    return trip.model_dump()


def validate_trip(trip_path: str) -> Dict[str, Any]:
    """Validate schema conformance and internal coherence of a trip.

    Args:
        trip_path: Path to the trip JSON file.

    Returns:
        Validation outcome and detected coherence issues.
    """
    trip = _resolve_trip(trip_path)
    issues = trip.validate_trip_coherence()
    budget = trip.calculate_budget()

    unverified_count = (
        sum(1 for t in trip.transports if t.verification_level.value in ("unverified", "outdated", "social_discovery_only"))
        + sum(1 for a in trip.accommodations if a.verification_level.value in ("unverified", "outdated"))
        + sum(1 for act in trip.activities if act.verification_level.value in ("unverified", "outdated", "social_discovery_only"))
    )

    return {
        "valid": len(issues) == 0,
        "trip_id": trip.id,
        "title": trip.title,
        "total_days": trip.total_days,
        "total_nights": trip.total_nights,
        "coherence_issues": issues,
        "budget_warnings": budget.warnings,
        "unverified_items_count": unverified_count,
        "stages_count": len(trip.stages),
        "reservations_count": len(trip.reservations),
    }


def get_itinerary(trip_path: str) -> List[Dict[str, Any]]:
    """Retrieve the day-by-day chronological itinerary for a trip.

    Args:
        trip_path: Path to the trip JSON file.

    Returns:
        List of day schedules with timeline events.
    """
    trip = _resolve_trip(trip_path)
    return [d.model_dump() for d in trip.itinerary]


def validate_itinerary(trip_path: str) -> Dict[str, Any]:
    """Validate schedule continuity, day count, and weather contingencies.

    Args:
        trip_path: Path to the trip JSON file.

    Returns:
        Itinerary validation summary.
    """
    trip = _resolve_trip(trip_path)
    issues: List[str] = []

    if not trip.itinerary:
        issues.append("Itinerary is completely empty.")
    elif trip.total_days > 0 and len(trip.itinerary) != trip.total_days:
        issues.append(
            f"Itinerary day count ({len(trip.itinerary)}) does not match trip calendar duration ({trip.total_days} days)."
        )

    expected_day = 1
    dest_ids = {d.id for d in trip.destinations}
    for day in trip.itinerary:
        if day.day_number != expected_day:
            issues.append(f"Day number sequence break: expected {expected_day}, got {day.day_number}")
        expected_day += 1
        if day.destination_id not in dest_ids:
            issues.append(f"Day {day.day_number} references unknown destination '{day.destination_id}'")

    days_with_missing_weather_backup = [
        d.day_number for d in trip.itinerary if not d.weather_contingency_notes
    ]

    return {
        "valid": len(issues) == 0,
        "trip_id": trip.id,
        "total_days_scheduled": len(trip.itinerary),
        "expected_calendar_days": trip.total_days,
        "days_without_weather_backup": days_with_missing_weather_backup,
        "issues": issues,
    }


def calculate_budget(trip_path: str, safety_buffer_pct: float = 12.0) -> Dict[str, Any]:
    """Calculate itemized budget with a safety reserve buffer.

    Args:
        trip_path: Path to the trip JSON file.
        safety_buffer_pct: Safety contingency percentage (default 12.0%).

    Returns:
        Itemized budget breakdown and warnings.
    """
    trip = _resolve_trip(trip_path)
    budget = trip.calculate_budget(safety_buffer_pct=safety_buffer_pct)
    return budget.model_dump()


def list_booking_requirements(trip_path: str) -> List[Dict[str, Any]]:
    """List all reservations, tickets, and formal requirements requiring human booking.

    Note: This system NEVER performs automated purchases. All links are direct official portals.

    Args:
        trip_path: Path to the trip JSON file.

    Returns:
        List of items requiring user reservation or preparation.
    """
    trip = _resolve_trip(trip_path)
    requirements: List[Dict[str, Any]] = []

    # 1. Explicit modeled reservations
    for r in trip.reservations:
        requirements.append({
            "type": f"reservation_{r.category}",
            "title": r.title,
            "estimated_cost": r.estimated_cost,
            "currency": r.currency,
            "official_url": r.official_booking_url,
            "verification_level": r.verification_level.value,
            "mandatory": r.mandatory,
            "action": r.action_required or "Manual booking on official portal required",
        })

    # 2. Accommodations
    for acc in trip.accommodations:
        requirements.append({
            "type": "accommodation",
            "title": f"Book stay: {acc.name} ({acc.total_nights} night(s))",
            "estimated_cost": acc.total_cost,
            "currency": acc.currency,
            "official_url": acc.official_booking_url,
            "verification_level": acc.verification_level.value,
            "mandatory": True,
            "action": "Manual booking required by traveler on hotel portal",
        })

    # 3. Transports requiring booking
    for tr in trip.transports:
        if tr.mode.value in ["flight", "train", "car_rental", "ferry"]:
            requirements.append({
                "type": "transport",
                "title": f"Book transit: {tr.origin} -> {tr.destination} ({tr.mode.value})",
                "estimated_cost": tr.estimated_cost,
                "currency": tr.currency,
                "official_url": tr.official_booking_url,
                "verification_level": tr.verification_level.value,
                "mandatory": True,
                "action": "Purchase ticket on official carrier portal",
            })

    # 4. Activities requiring advance booking
    for act in trip.activities:
        if act.advance_booking_required:
            requirements.append({
                "type": "activity_advance_ticket",
                "title": f"Advance ticket: {act.title}",
                "estimated_cost": act.estimated_cost,
                "currency": act.currency,
                "official_url": act.official_booking_url,
                "verification_level": act.verification_level.value,
                "mandatory": True,
                "action": "Book timed entry ticket in advance",
            })

    # 5. Mandatory checklists
    for chk in trip.checklists:
        if chk.is_mandatory:
            requirements.append({
                "type": "checklist_item",
                "title": chk.title,
                "estimated_cost": 0.0,
                "currency": trip.currency,
                "official_url": chk.official_reference_url,
                "verification_level": chk.verification_level.value,
                "mandatory": True,
                "action": chk.description,
            })

    return requirements


def export_trip_summary(trip_path: str, format: str = "markdown") -> str:
    """Export the complete multi-agent trip dossier in Markdown or JSON format.

    Args:
        trip_path: Path to the trip JSON file.
        format: Export format ('markdown' or 'json').

    Returns:
        Formatted summary content.
    """
    trip = _resolve_trip(trip_path)
    engine = TravelOrchestrationEngine()
    results = engine.execute_full_pipeline(trip)

    if format.lower() == "json":
        return json.dumps({
            "trip": trip.model_dump(),
            "agent_results": {k: v.model_dump() for k, v in results.items()}
        }, indent=2, ensure_ascii=False)

    return generate_markdown_report(trip, results)


def get_inter_city_routes(trip_path: str) -> List[Dict[str, Any]]:
    """Retrieve inter-city transit options and evaluations for a trip.

    Args:
        trip_path: Path to the trip JSON file.

    Returns:
        List of inter-city routes with multi-option details.
    """
    trip = _resolve_trip(trip_path)
    return [r.model_dump() for r in trip.inter_city_routes]


def get_contingency_dossier(trip_path: str) -> Dict[str, Any]:
    """Generate comprehensive contingency pack (Plan B, checklists, emergency summary).

    Args:
        trip_path: Path to the trip JSON file.

    Returns:
        Contingency dossier dictionary.
    """
    from ultimate_travel_agent.engine.contingency import generate_contingency_dossier
    trip = _resolve_trip(trip_path)
    dossier = generate_contingency_dossier(trip)
    return dossier.model_dump()


# ===========================================================================
# Phase 8: Travel Integration & Provider Hub MCP Tools
# ===========================================================================

def list_integration_providers(
    category: Optional[str] = None,
    mode: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List all registered travel integration providers and their capabilities.

    Args:
        category: Optional category filter (flight, train, hotel, activity, review, map, weather, currency, guide, social).
        mode: Optional mode filter (offline, mock, live).

    Returns:
        List of provider metadata descriptions.
    """
    from ultimate_travel_agent.integrations import default_registry
    return default_registry.list_providers(category=category, mode=mode)


def get_provider_status(provider_name: str) -> Dict[str, Any]:
    """Check health, configuration, and credentials readiness for a specific provider.

    Args:
        provider_name: Identifier of the provider (e.g. 'amadeus_flight', 'mock_weather', 'sncf_train').

    Returns:
        Structured health check result.
    """
    from ultimate_travel_agent.integrations import default_registry
    try:
        res = default_registry.get_provider_status(provider_name)
        return res.model_dump()
    except KeyError as err:
        return {
            "status": "error",
            "error_type": "ProviderNotFound",
            "error": str(err),
            "provider": provider_name,
        }


def search_flight_options(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    max_budget: Optional[float] = None,
    currency: str = "EUR",
    sort_by: str = "price",
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search flight offers with fare estimation, duration, and official ticketing links.

    STRICT SAFETY: Read-only search. Never performs automatic booking or payments.

    Args:
        origin: IATA code or city name (e.g. 'PAR', 'CDG', 'Paris').
        destination: IATA code or city name (e.g. 'BCN', 'Barcelona').
        departure_date: Date string (YYYY-MM-DD).
        return_date: Optional return date string (YYYY-MM-DD).
        passengers: Number of passengers (>= 1).
        max_budget: Optional maximum total budget threshold.
        currency: Currency code (default 'EUR').
        sort_by: 'price', 'duration', 'stops', or 'comfort'.
        provider: Optional target provider name (e.g. 'amadeus_flight', 'aviation_edge', 'mock_flight').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized ProviderSearchResult with verified or estimated flight items.
    """
    if passengers < 1:
        return {"status": "error", "error": "Passengers count must be >= 1."}

    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.FLIGHT,
            provider_name=provider,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            max_budget=max_budget,
            currency=currency,
            sort_by=sort_by,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "flight",
            "mode": mode,
            "requires_booking_verification": True,
        }


def search_train_options(
    origin: str,
    destination: str,
    date: str,
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search rail connections with door-to-door transit time, transfers, and official booking portals.

    STRICT SAFETY: Never executes automated ticketing.

    Args:
        origin: Departure station or city name.
        destination: Arrival station or city name.
        date: Travel date (YYYY-MM-DD).
        provider: Optional target provider name (e.g. 'sncf_train', 'navitia_train', 'mock_train').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized rail search result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.TRAIN,
            provider_name=provider,
            origin=origin,
            destination=destination,
            date=date,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "train",
            "mode": mode,
            "requires_booking_verification": True,
        }


def search_accommodation_options(
    city: str,
    checkin_date: str,
    checkout_date: str,
    neighborhood: Optional[str] = None,
    guests: int = 2,
    max_price_per_night: Optional[float] = None,
    currency: str = "EUR",
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Curate accommodations in strategic, quiet neighborhoods with price estimates.

    STRICT SAFETY: Read-only search; zero automated booking or payment handling.

    Args:
        city: Destination city name.
        checkin_date: Check-in date (YYYY-MM-DD).
        checkout_date: Check-out date (YYYY-MM-DD).
        neighborhood: Optional desired district or quarter (e.g. 'Gràcia').
        guests: Number of guests (default 2).
        max_price_per_night: Maximum nightly budget limit.
        currency: Currency code (default 'EUR').
        provider: Optional target provider name (e.g. 'amadeus_hotel', 'booking_hotel', 'mock_hotel').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized accommodation search result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.HOTEL,
            provider_name=provider,
            city=city,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            neighborhood=neighborhood,
            guests=guests,
            max_price_per_night=max_price_per_night,
            currency=currency,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "hotel",
            "mode": mode,
            "requires_booking_verification": True,
        }


def search_hotel_reviews(
    hotel_name: str,
    city: str,
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Retrieve community ratings and customer sentiment reviews for a lodging venue.

    NOTE: Review sources (including StayAPI Trip.com) provide feedback only, not inventory or booking.

    Args:
        hotel_name: Name of hotel or accommodation property.
        city: City where property is located.
        provider: Optional target provider name (e.g. 'stayapi_review', 'tripadvisor_review', 'mock_review').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized review result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.REVIEW,
            provider_name=provider,
            hotel_name=hotel_name,
            city=city,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "review",
            "mode": mode,
            "requires_booking_verification": False,
        }


def search_activity_options(
    city: str,
    category: Optional[str] = None,
    indoor_only: Optional[bool] = None,
    max_price: Optional[float] = None,
    currency: str = "EUR",
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Explore curated activities with crowd avoidance advice, weather alternatives, and official tickets.

    STRICT SAFETY: Informational only; zero cart additions or purchases.

    Args:
        city: Target city.
        category: Category (culture, gastronomy, nature, scenery, adventure, relaxation, family, photo, nightlife).
        indoor_only: Filter for indoor activities (useful during rain).
        max_price: Maximum admission cost per person.
        currency: Currency code (default 'EUR').
        provider: Optional target provider name (e.g. 'gyg_activity', 'viator', 'opentripmap', 'mock_activity').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized activity search result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.ACTIVITY,
            provider_name=provider,
            city=city,
            category_filter=category,
            indoor_only=indoor_only,
            max_price=max_price,
            currency=currency,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "activity",
            "mode": mode,
            "requires_booking_verification": True,
        }


def get_route_options(
    origin: str,
    destination: str,
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Calculate distance, travel durations (walking, driving, transit), and detect transit fatigue overload.

    Args:
        origin: Origin city or landmark.
        destination: Destination city or landmark.
        provider: Optional target provider name (e.g. 'google_maps', 'openrouteservice', 'osrm', 'nominatim', 'mock_maps').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized route calculation with fatigue warnings if transit exceeds 4 hours.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.MAP,
            provider_name=provider,
            origin=origin,
            destination=destination,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "map",
            "mode": mode,
            "requires_booking_verification": False,
        }


def get_weather_outlook(
    city: str,
    date: Optional[str] = None,
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Retrieve weather forecast and indoor contingency recommendations for rain or extreme weather.

    Args:
        city: Destination city name.
        date: Target date (YYYY-MM-DD).
        provider: Optional target provider name (e.g. 'openweather', 'open_meteo', 'mock_weather').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Weather outlook distinguishing forecast, historical climate, and rainy-day Plan B.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.WEATHER,
            provider_name=provider,
            city=city,
            date=date,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "weather",
            "mode": mode,
            "requires_booking_verification": False,
        }


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    custom_rate: Optional[float] = None,
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Convert monetary amounts between currencies with published reference date tracking.

    Args:
        amount: Numerical amount to convert (>= 0).
        from_currency: 3-letter currency code (e.g. 'EUR', 'USD', 'ISK').
        to_currency: 3-letter target currency code.
        custom_rate: Optional manual exchange rate override.
        provider: Optional target provider name (e.g. 'ecb_currency', 'mock_currency').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Converted amount, rate, rate publication date, and freshness warnings.
    """
    if amount < 0:
        return {"status": "error", "error": "Amount must be >= 0."}

    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.CURRENCY,
            provider_name=provider,
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            custom_rate=custom_rate,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": "currency",
            "mode": mode,
            "requires_booking_verification": False,
        }


def search_travel_sources(
    query: str,
    category: Optional[str] = None,
    provider: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Query travel guide knowledge, local etiquette, and social discovery trends.

    STRICT SAFETY: Results from social media are strictly marked 'social_discovery_only'
    and require independent verification.

    Args:
        query: Destination city or topic keyword.
        category: 'guide' (Wikivoyage editorial) or 'social' (community trends).
        provider: Optional target provider name (e.g. 'wikivoyage', 'social_discovery', 'mock_guide').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized search result with provenance metadata and verification levels.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    cat = ProviderCategory.SOCIAL if category == "social" else ProviderCategory.GUIDE
    try:
        res = default_registry.search(
            category=cat,
            provider_name=provider,
            city=query,
            keyword=query,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": cat.value,
            "mode": mode,
            "requires_booking_verification": False,
        }


# ===========================================================================
# Phase 10: Keyless Public Data MCP Tools (Zero API Key Required)
# ===========================================================================

def geocode_destination(destination: str, mode: str = "offline") -> Dict[str, Any]:
    """Geocode a destination to latitude, longitude, and country using Open-Meteo or Nominatim.

    Args:
        destination: Destination city or landmark name (e.g. 'Barcelona', 'Reykjavik', 'Paris').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Structured geocoding coordinates with license attribution and provenance metadata.
    """
    from datetime import datetime, timezone
    from ultimate_travel_agent.integrations import default_registry, ProviderConfigurationError
    from ultimate_travel_agent.integrations.weather.open_meteo import OpenMeteoProvider, OPEN_METEO_ATTRIBUTION, OPEN_METEO_SOURCE_URL

    clean_dest = destination.strip()
    now_iso = datetime.now(timezone.utc).isoformat()

    if mode.lower() == "live":
        prov = default_registry.get_provider("open_meteo")
        if isinstance(prov, OpenMeteoProvider) and prov.is_configured():
            geo = prov.geocode_destination(clean_dest)
            if geo:
                return {
                    "provider": "open_meteo",
                    "mode": "live",
                    "retrieved_at": now_iso,
                    "source_url": OPEN_METEO_SOURCE_URL,
                    "attribution": OPEN_METEO_ATTRIBUTION,
                    "verification_level": "official_verified",
                    "cache_status": "hit" if prov.http_client else "miss",
                    "result_status": "live",
                    "destination": geo["name"],
                    "latitude": geo["latitude"],
                    "longitude": geo["longitude"],
                    "country": geo.get("country"),
                    "timezone": geo.get("timezone", "UTC"),
                    "admin_region": geo.get("admin1"),
                    "requires_booking_verification": False,
                }
            return {
                "provider": "open_meteo",
                "mode": "live",
                "retrieved_at": now_iso,
                "source_url": OPEN_METEO_SOURCE_URL,
                "attribution": OPEN_METEO_ATTRIBUTION,
                "verification_level": "unverified",
                "cache_status": "miss",
                "result_status": "unavailable",
                "error": f"Destination '{clean_dest}' could not be resolved by geocoding.",
                "requires_booking_verification": False,
            }
        # If open_meteo not configured in live mode, check if nominatim is configured
        prov_nom = default_registry.get_provider("nominatim")
        if prov_nom and prov_nom.is_configured() and hasattr(prov_nom, "geocode"):
            geo_nom = prov_nom.geocode(clean_dest)
            if geo_nom:
                return {
                    "provider": "nominatim",
                    "mode": "live",
                    "retrieved_at": now_iso,
                    "source_url": "https://nominatim.openstreetmap.org/",
                    "attribution": "Geocoding data © OpenStreetMap contributors, ODbL 1.0",
                    "verification_level": "cross_checked",
                    "cache_status": geo_nom.get("cache_status", "miss"),
                    "result_status": "live",
                    "destination": clean_dest,
                    "display_name": geo_nom.get("display_name"),
                    "latitude": geo_nom.get("latitude"),
                    "longitude": geo_nom.get("longitude"),
                    "requires_booking_verification": False,
                }

        # If live requested but keyless live providers are not enabled
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": "Live geocoding requires TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_OPEN_METEO=true.",
            "provider": "open_meteo",
            "mode": mode,
            "requires_booking_verification": False,
        }

    # Deterministic offline / mock fallback coordinates
    from ultimate_travel_agent.integrations.maps.osrm import CITY_COORDINATES
    coords = CITY_COORDINATES.get(clean_dest.lower(), (48.8566, 2.3522))
    return {
        "provider": "mock_maps",
        "mode": mode,
        "retrieved_at": now_iso,
        "source_url": "local://offline-catalog",
        "attribution": "Offline deterministic coordinates database",
        "verification_level": "cross_checked",
        "cache_status": "hit",
        "result_status": "needs_verification",
        "destination": clean_dest,
        "latitude": coords[0],
        "longitude": coords[1],
        "country": "Offline / Catalog",
        "timezone": "UTC",
        "requires_booking_verification": False,
    }


def get_weather_forecast(city: str, days: int = 7, mode: str = "offline") -> Dict[str, Any]:
    """Retrieve 7-day weather forecast (temperatures, precipitation, wind) from Open-Meteo.

    Args:
        city: Target city name (e.g. 'Paris', 'Barcelona', 'Reykjavik').
        days: Forecast window in days (default 7, max 14).
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Structured weather forecast with rain probability, temperature ranges, and CC BY 4.0 attribution.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.WEATHER,
            provider_name="open_meteo",
            city=city,
            days=days,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "provider": "open_meteo",
            "category": "weather",
            "mode": mode,
            "requires_booking_verification": False,
        }


def get_weather_activity_advice(
    city: str,
    date: Optional[str] = None,
    planned_activity: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Evaluate weather conditions and recommend indoor Plan B or optimal outdoor windows.

    Args:
        city: Target city name.
        date: Target travel date (YYYY-MM-DD).
        planned_activity: Optional description of outdoor activity planned (e.g. 'Park walk', 'Boat tour').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Rain risk evaluation, activity advice, and indoor backup suggestions.
    """
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    fc = get_weather_forecast(city=city, days=7, mode=mode)

    if fc.get("status") == "error":
        return fc

    items = fc.get("items", [])
    target_item = None
    if date:
        for it in items:
            if it.get("details", {}).get("date") == date:
                target_item = it
                break

    if not target_item and items:
        # Fall back to first daily forecast item or current conditions
        target_item = items[1] if len(items) > 1 else items[0]

    details = target_item.get("details", {}) if target_item else {}
    p_prob = details.get("precipitation_probability_pct", 10)
    p_sum = details.get("precipitation_sum_mm", 0.0)
    cond = details.get("condition", "Mild conditions")
    rain_risk = details.get("rain_risk", p_prob >= 40 or p_sum >= 2.0)

    if rain_risk:
        advice = (
            f"Adverse weather / rain risk detected ({p_prob}% chance, {p_sum}mm) in {city}. "
            f"Switch outdoor activities ('{planned_activity or 'outdoor visits'}') to indoor contingency Plan B: "
            "major museums, covered food halls, historical galleries, or transit tours."
        )
        indoor_backup = "Visit national art museum, historic basilica interior, or covered market."
    else:
        advice = (
            f"Favorable outdoor conditions in {city} ({cond}). "
            f"Proceed with outdoor activities ('{planned_activity or 'walking tour'}')."
        )
        indoor_backup = "Standard indoor alternative on standby if afternoon showers develop."

    return {
        "provider": fc.get("provider", "open_meteo"),
        "mode": fc.get("mode", mode),
        "retrieved_at": fc.get("retrieved_at", now_iso),
        "source_url": fc.get("source_url", "https://open-meteo.com/"),
        "attribution": fc.get("attribution", "Weather data by Open-Meteo.com under CC BY 4.0"),
        "verification_level": fc.get("verification_level", "official_verified"),
        "cache_status": fc.get("cache_status", "hit"),
        "result_status": fc.get("result_status", "live"),
        "city": city,
        "date": date or "upcoming",
        "condition": cond,
        "precipitation_probability_pct": p_prob,
        "precipitation_sum_mm": p_sum,
        "rain_risk_detected": rain_risk,
        "indoor_plan_b_recommended": rain_risk,
        "recommended_indoor_backup": indoor_backup,
        "activity_advice": advice,
        "requires_booking_verification": False,
    }


def get_exchange_rates(
    base_currency: str = "EUR",
    symbols: Optional[List[str]] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Retrieve daily official reference exchange rates published by the European Central Bank.

    STRICT NOTICE: ECB reference rates are non-commercial benchmarks and do not include credit card markups (1.5-3.5%).

    Args:
        base_currency: Base 3-letter currency code (default 'EUR').
        symbols: Optional list of target currencies (e.g. ['USD', 'GBP', 'JPY', 'ISK']).
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Table of reference rates, publication date, and mandatory card fee disclaimer.
    """
    from datetime import datetime, timezone
    from ultimate_travel_agent.integrations import default_registry, ProviderConfigurationError
    from ultimate_travel_agent.integrations.currency.ecb import (
        ECBCurrencyProvider,
        ECB_ATTRIBUTION,
        ECB_SOURCE_URL,
        LOCAL_RATE_FALLBACK,
    )

    base = base_currency.strip().upper()
    now_iso = datetime.now(timezone.utc).isoformat()
    advisory = (
        "Official European Central Bank (ECB) reference rate. "
        "Indicative only: commercial card and bank exchange rates typically incur 1.5% - 3.5% markup."
    )

    if mode.lower() == "live":
        prov = default_registry.get_provider("ecb_currency")
        if isinstance(prov, ECBCurrencyProvider) and prov.is_configured():
            try:
                rates_raw, rate_date, cache_status = prov.fetch_ecb_rates()
                base_rate = rates_raw.get(base, 1.0)
                rates_out: Dict[str, float] = {}
                for curr, r in rates_raw.items():
                    if not symbols or curr in [s.upper() for s in symbols]:
                        rates_out[curr] = round(r / base_rate, 5)
                return {
                    "provider": "ecb_currency",
                    "mode": "live",
                    "retrieved_at": now_iso,
                    "source_url": ECB_SOURCE_URL,
                    "attribution": ECB_ATTRIBUTION,
                    "verification_level": "official_verified",
                    "cache_status": cache_status,
                    "result_status": "live",
                    "base_currency": base,
                    "rate_date": rate_date,
                    "rates": rates_out,
                    "advisory": advisory,
                    "requires_booking_verification": False,
                }
            except Exception as err:
                return {
                    "status": "error",
                    "error_type": "ProviderNetworkError",
                    "error": f"Failed to retrieve live ECB rates: {str(err)}",
                    "provider": "ecb_currency",
                    "mode": mode,
                }
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": "Live ECB feed requires TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_ECB=true.",
            "provider": "ecb_currency",
            "mode": mode,
        }

    # Offline table
    base_rate = LOCAL_RATE_FALLBACK.get(base, 1.0)
    rates_out = {
        k: round(v / base_rate, 5)
        for k, v in LOCAL_RATE_FALLBACK.items()
        if not symbols or k in [s.upper() for s in symbols]
    }
    return {
        "provider": "mock_currency",
        "mode": mode,
        "retrieved_at": now_iso,
        "source_url": "local://offline-catalog",
        "attribution": "Local deterministic exchange rate reference table",
        "verification_level": "cross_checked",
        "cache_status": "hit",
        "result_status": "needs_verification",
        "base_currency": base,
        "rate_date": "2026-09-01 (offline catalog)",
        "rates": rates_out,
        "advisory": advisory,
        "requires_booking_verification": False,
    }


def convert_currency_live(
    amount: float,
    from_currency: str,
    to_currency: str,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Convert an amount using official ECB reference rates (keyless, zero API fee).

    Args:
        amount: Number of units to convert (>= 0).
        from_currency: Source currency ISO code (e.g. 'EUR', 'USD', 'GBP').
        to_currency: Target currency ISO code (e.g. 'ISK', 'JPY', 'CHF').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Converted value, reference rate, publication date, and card markup advisory.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.CURRENCY,
            provider_name="ecb_currency",
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "provider": "ecb_currency",
            "category": "currency",
            "mode": mode,
            "requires_booking_verification": False,
        }


def search_wikivoyage_destination(destination: str, mode: str = "offline") -> Dict[str, Any]:
    """Search Wikivoyage for matching destination guide articles (CC BY-SA 4.0).

    Args:
        destination: Query keyword or city name (e.g. 'Barcelone', 'Reykjavik', 'Kyoto').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        List of matching articles with titles, descriptions, and official Wikivoyage URLs.
    """
    from datetime import datetime, timezone
    from ultimate_travel_agent.integrations import default_registry, ProviderConfigurationError
    from ultimate_travel_agent.integrations.guides.wikivoyage import (
        WikivoyageProvider,
        WIKIVOYAGE_ATTRIBUTION,
        WIKIVOYAGE_COMMUNITY_ADVISORY,
    )

    clean_dest = destination.strip()
    now_iso = datetime.now(timezone.utc).isoformat()

    if mode.lower() == "live":
        prov = default_registry.get_provider("wikivoyage")
        if isinstance(prov, WikivoyageProvider) and prov.is_configured():
            articles = prov.search_destinations(clean_dest)
            return {
                "provider": "wikivoyage",
                "mode": "live",
                "retrieved_at": now_iso,
                "source_url": "https://en.wikivoyage.org/",
                "attribution": WIKIVOYAGE_ATTRIBUTION,
                "verification_level": "community_recommended",
                "cache_status": "hit" if prov.http_client else "miss",
                "result_status": "live",
                "query": clean_dest,
                "total_results": len(articles),
                "articles": articles,
                "advisory": WIKIVOYAGE_COMMUNITY_ADVISORY,
                "requires_booking_verification": False,
            }
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": "Live Wikivoyage requires TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_WIKIVOYAGE=true.",
            "provider": "wikivoyage",
            "mode": mode,
        }

    # Offline / mock response
    return {
        "provider": "mock_guide",
        "mode": mode,
        "retrieved_at": now_iso,
        "source_url": f"https://en.wikivoyage.org/wiki/{clean_dest.replace(' ', '_')}",
        "attribution": WIKIVOYAGE_ATTRIBUTION,
        "verification_level": "community_recommended",
        "cache_status": "hit",
        "result_status": "needs_verification",
        "query": clean_dest,
        "total_results": 1,
        "articles": [
            {
                "title": clean_dest,
                "description": f"Curated guide overview for {clean_dest} (offline catalog).",
                "url": f"https://en.wikivoyage.org/wiki/{clean_dest.replace(' ', '_')}",
            }
        ],
        "advisory": WIKIVOYAGE_COMMUNITY_ADVISORY,
        "requires_booking_verification": False,
    }


def get_wikivoyage_summary(destination: str, mode: str = "offline") -> Dict[str, Any]:
    """Retrieve encyclopedic introduction and essential cultural context from Wikivoyage.

    Args:
        destination: Destination name (e.g. 'Barcelona', 'Kyoto', 'Paris').
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Structured destination summary, canonical URL, and CC BY-SA 4.0 license attribution.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.GUIDE,
            provider_name="wikivoyage",
            city=destination,
            mode=mode,
        )
        return res.model_dump()
    except (ProviderConfigurationError, KeyError) as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "provider": "wikivoyage",
            "category": "guide",
            "mode": mode,
            "requires_booking_verification": False,
        }


def get_limited_route_options(origin: str, destination: str, mode: str = "offline") -> Dict[str, Any]:
    """Calculate driving distance and durations using OSRM demo routing (experimental, disabled by default).

    Args:
        origin: Origin city or coordinates (lat, lon).
        destination: Destination city or coordinates.
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Distance, driving duration, fatigue alerts, and OSRM/OSM attribution.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.MAP,
            provider_name="osrm",
            origin=origin,
            destination=destination,
            mode=mode,
        )
        return res.model_dump()
    except ProviderConfigurationError as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "provider": "osrm",
            "category": "map",
            "mode": mode,
            "requires_booking_verification": False,
            "advisory": "OSRM demo routing is disabled by default to respect public demo quotas. Use mock/offline mode or self-host OSRM.",
        }


def get_keyless_provider_status() -> Dict[str, Any]:
    """Inspect operational readiness, rate limits, and configuration of all Phase 10 keyless providers.

    Returns:
        Status audit of Open-Meteo, ECB, Wikivoyage, Nominatim, and OSRM.
    """
    from datetime import datetime, timezone
    import os
    from ultimate_travel_agent.integrations import default_registry

    keyless_active = os.getenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "").lower() in ("true", "1", "yes") or \
                     os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")
    user_agent = os.getenv("TRAVEL_MCP_HTTP_USER_AGENT", "UltimateTravelAgent/1.0 (https://github.com/Gustor1/ultimate-travel-agent)")

    providers_info = [
        {
            "provider": "open_meteo",
            "category": "weather",
            "status": "live_ready" if (keyless_active and os.getenv("TRAVEL_MCP_ENABLE_OPEN_METEO", "true").lower() in ("true", "1", "yes")) else "offline_mock",
            "decision": "approved",
            "rate_limit": "5 req/s max",
            "requires_key": False,
            "license": "CC BY 4.0",
            "attribution": "Weather data by Open-Meteo.com under CC BY 4.0",
        },
        {
            "provider": "ecb_currency",
            "category": "currency",
            "status": "live_ready" if (keyless_active and os.getenv("TRAVEL_MCP_ENABLE_ECB", "true").lower() in ("true", "1", "yes")) else "offline_mock",
            "decision": "approved",
            "rate_limit": "2 req/s max",
            "requires_key": False,
            "license": "Open ECB Data",
            "attribution": "Source: European Central Bank (ECB) euro reference exchange rates",
        },
        {
            "provider": "wikivoyage",
            "category": "guide",
            "status": "live_ready" if (keyless_active and os.getenv("TRAVEL_MCP_ENABLE_WIKIVOYAGE", "true").lower() in ("true", "1", "yes")) else "offline_mock",
            "decision": "approved",
            "rate_limit": "3 req/s max",
            "requires_key": False,
            "license": "CC BY-SA 4.0",
            "attribution": "Text from Wikivoyage under CC BY-SA 4.0",
        },
        {
            "provider": "nominatim",
            "category": "map",
            "status": "live_ready" if (keyless_active and os.getenv("TRAVEL_MCP_ENABLE_NOMINATIM", "false").lower() in ("true", "1", "yes")) else "disabled_by_default",
            "decision": "limited",
            "rate_limit": "1 req/s absolute max (single worker mutex)",
            "requires_key": False,
            "license": "ODbL 1.0",
            "attribution": "Data © OpenStreetMap contributors, ODbL 1.0",
        },
        {
            "provider": "osrm",
            "category": "map",
            "status": "live_ready" if (keyless_active and os.getenv("TRAVEL_MCP_ENABLE_OSRM", "false").lower() in ("true", "1", "yes")) else "disabled_by_default",
            "decision": "experimental",
            "rate_limit": "1 req/s max (public demo server, no SLA)",
            "requires_key": False,
            "license": "BSD 2-Clause / ODbL",
            "attribution": "Routing data © Project OSRM / OpenStreetMap contributors",
        },
    ]

    return {
        "status": "healthy",
        "hub_phase": "Phase 10 — Keyless Public Data Integrations",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "keyless_live_master_enabled": keyless_active,
        "http_user_agent": user_agent,
        "total_keyless_providers": len(providers_info),
        "providers": providers_info,
        "commercial_providers_status": "disabled_for_phase_10",
    }

