"""Base abstract interface for optional external integrations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ultimate_travel_agent.models import VerificationLevel


class BaseIntegrationAdapter(ABC):
    """Abstract base class for external service adapters.

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
