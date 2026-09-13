"""Currency exchange integration adapter."""

from typing import Any, Dict
from ultimate_travel_agent.integrations.base import BaseIntegrationAdapter
from ultimate_travel_agent.models import VerificationLevel


class CurrencyAdapter(BaseIntegrationAdapter):
    """Adapter for currency exchange rates and safety margins."""

    STATIC_RATES_TO_EUR = {
        "EUR": 1.0,
        "USD": 1.08,
        "GBP": 0.86,
        "JPY": 162.5,
        "ISK": 149.0,
        "CHF": 0.96,
        "CAD": 1.48,
    }

    def __init__(self, enabled: bool = False) -> None:
        super().__init__(
            provider_name="CurrencyExchange",
            enabled=enabled,
            requires_api_key=False,
            data_transmitted_policy="Currency codes only.",
        )

    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        from_curr = kwargs.get("from_currency", "EUR").upper()
        to_curr = kwargs.get("to_currency", "USD").upper()
        is_known_from = from_curr in self.STATIC_RATES_TO_EUR
        is_known_to = to_curr in self.STATIC_RATES_TO_EUR
        rate_from = self.STATIC_RATES_TO_EUR.get(from_curr, 1.0)
        rate_to = self.STATIC_RATES_TO_EUR.get(to_curr, 1.0)
        rate = round(rate_to / rate_from, 4)

        is_verified = is_known_from and is_known_to
        warning = None
        if not is_verified:
            missing = [c for c, known in [(from_curr, is_known_from), (to_curr, is_known_to)] if not known]
            warning = f"Currency code(s) {missing} not in static reference table; using unverified 1.0 fallback rate."

        return {
            "from_currency": from_curr,
            "to_currency": to_curr,
            "rate": rate,
            "warning": warning,
            "safety_buffer_recommended_pct": 5.0 if is_verified else 15.0,
            "verification_level": (
                VerificationLevel.OFFICIAL_VERIFIED.value
                if is_verified
                else VerificationLevel.UNVERIFIED.value
            ),
        }

    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        return self.get_mock_data(**kwargs)
