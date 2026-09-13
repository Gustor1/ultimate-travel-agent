"""Viator Partner API provider for activities and excursions."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.activities.mock import MockActivityProvider
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    PriceStatus,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
)
from ultimate_travel_agent.models import VerificationLevel


class ViatorActivityProvider(Provider):
    """Viator (Tripadvisor company) activity catalog provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="viator",
            category=ProviderCategory.ACTIVITY,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=True,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["excursions", "sightseeing", "duration_estimates"],
        )
        self.api_key = api_key or os.getenv("VIATOR_API_KEY", "")
        self._mock_delegate = MockActivityProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://www.viator.com",
            verification_level=VerificationLevel.COMMUNITY_RECOMMENDED.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=raw.get("title", "Viator Excursion"),
            description=f"Viator experience: {raw.get('category')}",
            price=raw.get("cost_per_person"),
            rating=raw.get("rating", 4.5),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError("Viator API key not configured. Set VIATOR_API_KEY in .env.")
            raise ProviderConfigurationError("Live API calls to Viator disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
