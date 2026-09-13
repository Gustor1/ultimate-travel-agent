"""Inter-city route recommendation and ranking engine for ultimate-travel-agent."""

from typing import Dict, List, Optional, Tuple, Union
from ultimate_travel_agent.models.enums import RoutePreference, RouteTransportMode
from ultimate_travel_agent.models.route import InterCityRoute, RouteOption

# Default carbon footprint (kg CO2 per passenger for typical inter-city hop) if unstated
_DEFAULT_ECO_WEIGHTS: Dict[RouteTransportMode, float] = {
    RouteTransportMode.WALKING: 0.0,
    RouteTransportMode.TRAIN: 14.0,
    RouteTransportMode.PUBLIC_TRANSPORT: 20.0,
    RouteTransportMode.BUS: 28.0,
    RouteTransportMode.FERRY: 55.0,
    RouteTransportMode.CAR: 110.0,
    RouteTransportMode.FLIGHT: 180.0,
}


def _effective_carbon(option: RouteOption) -> float:
    """Return explicit carbon footprint or default mode estimate."""
    if option.carbon_footprint_kg is not None:
        return option.carbon_footprint_kg
    return _DEFAULT_ECO_WEIGHTS.get(option.mode, 75.0)


def recommend_route_option(
    route: InterCityRoute,
    preference: Union[RoutePreference, str] = RoutePreference.CHEAPEST,
) -> Tuple[Optional[RouteOption], str]:
    """Recommend the optimal RouteOption for an InterCityRoute given user preference.

    Supported preferences (in English or French):
    - 'cheapest' / 'moins chère': Minimal estimated financial cost
    - 'fastest' / 'plus rapide': Minimal total door-to-door transit duration
    - 'fewest_transfers' / 'moins de correspondances': Fewest connections, then fastest duration
    - 'most_comfortable' / 'plus confortable': Highest comfort score, then fewest transfers
    - 'most_eco_friendly' / 'plus écologique': Lowest carbon footprint (kg CO2)
    - 'relaxed': High comfort, minimal connections (<=1), peaceful travel
    - 'packed': Fastest transit to maximize sightseeing time at destination
    """
    if not route.options:
        return None, "No route options available between these destinations."

    pref_val = preference.value if isinstance(preference, RoutePreference) else str(preference).lower()
    norm = (
        pref_val.strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("é", "e")
        .replace("è", "e")
    )

    if norm in ("cheapest", "moins_chere", "moins_cher", "economique"):
        sorted_opts = sorted(route.options, key=lambda o: (o.estimated_cost, o.estimated_duration_minutes))
        chosen = sorted_opts[0]
        reason = f"Cheapest option at {chosen.estimated_cost:.2f} {chosen.currency} ({chosen.mode.value})."
        return chosen, reason

    if norm in ("fastest", "plus_rapide", "rapide", "packed", "intense"):
        sorted_opts = sorted(route.options, key=lambda o: (o.estimated_duration_minutes, o.transfers_count))
        chosen = sorted_opts[0]
        reason = f"Fastest door-to-door option at {chosen.estimated_duration_minutes} min ({chosen.mode.value})."
        return chosen, reason

    if norm in ("fewest_transfers", "moins_de_correspondances", "direct"):
        sorted_opts = sorted(route.options, key=lambda o: (o.transfers_count, o.estimated_duration_minutes))
        chosen = sorted_opts[0]
        reason = f"Fewest transfers ({chosen.transfers_count} connection(s)) via {chosen.mode.value} in {chosen.estimated_duration_minutes} min."
        return chosen, reason

    if norm in ("most_comfortable", "plus_confortable", "confort"):
        sorted_opts = sorted(route.options, key=lambda o: (-o.comfort_level, o.transfers_count, o.estimated_duration_minutes))
        chosen = sorted_opts[0]
        reason = f"Most comfortable option (score {chosen.comfort_level}/5) via {chosen.mode.value}."
        return chosen, reason

    if norm in ("most_eco_friendly", "plus_ecologique", "ecologique", "eco"):
        sorted_opts = sorted(route.options, key=lambda o: (_effective_carbon(o), o.estimated_cost))
        chosen = sorted_opts[0]
        carbon = _effective_carbon(chosen)
        reason = f"Lowest environmental footprint (~{carbon:.1f} kg CO2) via {chosen.mode.value}."
        return chosen, reason

    if norm in ("relaxed", "detendu", "detente"):
        # Prefer comfort >= 3 and transfers <= 1, then least transfers and highest comfort
        def relaxed_score(o: RouteOption) -> Tuple[int, int, int]:
            # penalty if transfers > 1
            transfer_penalty = 1 if o.transfers_count > 1 else 0
            # comfort bonus
            comfort_rank = -o.comfort_level
            return (transfer_penalty, comfort_rank, o.estimated_duration_minutes)

        sorted_opts = sorted(route.options, key=relaxed_score)
        chosen = sorted_opts[0]
        reason = f"Optimized for relaxed pacing: {chosen.transfers_count} transfer(s), comfort {chosen.comfort_level}/5 via {chosen.mode.value}."
        return chosen, reason

    # Default fallback: balance of cost and time
    sorted_opts = sorted(route.options, key=lambda o: (o.estimated_cost * 0.5 + o.estimated_duration_minutes * 0.2))
    chosen = sorted_opts[0]
    return chosen, f"Balanced recommendation: {chosen.mode.value} ({chosen.estimated_duration_minutes} min, {chosen.estimated_cost:.2f} {chosen.currency})."


def evaluate_all_preferences(route: InterCityRoute) -> Dict[str, Dict[str, Union[str, float, int]]]:
    """Evaluate optimal choices across all 7 supported travel preference profiles."""
    profiles = [
        RoutePreference.CHEAPEST,
        RoutePreference.FASTEST,
        RoutePreference.FEWEST_TRANSFERS,
        RoutePreference.MOST_COMFORTABLE,
        RoutePreference.MOST_ECO_FRIENDLY,
        RoutePreference.RELAXED,
        RoutePreference.PACKED,
    ]
    results: Dict[str, Dict[str, Union[str, float, int]]] = {}
    for prof in profiles:
        chosen, reason = recommend_route_option(route, prof)
        if chosen:
            results[prof.value] = {
                "option_id": chosen.id,
                "mode": chosen.mode.value,
                "duration_minutes": chosen.estimated_duration_minutes,
                "transfers_count": chosen.transfers_count,
                "cost": chosen.estimated_cost,
                "currency": chosen.currency,
                "comfort_level": chosen.comfort_level,
                "carbon_footprint_kg": _effective_carbon(chosen),
                "reason": reason,
            }
    return results
