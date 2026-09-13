"""Wikivoyage open knowledge provider (CC BY-SA 4.0)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.guides.mock import MockGuideProvider
from ultimate_travel_agent.integrations.models import (
    AvailabilityStatus,
    PriceStatus,
    ProviderCategory,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
)
from ultimate_travel_agent.models import VerificationLevel


class WikivoyageProvider(Provider):
    """Wikivoyage editorial destination guide provider (open content, keyless)."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="wikivoyage",
            category=ProviderCategory.GUIDE,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=["destination_overview", "culture", "safety_tips"],
        )
        self._mock_delegate = MockGuideProvider(mode=mode)

    def is_configured(self) -> bool:
        return True

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
