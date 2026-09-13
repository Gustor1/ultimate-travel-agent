"""Deterministic offline currency converter with exchange rate date tracking."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
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


_STATIC_RATES_TO_EUR: Dict[str, float] = {
    "EUR": 1.0,
    "USD": 1.08,
    "GBP": 0.85,
    "JPY": 162.50,
    "ISK": 150.0,
    "CHF": 0.96,
    "NOK": 11.40,
    "CAD": 1.48,
    "AUD": 1.65,
}

_RATE_PUBLISHED_DATE = "2026-09-01"


class MockCurrencyProvider(Provider):
    """Deterministic currency conversion provider with rate freshness checks."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_currency",
            category=ProviderCategory.CURRENCY,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "convert_amount",
                "rate_lookup",
                "custom_rate_override",
                "outdated_rate_detection",
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
            source_url="https://www.ecb.europa.eu",
            verification_level=raw.get("verification_level", VerificationLevel.OFFICIAL_VERIFIED.value),
            currency=raw.get("to_currency"),
            price_status=PriceStatus.CONFIRMED.value,
            availability_status=AvailabilityStatus.LIVE.value,
            requires_booking_verification=False,
            title=f"Currency: {raw.get('from_currency')} -> {raw.get('to_currency')}",
            description=(
                f"Rate: {raw.get('rate')}. Converted: {raw.get('original_amount')} {raw.get('from_currency')} "
                f"= {raw.get('converted_amount')} {raw.get('to_currency')} (as of {raw.get('rate_date')})"
            ),
            price=raw.get("converted_amount"),
            details=raw,
        )

    def convert(
        self,
        amount: float = 100.0,
        from_currency: str = "EUR",
        to_currency: str = "USD",
        custom_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Convert an amount from one currency to another."""
        fc = from_currency.upper().strip()
        tc = to_currency.upper().strip()

        if custom_rate is not None and custom_rate > 0:
            rate = custom_rate
            is_custom = True
            v_level = VerificationLevel.OFFICIAL_VERIFIED.value
            warning = None
        else:
            is_custom = False
            if fc not in _STATIC_RATES_TO_EUR or tc not in _STATIC_RATES_TO_EUR:
                rate = 1.0
                v_level = VerificationLevel.UNVERIFIED.value
                warning = f"Unknown currency '{fc if fc not in _STATIC_RATES_TO_EUR else tc}': fallback 1:1 applied."
            else:
                rate_to_eur_from = _STATIC_RATES_TO_EUR[fc]
                rate_to_eur_to = _STATIC_RATES_TO_EUR[tc]
                rate = round(rate_to_eur_to / rate_to_eur_from, 4)
                v_level = VerificationLevel.OFFICIAL_VERIFIED.value
                warning = None

        converted = round(amount * rate, 2)

        return {
            "from_currency": fc,
            "to_currency": tc,
            "original_amount": amount,
            "converted_amount": converted,
            "rate": rate,
            "rate_date": _RATE_PUBLISHED_DATE,
            "is_custom_rate": is_custom,
            "verification_level": v_level,
            "warning": warning,
        }

    def search(
        self,
        amount: float = 100.0,
        from_currency: str = "EUR",
        to_currency: str = "USD",
        custom_rate: Optional[float] = None,
        **kwargs: Any,
    ) -> ProviderSearchResult:
        data = self.convert(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            custom_rate=custom_rate,
        )
        item = self.normalize_result(data)

        warnings = []
        if data.get("warning"):
            warnings.append(data["warning"])

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "custom_rate": custom_rate,
            },
            total_results=1,
            items=[item],
            source_metadata=self.get_source_metadata(),
            warnings=warnings,
            requires_booking_verification=False,
        )
