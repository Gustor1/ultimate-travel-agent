"""OSRM (Open Source Routing Machine) routing provider (experimental, demo server, BSD 2-Clause / ODbL)."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional, Tuple

from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.http_client import KeylessHttpClient
from ultimate_travel_agent.integrations.maps.mock import MockMapsProvider
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    CacheStatus,
    PriceStatus,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
    ResultStatus,
)
from ultimate_travel_agent.models import VerificationLevel

OSRM_DEMO_URL = "https://router.project-osrm.org"
OSRM_ATTRIBUTION = "Routing data © Project OSRM / OpenStreetMap contributors (ODbL / BSD 2-Clause)"
OSRM_SOURCE_URL = "https://project-osrm.org/"
OSRM_EXPERIMENTAL_NOTICE = (
    "Public OSRM demo server is provided strictly for experimental evaluation and carries NO SLA or uptime guarantee. "
    "Production deployments require self-hosting OSRM or using a professional provider (e.g. OpenRouteService)."
)

# Reference coordinates for common cities to avoid cascading geocoding in routing queries
CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    "paris": (48.8566, 2.3522),
    "lyon": (45.7640, 4.8357),
    "marseille": (43.2965, 5.3698),
    "bordeaux": (44.8378, -0.5792),
    "barcelona": (41.3879, 2.1699),
    "barcelone": (41.3879, 2.1699),
    "madrid": (40.4168, -3.7038),
    "rome": (41.9028, 12.4964),
    "roma": (41.9028, 12.4964),
    "london": (51.5074, -0.1278),
    "londres": (51.5074, -0.1278),
    "berlin": (52.5200, 13.4050),
    "amsterdam": (52.3676, 4.9041),
    "brussels": (50.8503, 4.3517),
    "bruxelles": (50.8503, 4.3517),
    "geneva": (46.2044, 6.1432),
    "geneve": (46.2044, 6.1432),
    "reykjavik": (64.1466, -21.9426),
}


class OSRMProvider(Provider):
    """OSRM route calculation provider for experimental low-volume road transit queries."""

    def __init__(
        self,
        backend_url: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
        http_client: Optional[KeylessHttpClient] = None,
    ) -> None:
        super().__init__(
            name="osrm",
            category=ProviderCategory.MAP,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["road_routing", "driving_duration", "distance_matrix"],
        )
        self.backend_url = backend_url or os.getenv("OSRM_BACKEND_URL", OSRM_DEMO_URL)
        self.http_client = http_client or KeylessHttpClient.get_instance()
        self._mock_delegate = MockMapsProvider(mode=mode)

    def is_configured(self) -> bool:
        """OSRM public demo is EXPERIMENTAL, DISABLED by default."""
        keyless_active = os.getenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "").lower() in ("true", "1", "yes") or \
                         os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")
        # Explicit opt-in required; defaults to False
        enabled = os.getenv("TRAVEL_MCP_ENABLE_OSRM", "false").lower() in ("true", "1", "yes")
        return keyless_active and enabled

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def _resolve_coordinates(self, location_str: str) -> Optional[Tuple[float, float]]:
        """Resolve city name or raw lat,lon string to (lat, lon)."""
        clean = location_str.strip()
        if "," in clean:
            parts = clean.split(",")
            try:
                return float(parts[0].strip()), float(parts[1].strip())
            except ValueError:
                pass
        return CITY_COORDINATES.get(clean.lower())

    def calculate_driving_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """Calculate road route via OSRM routing endpoint."""
        coord_orig = self._resolve_coordinates(origin)
        coord_dest = self._resolve_coordinates(destination)

        if not coord_orig or not coord_dest:
            raise ValueError(
                f"Cannot resolve coordinates for route '{origin}' -> '{destination}'. "
                "Provide known cities or numeric 'lat,lon' strings."
            )

        # OSRM expects {lon1},{lat1};{lon2},{lat2}
        url = f"{self.backend_url.rstrip('/')}/route/v1/driving/{coord_orig[1]},{coord_orig[0]};{coord_dest[1]},{coord_dest[0]}"
        params = {"overview": "false", "steps": "false"}

        data, cache_status = self.http_client.get(
            url,
            params=params,
            ttl_seconds=7200,  # 2 hours cache
            service_name="osrm",
            min_interval_seconds=1.0,
        )

        if not isinstance(data, dict) or data.get("code") != "Ok":
            raise ProviderConfigurationError(f"OSRM returned unexpected route status: {data.get('code', 'Unknown')}")

        routes = data.get("routes", [])
        if not routes:
            raise ProviderConfigurationError("No route found between specified points.")

        top_route = routes[0]
        distance_km = round(top_route.get("distance", 0.0) / 1000.0, 1)
        duration_minutes = round(top_route.get("duration", 0.0) / 60.0, 1)

        return {
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km,
            "duration_minutes": duration_minutes,
            "duration_hours": round(duration_minutes / 60.0, 2),
            "fatigue_warning": duration_minutes > 240.0,
            "cache_status": cache_status,
        }

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        """Route calculation search query. LIVE mode requires explicit configuration."""
        origin = kwargs.get("origin", "Paris")
        destination = kwargs.get("destination", "Lyon")

        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "OSRM demo routing provider is EXPERIMENTAL and DISABLED by default. "
                    "To activate, set TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_OSRM=true. "
                    "For production use, deploy a self-hosted OSRM container or use OpenRouteService."
                )

            route_info = self.calculate_driving_route(origin, destination)
            cache_status = route_info.get("cache_status", CacheStatus.MISS.value)
            warnings: List[str] = [OSRM_EXPERIMENTAL_NOTICE]

            if route_info["fatigue_warning"]:
                warnings.append(
                    f"Driving duration exceeds 4 hours ({route_info['duration_hours']:.1f}h). "
                    "Enforce a 30-minute rest buffer or consider high-speed rail alternative."
                )

            item = ProviderResultItem(
                provider=self.name,
                category=self.category.value,
                mode=self.mode.value,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                source_url=OSRM_SOURCE_URL,
                verification_level=VerificationLevel.CROSS_CHECKED.value,
                price_status=PriceStatus.ESTIMATED.value,
                availability_status=AvailabilityStatus.LIVE.value,
                requires_booking_verification=False,
                title=f"OSRM Driving: {origin} -> {destination} ({route_info['distance_km']} km)",
                description=f"Driving distance: {route_info['distance_km']} km, estimated duration: {route_info['duration_minutes']} min ({route_info['duration_hours']} hours).",
                details=route_info,
                attribution=OSRM_ATTRIBUTION,
                cache_status=cache_status,
                result_status=ResultStatus.LIVE.value,
            )

            return ProviderSearchResult(
                provider=self.name,
                category=self.category.value,
                mode=self.mode.value,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                query={"origin": origin, "destination": destination},
                total_results=1,
                items=[item],
                source_metadata={
                    "provider": self.name,
                    "category": self.category.value,
                    "attribution": OSRM_ATTRIBUTION,
                    "source_url": OSRM_SOURCE_URL,
                    "cache_status": cache_status,
                    "notice": OSRM_EXPERIMENTAL_NOTICE,
                },
                warnings=warnings,
                requires_booking_verification=False,
                attribution=OSRM_ATTRIBUTION,
                cache_status=cache_status,
                result_status=ResultStatus.LIVE.value,
                source_url=OSRM_SOURCE_URL,
            )

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        res.attribution = OSRM_ATTRIBUTION
        res.source_url = OSRM_SOURCE_URL
        res.cache_status = CacheStatus.HIT.value
        res.result_status = ResultStatus.NEEDS_VERIFICATION.value
        for it in res.items:
            it.provider = self.name
            it.attribution = OSRM_ATTRIBUTION
            it.source_url = OSRM_SOURCE_URL
        return res
