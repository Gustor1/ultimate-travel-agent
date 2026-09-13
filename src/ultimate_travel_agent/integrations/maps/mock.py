"""Deterministic offline maps, routing, geocoding, and distance matrix provider."""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    PriceStatus,
    ProviderCategory,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
)
from ultimate_travel_agent.models import VerificationLevel


# Static coordinates of reference cities and landmarks
_GEO_COORDINATES: Dict[str, Tuple[float, float]] = {
    "paris": (48.8566, 2.3522),
    "barcelona": (41.3851, 2.1734),
    "madrid": (40.4168, -3.7038),
    "reykjavik": (64.1466, -21.9426),
    "vik": (63.4186, -19.0060),
    "hofn": (64.2539, -15.2082),
    "lyon": (45.7640, 4.8357),
    "perpignan": (42.6886, 2.8948),
    "girona": (41.9794, 2.8214),
    "sagrada familia": (41.4036, 2.1744),
    "park guell": (41.4145, 2.1527),
}


def _haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Compute great-circle distance in kilometers between two GPS coordinates."""
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return round(6371.0 * c, 1)


class MockMapsProvider(Provider):
    """Deterministic routing and geocoding provider operating 100% offline."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_maps",
            category=ProviderCategory.MAP,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "geocode",
                "calculate_distance",
                "calculate_route",
                "create_city_matrix",
                "suggest_stage_order",
                "flag_transit_overload",
            ],
        )

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://www.openstreetmap.org",
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=None,
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.LIVE.value,
            requires_booking_verification=False,
            title=f"Route: {raw.get('origin')} -> {raw.get('destination')}",
            description=(
                f"Distance: {raw.get('distance_km')} km. Driving: {raw.get('driving_minutes')} min. "
                f"Transit: {raw.get('transit_minutes')} min. Walking: {raw.get('walking_minutes')} min."
            ),
            price=None,
            details=raw,
        )

    def geocode(self, place_name: str) -> Optional[Tuple[float, float]]:
        """Resolve a city or landmark to (lat, lon) coordinates."""
        key = place_name.lower().strip()
        for k, coords in _GEO_COORDINATES.items():
            if k in key or key in k:
                return coords
        return (48.8566, 2.3522)  # fallback

    def calculate_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """Compute estimated distance and transit times."""
        c1 = self.geocode(origin) or (48.8566, 2.3522)
        c2 = self.geocode(destination) or (41.3851, 2.1734)
        dist = _haversine_distance(c1, c2)
        if dist == 0:
            dist = 5.0  # internal intra-city transfer

        # Road curvature factor ~ 1.25
        road_km = round(dist * 1.25, 1)
        driving_min = max(10, int((road_km / 85.0) * 60))
        transit_min = max(15, int((road_km / 120.0) * 60) + 30)
        walking_min = int((road_km / 4.5) * 60)

        is_overloaded = driving_min > 240 or transit_min > 300

        return {
            "origin": origin,
            "destination": destination,
            "origin_coordinates": c1,
            "destination_coordinates": c2,
            "direct_distance_km": dist,
            "distance_km": road_km,
            "driving_minutes": driving_min,
            "transit_minutes": transit_min,
            "walking_minutes": walking_min,
            "is_transit_overloaded": is_overloaded,
            "fatigue_warning": (
                f"Heavy transit warning: {driving_min} min of driving exceeds recommended 4h daily threshold."
                if is_overloaded
                else None
            ),
        }

    def create_city_matrix(self, cities: List[str]) -> Dict[str, Dict[str, float]]:
        """Create an N x N distance matrix between multiple cities."""
        matrix: Dict[str, Dict[str, float]] = {}
        for c1 in cities:
            matrix[c1] = {}
            for c2 in cities:
                if c1 == c2:
                    matrix[c1][c2] = 0.0
                else:
                    route = self.calculate_route(c1, c2)
                    matrix[c1][c2] = route["distance_km"]
        return matrix

    def suggest_stage_order(self, stages: List[str], start_stage: Optional[str] = None) -> List[str]:
        """Suggest logical geographic sequencing to minimize backtracking (greedy TSP)."""
        if len(stages) <= 2:
            return stages

        unvisited = list(stages)
        current = start_stage if start_stage and start_stage in unvisited else unvisited[0]
        unvisited.remove(current)
        route = [current]

        while unvisited:
            next_stop = min(
                unvisited,
                key=lambda candidate: self.calculate_route(current, candidate)["distance_km"],
            )
            unvisited.remove(next_stop)
            route.append(next_stop)
            current = next_stop

        return route

    def search(
        self,
        origin: str = "Paris",
        destination: str = "Barcelona",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        route_data = self.calculate_route(origin, destination)
        item = self.normalize_result(route_data)

        warnings = []
        if route_data.get("fatigue_warning"):
            warnings.append(route_data["fatigue_warning"])

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={"origin": origin, "destination": destination},
            total_results=1,
            items=[item],
            source_metadata=self.get_source_metadata(),
            warnings=warnings,
            requires_booking_verification=False,
        )
