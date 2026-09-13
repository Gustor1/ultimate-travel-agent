"""Wikivoyage open knowledge guide provider (keyless, CC BY-SA 4.0)."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
import urllib.parse

from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.guides.mock import MockGuideProvider
from ultimate_travel_agent.integrations.http_client import KeylessHttpClient
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

WIKIVOYAGE_API_URL = "https://en.wikivoyage.org/w/api.php"
WIKIVOYAGE_ATTRIBUTION = (
    "Text from Wikivoyage available under the Creative Commons Attribution-ShareAlike 4.0 "
    "International License (CC BY-SA 4.0); see https://en.wikivoyage.org for author history."
)
WIKIVOYAGE_COMMUNITY_ADVISORY = (
    "Community-curated editorial guide. While rich in historical and practical context, "
    "operating hours, ticket prices, visa regulations, and safety advisories must be verified with official portals."
)


class WikivoyageProvider(Provider):
    """Wikivoyage destination guide provider (open content, keyless)."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
        http_client: Optional[KeylessHttpClient] = None,
    ) -> None:
        super().__init__(
            name="wikivoyage",
            category=ProviderCategory.GUIDE,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "destination_search",
                "destination_summary",
                "editorial_context",
                "culture_tips",
            ],
        )
        self.endpoint_url = endpoint_url or os.getenv("WIKIVOYAGE_API_URL", WIKIVOYAGE_API_URL)
        self.http_client = http_client or KeylessHttpClient.get_instance()
        self._mock_delegate = MockGuideProvider(mode=mode)

    def is_configured(self) -> bool:
        """Check if live keyless mode is toggled for Wikivoyage."""
        keyless_active = os.getenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "").lower() in ("true", "1", "yes") or \
                         os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")
        enabled = os.getenv("TRAVEL_MCP_ENABLE_WIKIVOYAGE", "true").lower() in ("true", "1", "yes")
        return keyless_active and enabled

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def search_destinations(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Search Wikivoyage for matching destination articles using opensearch."""
        if not query or not query.strip():
            return []

        params = {
            "action": "opensearch",
            "search": query.strip(),
            "limit": limit,
            "namespace": 0,
            "format": "json",
        }
        data, _ = self.http_client.get(
            self.endpoint_url,
            params=params,
            ttl_seconds=86400,  # 24 hours cache
            service_name="wikivoyage",
            min_interval_seconds=0.33,
        )

        results: List[Dict[str, str]] = []
        # OpenSearch returns [query, [titles], [descriptions], [urls]]
        if isinstance(data, list) and len(data) >= 4:
            titles = data[1] if isinstance(data[1], list) else []
            descriptions = data[2] if isinstance(data[2], list) else []
            urls = data[3] if isinstance(data[3], list) else []
            for i in range(len(titles)):
                title = titles[i]
                desc = descriptions[i] if i < len(descriptions) else ""
                url = urls[i] if i < len(urls) else f"https://en.wikivoyage.org/wiki/{urllib.parse.quote(title)}"
                results.append({"title": title, "description": desc, "url": url})

        return results

    def get_destination_summary(self, destination: str) -> Dict[str, Any]:
        """Fetch introductory extract and canonical metadata for a destination article."""
        clean_dest = destination.strip()
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "titles": clean_dest,
            "redirects": 1,
            "format": "json",
        }
        data, cache_status = self.http_client.get(
            self.endpoint_url,
            params=params,
            ttl_seconds=86400,
            service_name="wikivoyage",
            min_interval_seconds=0.33,
        )

        summary_text = ""
        canonical_title = clean_dest
        page_id = None

        if isinstance(data, dict):
            pages = data.get("query", {}).get("pages", {})
            for pid, page_info in pages.items():
                if pid != "-1":
                    page_id = pid
                    canonical_title = page_info.get("title", clean_dest)
                    summary_text = page_info.get("extract", "")
                    break

        canonical_url = f"https://en.wikivoyage.org/wiki/{urllib.parse.quote(canonical_title.replace(' ', '_'))}"
        return {
            "title": canonical_title,
            "page_id": page_id,
            "summary": summary_text,
            "url": canonical_url,
            "found": page_id is not None,
            "cache_status": cache_status,
        }

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        """Query Wikivoyage knowledge. In LIVE mode queries MediaWiki; in OFFLINE/MOCK delegates to mock."""
        city = kwargs.get("city") or kwargs.get("keyword") or kwargs.get("destination") or kwargs.get("query") or "Paris"

        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "Wikivoyage live guide feed is disabled or unconfigured. "
                    "Set TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_WIKIVOYAGE=true."
                )

            summary_info = self.get_destination_summary(city)
            cache_status = summary_info.get("cache_status", CacheStatus.MISS.value)
            warnings: List[str] = [WIKIVOYAGE_COMMUNITY_ADVISORY]

            items: List[ProviderResultItem] = []
            if summary_info["found"]:
                item = ProviderResultItem(
                    provider=self.name,
                    category=self.category.value,
                    mode=self.mode.value,
                    retrieved_at=datetime.now(timezone.utc).isoformat(),
                    source_url=summary_info["url"],
                    verification_level=VerificationLevel.COMMUNITY_RECOMMENDED.value,
                    price_status=PriceStatus.ESTIMATED.value,
                    availability_status=AvailabilityStatus.LIVE.value,
                    requires_booking_verification=False,
                    title=f"Wikivoyage: {summary_info['title']}",
                    description=summary_info["summary"][:600] + ("..." if len(summary_info["summary"]) > 600 else ""),
                    details={
                        "title": summary_info["title"],
                        "full_summary": summary_info["summary"],
                        "url": summary_info["url"],
                        "page_id": summary_info["page_id"],
                        "source_type": "editorial_community_guide",
                        "advisory": WIKIVOYAGE_COMMUNITY_ADVISORY,
                    },
                    attribution=WIKIVOYAGE_ATTRIBUTION,
                    cache_status=cache_status,
                    result_status=ResultStatus.LIVE.value,
                )
                items.append(item)
            else:
                warnings.append(f"No dedicated article found for '{city}' on Wikivoyage.")

            return ProviderSearchResult(
                provider=self.name,
                category=self.category.value,
                mode=self.mode.value,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                query={"city": city},
                total_results=len(items),
                items=items,
                source_metadata={
                    "provider": self.name,
                    "category": self.category.value,
                    "article_url": summary_info["url"],
                    "attribution": WIKIVOYAGE_ATTRIBUTION,
                    "cache_status": cache_status,
                    "verification_level": VerificationLevel.COMMUNITY_RECOMMENDED.value,
                },
                warnings=warnings,
                requires_booking_verification=False,
                attribution=WIKIVOYAGE_ATTRIBUTION,
                cache_status=cache_status,
                result_status=ResultStatus.LIVE.value if items else ResultStatus.UNAVAILABLE.value,
                source_url=summary_info["url"],
            )

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        res.attribution = WIKIVOYAGE_ATTRIBUTION
        res.source_url = f"https://en.wikivoyage.org/wiki/{urllib.parse.quote(city.replace(' ', '_'))}"
        res.cache_status = CacheStatus.HIT.value
        res.result_status = ResultStatus.NEEDS_VERIFICATION.value
        for it in res.items:
            it.provider = self.name
            it.attribution = WIKIVOYAGE_ATTRIBUTION
            it.source_url = res.source_url
        return res
