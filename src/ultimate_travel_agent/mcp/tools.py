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
    except ProviderConfigurationError as err:
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
    mode: str = "offline",
) -> Dict[str, Any]:
    """Search rail connections with door-to-door transit time, transfers, and official booking portals.

    STRICT SAFETY: Never executes automated ticketing.

    Args:
        origin: Departure station or city name.
        destination: Arrival station or city name.
        date: Travel date (YYYY-MM-DD).
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized rail search result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.TRAIN,
            origin=origin,
            destination=destination,
            date=date,
            mode=mode,
        )
        return res.model_dump()
    except ProviderConfigurationError as err:
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
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized accommodation search result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.HOTEL,
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
    except ProviderConfigurationError as err:
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
    mode: str = "offline",
) -> Dict[str, Any]:
    """Retrieve community ratings and customer sentiment reviews for a lodging venue.

    NOTE: Review sources (including StayAPI Trip.com) provide feedback only, not inventory or booking.

    Args:
        hotel_name: Name of hotel or accommodation property.
        city: City where property is located.
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized review result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.REVIEW,
            hotel_name=hotel_name,
            city=city,
            mode=mode,
        )
        return res.model_dump()
    except ProviderConfigurationError as err:
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
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized activity search result.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.ACTIVITY,
            city=city,
            category_filter=category,
            indoor_only=indoor_only,
            max_price=max_price,
            currency=currency,
            mode=mode,
        )
        return res.model_dump()
    except ProviderConfigurationError as err:
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
    mode: str = "offline",
) -> Dict[str, Any]:
    """Calculate distance, travel durations (walking, driving, transit), and detect transit fatigue overload.

    Args:
        origin: Origin city or landmark.
        destination: Destination city or landmark.
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized route calculation with fatigue warnings if transit exceeds 4 hours.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.MAP,
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
            "category": "map",
            "mode": mode,
            "requires_booking_verification": False,
        }


def get_weather_outlook(
    city: str,
    date: Optional[str] = None,
    mode: str = "offline",
) -> Dict[str, Any]:
    """Retrieve weather forecast and indoor contingency recommendations for rain or extreme weather.

    Args:
        city: Destination city name.
        date: Target date (YYYY-MM-DD).
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Weather outlook distinguishing forecast, historical climate, and rainy-day Plan B.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    try:
        res = default_registry.search(
            category=ProviderCategory.WEATHER,
            city=city,
            date=date,
            mode=mode,
        )
        return res.model_dump()
    except ProviderConfigurationError as err:
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
    mode: str = "offline",
) -> Dict[str, Any]:
    """Convert monetary amounts between currencies with published reference date tracking.

    Args:
        amount: Numerical amount to convert (>= 0).
        from_currency: 3-letter currency code (e.g. 'EUR', 'USD', 'ISK').
        to_currency: 3-letter target currency code.
        custom_rate: Optional manual exchange rate override.
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
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            custom_rate=custom_rate,
            mode=mode,
        )
        return res.model_dump()
    except ProviderConfigurationError as err:
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
    mode: str = "offline",
) -> Dict[str, Any]:
    """Query travel guide knowledge, local etiquette, and social discovery trends.

    STRICT SAFETY: Results from social media are strictly marked 'social_discovery_only'
    and require independent verification.

    Args:
        query: Destination city or topic keyword.
        category: 'guide' (Wikivoyage editorial) or 'social' (community trends).
        mode: 'offline', 'mock', or 'live'.

    Returns:
        Standardized search result with provenance metadata and verification levels.
    """
    from ultimate_travel_agent.integrations import ProviderCategory, ProviderConfigurationError, default_registry
    cat = ProviderCategory.SOCIAL if category == "social" else ProviderCategory.GUIDE
    try:
        res = default_registry.search(
            category=cat,
            city=query,
            keyword=query,
            mode=mode,
        )
        return res.model_dump()
    except ProviderConfigurationError as err:
        return {
            "status": "error",
            "error_type": "ProviderConfigurationError",
            "error": str(err),
            "category": cat.value,
            "mode": mode,
            "requires_booking_verification": False,
        }
