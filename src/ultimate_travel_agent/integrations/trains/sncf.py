"""SNCF Open Data and Connect rail API provider."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
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
from ultimate_travel_agent.integrations.trains.mock import MockTrainProvider
from ultimate_travel_agent.models import VerificationLevel


class SNCFTrainProvider(Provider):
    """SNCF rail timetable and connections provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
    ) -> None:
        super().__init__(
            name="sncf_train",
            category=ProviderCategory.TRAIN,
            mode=mode,
            requires_api_key=True,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["FR", "ES", "DE", "IT", "CH", "BE", "NL", "GB"],
            capabilities=["door_to_door", "transfers", "seat_booking_notice"],
        )
        self.api_key = api_key or os.getenv("SNCF_API_KEY", "")
        self._mock_delegate = MockTrainProvider(mode=mode)

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url="https://www.sncf-connect.com",
            verification_level=(
                VerificationLevel.OFFICIAL_VERIFIED.value
                if self.mode == ProviderMode.LIVE
                else VerificationLevel.CROSS_CHECKED.value
            ),
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=f"{raw.get('train_type', 'TGV')}: {raw.get('origin')} -> {raw.get('destination')}",
            description=f"Duration: {raw.get('duration_minutes', 180)} min, {raw.get('transfers', 0)} transfer(s)",
            price=raw.get("price_per_person"),
            details=raw,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError("SNCF API key not configured. Set SNCF_API_KEY in .env.")
            raise ProviderConfigurationError("Live API calls to SNCF disabled during development/testing.")

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        for it in res.items:
            it.provider = self.name
        return res
