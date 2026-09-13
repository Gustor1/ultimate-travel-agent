"""European Central Bank (ECB) currency exchange rate provider (keyless open reference data)."""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET

from ultimate_travel_agent.integrations.base import Provider
from ultimate_travel_agent.integrations.currency.mock import MockCurrencyProvider
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

ECB_DAILY_XML_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
ECB_ATTRIBUTION = (
    "Source: European Central Bank (ECB) euro reference exchange rates "
    "(https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/)"
)
ECB_SOURCE_URL = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"

# Local static fallback rates against EUR for currencies that might be absent from daily feed or during offline mode
LOCAL_RATE_FALLBACK: Dict[str, float] = {
    "EUR": 1.0,
    "USD": 1.085,
    "GBP": 0.842,
    "CHF": 0.955,
    "JPY": 162.5,
    "CAD": 1.482,
    "AUD": 1.625,
    "SEK": 11.25,
    "NOK": 11.65,
    "DKK": 7.46,
    "PLN": 4.28,
    "CZK": 25.10,
    "HUF": 395.0,
    "ISK": 150.2,
    "SGD": 1.42,
    "HKD": 8.48,
    "NZD": 1.78,
    "MXN": 21.5,
    "BRL": 6.10,
    "ZAR": 19.8,
}


class ECBCurrencyProvider(Provider):
    """European Central Bank official reference exchange rates provider (public, keyless)."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        mode: ProviderMode = ProviderMode.OFFLINE,
        http_client: Optional[KeylessHttpClient] = None,
    ) -> None:
        super().__init__(
            name="ecb_currency",
            category=ProviderCategory.CURRENCY,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "euro_reference_rates",
                "cross_currency_rates",
                "convert_amount",
                "rate_publication_date",
            ],
        )
        self.endpoint_url = endpoint_url or os.getenv("ECB_FEED_URL", ECB_DAILY_XML_URL)
        self.http_client = http_client or KeylessHttpClient.get_instance()
        self._mock_delegate = MockCurrencyProvider(mode=mode)

    def is_configured(self) -> bool:
        """Check if live keyless mode is toggled for ECB."""
        keyless_active = os.getenv("TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS", "").lower() in ("true", "1", "yes") or \
                         os.getenv("ENABLE_LIVE_KEYLESS_APIS", "").lower() in ("true", "1", "yes")
        enabled = os.getenv("TRAVEL_MCP_ENABLE_ECB", "true").lower() in ("true", "1", "yes")
        return keyless_active and enabled

    def normalize_result(self, raw: Dict[str, Any]) -> ProviderResultItem:
        return self._mock_delegate.normalize_result(raw)

    def fetch_ecb_rates(self) -> Tuple[Dict[str, float], str, str]:
        """Fetch and parse official ECB daily reference exchange rates XML.

        Returns:
            Tuple of (rates_dict, rate_date_str, cache_status)
        """
        xml_content, cache_status = self.http_client.get(
            self.endpoint_url,
            ttl_seconds=43200,  # 12 hours cache
            service_name="ecb",
            min_interval_seconds=0.5,
            parse_json=False,
        )

        rates: Dict[str, float] = {"EUR": 1.0}
        rate_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if not isinstance(xml_content, str):
            raise ProviderConfigurationError("Expected XML string content from ECB feed.")

        try:
            root = ET.fromstring(xml_content)
            # Traverse namespace-agnostic tags ending in 'Cube'
            for elem in root.iter():
                if elem.tag.endswith("Cube"):
                    if "time" in elem.attrib:
                        rate_date = elem.attrib["time"]
                    if "currency" in elem.attrib and "rate" in elem.attrib:
                        curr = elem.attrib["currency"].upper()
                        try:
                            rates[curr] = float(elem.attrib["rate"])
                        except ValueError:
                            pass
        except ET.ParseError as parse_err:
            raise ProviderConfigurationError(f"Failed to parse ECB XML rates: {str(parse_err)}") from parse_err

        return rates, rate_date, cache_status

    def convert_amount(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        custom_rate: Optional[float] = None,
    ) -> ProviderSearchResult:
        """Convert amount between currencies with ECB reference rates or manual override."""
        from_curr = from_currency.strip().upper()
        to_curr = to_currency.strip().upper()
        warnings: List[str] = []

        if custom_rate is not None and custom_rate > 0:
            rate = custom_rate
            rate_date = "custom_override"
            cache_status = CacheStatus.HIT.value
            verif_level = VerificationLevel.CROSS_CHECKED.value
            res_status = ResultStatus.LIVE.value
        else:
            try:
                rates, rate_date, cache_status = self.fetch_ecb_rates()
            except Exception as err:
                # Network or parsing failure fallback
                rates = LOCAL_RATE_FALLBACK
                rate_date = "2026-09-01 (fallback)"
                cache_status = CacheStatus.STALE.value
                warnings.append(f"Live ECB feed unavailable ({type(err).__name__}); static fallback table used.")

            from_rate = rates.get(from_curr)
            to_rate = rates.get(to_curr)

            if from_rate is None:
                from_rate = LOCAL_RATE_FALLBACK.get(from_curr, 1.0)
                warnings.append(f"Currency '{from_curr}' missing from ECB feed; static reference estimate applied.")

            if to_rate is None:
                to_rate = LOCAL_RATE_FALLBACK.get(to_curr, 1.0)
                warnings.append(f"Currency '{to_curr}' missing from ECB feed; static reference estimate applied.")

            # Calculate cross rate: EUR base
            rate = to_rate / from_rate
            verif_level = (
                VerificationLevel.OFFICIAL_VERIFIED.value
                if not warnings
                else VerificationLevel.CROSS_CHECKED.value
            )
            res_status = ResultStatus.LIVE.value

        converted_amount = round(amount * rate, 2)
        advisory = (
            "Official European Central Bank (ECB) reference rate. "
            "Indicative only: commercial card and bank exchange rates typically incur 1.5% - 3.5% markup."
        )

        item = ProviderResultItem(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            source_url=ECB_SOURCE_URL,
            verification_level=verif_level,
            currency=to_curr,
            price_status=PriceStatus.CONFIRMED.value if custom_rate else PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.LIVE.value,
            requires_booking_verification=False,
            title=f"{amount:.2f} {from_curr} = {converted_amount:.2f} {to_curr}",
            description=f"Exchange rate: 1 {from_curr} = {rate:.4f} {to_curr} as of {rate_date}. {advisory}",
            price=converted_amount,
            details={
                "amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "exchange_rate": rate,
                "converted_amount": converted_amount,
                "rate_date": rate_date,
                "is_reference_rate": True,
                "advisory": advisory,
            },
            attribution=ECB_ATTRIBUTION,
            cache_status=cache_status,
            result_status=res_status,
        )

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={
                "amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "custom_rate": custom_rate,
            },
            total_results=1,
            items=[item],
            source_metadata={
                "provider": self.name,
                "category": self.category.value,
                "rate_date": rate_date,
                "attribution": ECB_ATTRIBUTION,
                "source_url": ECB_SOURCE_URL,
                "cache_status": cache_status,
            },
            warnings=warnings,
            requires_booking_verification=False,
            attribution=ECB_ATTRIBUTION,
            cache_status=cache_status,
            result_status=res_status,
            source_url=ECB_SOURCE_URL,
        )

    def search(self, **kwargs: Any) -> ProviderSearchResult:
        """Perform currency conversion or query reference rates."""
        amount = float(kwargs.get("amount", 100.0))
        from_curr = kwargs.get("from_currency") or kwargs.get("from") or "EUR"
        to_curr = kwargs.get("to_currency") or kwargs.get("to") or "USD"
        custom_rate = kwargs.get("custom_rate")

        if self.mode == ProviderMode.LIVE:
            if not self.is_configured():
                raise ProviderConfigurationError(
                    "ECB live currency feed is disabled or unconfigured. "
                    "Set TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=true and TRAVEL_MCP_ENABLE_ECB=true."
                )
            return self.convert_amount(
                amount=amount,
                from_currency=from_curr,
                to_currency=to_curr,
                custom_rate=custom_rate,
            )

        res = self._mock_delegate.search(**kwargs)
        res.provider = self.name
        res.attribution = ECB_ATTRIBUTION
        res.source_url = ECB_SOURCE_URL
        res.cache_status = CacheStatus.HIT.value
        res.result_status = ResultStatus.NEEDS_VERIFICATION.value
        for it in res.items:
            it.provider = self.name
            it.attribution = ECB_ATTRIBUTION
            it.source_url = ECB_SOURCE_URL
        return res
