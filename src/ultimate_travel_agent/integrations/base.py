"""Base abstract provider interface and legacy adapter compatibility."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.health import create_health_report
from ultimate_travel_agent.integrations.models import (
    HealthCheckResult,
    HealthStatus,
    PriceStatus,
    ProviderCategory,
    ProviderConfigurationError,
    ProviderMode,
    ProviderResultItem,
    ProviderSearchResult,
)
from ultimate_travel_agent.models import VerificationLevel


class Provider(ABC):
    """Core modular Provider interface for travel integrations."""

    def __init__(
        self,
        name: str,
        category: ProviderCategory,
        mode: ProviderMode = ProviderMode.OFFLINE,
        requires_api_key: bool = False,
        requires_partner_approval: bool = False,
        requires_payment_setup: bool = False,
        privacy_level: str = "strict_no_pii",
        supported_countries: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        is_mock: bool = False,
    ) -> None:
        self.name = name
        self.category = category
        self.mode = mode
        self.requires_api_key = requires_api_key
        self.requires_partner_approval = requires_partner_approval
        self.requires_payment_setup = requires_payment_setup
        self.privacy_level = privacy_level
        self.supported_countries = supported_countries or ["*"]
        self.capabilities = capabilities or []
        self.is_mock = is_mock or ("mock" in name.lower())

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if necessary environment credentials and partner agreements are configured."""
        pass

    def health_check(self) -> HealthCheckResult:
        """Perform a non-intrusive health and configuration inspection."""
        configured = self.is_configured()
        return create_health_report(
            provider_name=self.name,
            category=self.category.value,
            is_configured=configured,
            mode=self.mode.value,
            details={
                "requires_api_key": self.requires_api_key,
                "requires_partner_approval": self.requires_partner_approval,
                "requires_payment_setup": self.requires_payment_setup,
                "privacy_level": self.privacy_level,
                "capabilities": self.capabilities,
                "supported_countries": self.supported_countries,
            },
        )

    def get_source_metadata(self) -> Dict[str, Any]:
        """Return provenance metadata and verification policies."""
        return {
            "provider": self.name,
            "category": self.category.value,
            "mode": self.mode.value,
            "requires_booking_verification": True,
            "financial_transactions_prohibited": True,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    @abstractmethod
    def normalize_result(self, raw: Any) -> ProviderResultItem:
        """Normalize a raw search item into the standard ProviderResultItem."""
        pass

    @abstractmethod
    def search(self, **kwargs: Any) -> ProviderSearchResult:
        """Execute search in current mode (offline, mock, or live)."""
        pass

    def execute_query(self, mode: Optional[str] = None, **kwargs: Any) -> ProviderSearchResult:
        """Execute search with explicit mode override and credential validation."""
        selected_mode = ProviderMode(str(mode).lower()) if mode else self.mode

        if selected_mode == ProviderMode.LIVE:
            if getattr(self, "is_mock", False) or "mock" in self.name.lower():
                raise ProviderConfigurationError(
                    f"Mock provider '{self.name}' cannot execute in live mode. "
                    f"An official live provider must be configured and activated."
                )
            if not self.is_configured():
                raise ProviderConfigurationError(
                    f"Provider '{self.name}' is not configured for live queries. "
                    f"API credentials or partner approval required. Falling back to offline mode is recommended."
                )

        # Execute search
        prev_mode = self.mode
        try:
            self.mode = selected_mode
            return self.search(**kwargs)
        finally:
            self.mode = prev_mode


# ---------------------------------------------------------------------------
# Backward Compatibility Shim for BaseIntegrationAdapter
# ---------------------------------------------------------------------------

class BaseIntegrationAdapter(ABC):
    """Abstract base class for external service adapters (v1.0 backward compatibility).

    All adapters are DISABLED by default and must provide a graceful mock fallback.
    They must never trigger automated bookings, payments, or write operations.
    """

    def __init__(
        self,
        provider_name: str,
        enabled: bool = False,
        requires_api_key: bool = False,
        api_key: Optional[str] = None,
        data_transmitted_policy: str = "Destination city/country and dates only (no personal traveler PII).",
    ) -> None:
        self.provider_name = provider_name
        self.enabled = enabled
        self.requires_api_key = requires_api_key
        self.api_key = api_key
        self.data_transmitted_policy = data_transmitted_policy

    @abstractmethod
    def get_mock_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Return deterministic local mock data when offline or disabled."""
        pass

    @abstractmethod
    def fetch_live_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Fetch live data from external API if enabled and configured."""
        pass

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute query with automatic graceful fallback to mock data."""
        if not self.enabled:
            data = self.get_mock_data(**kwargs)
            data["_source"] = f"{self.provider_name} (offline mock fallback)"
            if "verification_level" not in data:
                data["verification_level"] = VerificationLevel.CROSS_CHECKED.value
            return data

        if self.requires_api_key and not self.api_key:
            data = self.get_mock_data(**kwargs)
            data["_source"] = f"{self.provider_name} (missing API key fallback)"
            if "verification_level" not in data:
                data["verification_level"] = VerificationLevel.CROSS_CHECKED.value
            return data

        try:
            data = self.fetch_live_data(**kwargs)
            data["_source"] = f"{self.provider_name} (live API)"
            return data
        except Exception as err:
            data = self.get_mock_data(**kwargs)
            data["_source"] = f"{self.provider_name} (error fallback: {type(err).__name__})"
            data["verification_level"] = VerificationLevel.UNVERIFIED.value
            return data
