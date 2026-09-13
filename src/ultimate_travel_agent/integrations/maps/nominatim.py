"""Nominatim OpenStreetMap geocoding provider (rate-limited to 1 req/sec max, ODbL)."""

from datetime import datetime, timezone
import os
import threading
from typing import Any, Dict, List, Optional

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

NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
NOMINATIM_ATTRIBUTION = "Geocoding data © OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright)"
NOMINATIM_SOURCE_URL = "https://nominatim.openstreetmap.org/"

# Dedicated process-level lock to ensure strictly ONE single worker executes Nominatim requests
_NOMINATIM_WORKER_LOCK = threading.Lock()


class NominatimProvider(Provider):
    """Nominatim geocoding provider adhering to strict OSM Usage Policy (1 req/sec, no autocomplete)."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
        http_client: Optional[KeylessHttpClient] = None,
    ) -> None:
        super().__init__(
            name="nominatim",
            category=ProviderCategory.MAP,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["geocoding", "low_volume_reference", "osm_coordinates"],
        )
        self.endpoint_url = endpoint_url or os.getenv("NOMINATIM_URL", NOMINATIM_ENDPOINT)
        self.http_client = http_client or KeylessHttpClient.get_instance()
        self._mock_delegate = MockMapsProvider(mode=mode)

    def is_configured(self) -> bool:
        """Nominatim is a strictly LIMITED provider, DISABLED by default."""
        keyless_active = os.getenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "").lower() in ("true", "1", "yes") or \
                         os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")
        # Explicit opt-in required; defaults to False
        enabled = os.getenv("TRAVEL_MCP_ENABLE_NOMINATIM", "false").lower() in ("true", "1", "yes")
        return keyless_active and enabled

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def geocode(self, query: str) -> Optional[Dict[str, Any]]:
        """Geocode query with single-worker concurrency lock and 1 req/sec rate limit."""
        if not query or not query.strip():
            return None

        clean_query = query.strip()
        params = {
            "q": clean_query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }

        with _NOMINATIM_WORKER_LOCK:
            resp = self.http_client.get(
                self.endpoint_url,
                params=params,
                ttl_seconds=604800,  # 7 days compulsory caching
                service_name="nominatim",
                min_interval_seconds=1.0,  # Absolute 1.0s interval
            )
            data = resp[0]
            cache_status = resp[1]
            retrieved_at = getattr(resp, "retrieved_at", datetime.now(timezone.utc).isoformat())

        if isinstance(data, list) and data:
            top = data[0]
            return {
                "display_name": top.get("display_name"),
                "latitude": float(top["lat"]),
                "longitude": float(top["lon"]),
                "osm_type": top.get("osm_type"),
                "osm_id": top.get("osm_id"),
                "address": top.get("address", {}),
                "cache_status": cache_status,
                "retrieved_at": retrieved_at,
            }
        return None

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        """Execute geocoding search. Live mode is gated by explicit configuration."""
        query = kwargs.get("origin") or kwargs.get("destination") or kwargs.get("query") or kwargs.get("city") or "Paris"

        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "Nominatim is a rate-limited provider (max 1 req/s) and is DISABLED by default. "
                    "To activate, set TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_NOMINATIM=true. "
                    "For high-volume production, consider self-hosting Nominatim or using Open-Meteo."
                )

            geo = self.geocode(query)
            cache_status = geo.get("cache_status", CacheStatus.MISS.value) if geo else CacheStatus.MISS.value
            retrieved_at = geo.get("retrieved_at", datetime.now(timezone.utc).isoformat()) if geo else datetime.now(timezone.utc).isoformat()
            items: List[ProviderResultItem] = []
            warnings: List[str] = [
                "Nominatim public instance is strictly rate-limited to 1 req/sec. Do not use for bulk queries."
            ]

            if geo:
                item = ProviderResultItem(
                    provider=self.name,
                    category=self.category.value,
                    mode=self.mode.value,
                    retrieved_at=retrieved_at,
                    source_url=NOMINATIM_SOURCE_URL,
                    verification_level=VerificationLevel.CROSS_CHECKED.value,
                    price_status=PriceStatus.ESTIMATED.value,
                    availability_status=AvailabilityStatus.LIVE.value,
                    requires_booking_verification=False,
                    title=f"Nominatim: {geo['display_name']}",
                    description=f"Coordinates: {geo['latitude']:.5f}, {geo['longitude']:.5f}. Type: {geo.get('osm_type', 'place')}",
                    details=geo,
                    attribution=NOMINATIM_ATTRIBUTION,
                    cache_status=cache_status,
                    result_status=ResultStatus.LIVE.value,
                )
                items.append(item)
            else:
                warnings.append(f"No geocoding match found on OpenStreetMap for '{query}'.")

            return ProviderSearchResult(
                provider=self.name,
                category=self.category.value,
                mode=self.mode.value,
                retrieved_at=retrieved_at,
                query={"query": query},
                total_results=len(items),
                items=items,
                source_metadata={
                    "provider": self.name,
                    "category": self.category.value,
                    "attribution": NOMINATIM_ATTRIBUTION,
                    "source_url": NOMINATIM_SOURCE_URL,
                    "cache_status": cache_status,
                    "retrieved_at": retrieved_at,
                },
                warnings=warnings,
                requires_booking_verification=False,
                attribution=NOMINATIM_ATTRIBUTION,
                cache_status=cache_status,
                result_status=ResultStatus.LIVE.value if items else ResultStatus.UNAVAILABLE.value,
                source_url=NOMINATIM_SOURCE_URL,
                verification_level=VerificationLevel.CROSS_CHECKED.value,
            )

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        res.attribution = NOMINATIM_ATTRIBUTION
        res.source_url = NOMINATIM_SOURCE_URL
        res.cache_status = CacheStatus.HIT.value
        res.result_status = ResultStatus.NEEDS_VERIFICATION.value
        res.verification_level = VerificationLevel.CROSS_CHECKED.value
        for it in res.items:
            it.provider = self.name
            it.attribution = NOMINATIM_ATTRIBUTION
            it.source_url = NOMINATIM_SOURCE_URL
        return res
