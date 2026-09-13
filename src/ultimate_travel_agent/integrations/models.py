"""Data models and enums for the Travel Integrations and Provider Hub."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProviderMode(str, Enum):
    """Execution mode of a travel provider."""
    OFFLINE = "offline"
    MOCK = "mock"
    LIVE = "live"


class ProviderCategory(str, Enum):
    """Category of travel data provided."""
    FLIGHT = "flight"
    TRAIN = "train"
    HOTEL = "hotel"
    ACTIVITY = "activity"
    REVIEW = "review"
    MAP = "map"
    WEATHER = "weather"
    CURRENCY = "currency"
    GUIDE = "guide"
    SOCIAL = "social"


class PriceStatus(str, Enum):
    """Pricing status of an offer or quote."""
    CONFIRMED = "confirmed"
    ESTIMATED = "estimated"
    NEEDS_VERIFICATION = "needs_verification"


class AvailabilityStatus(str, Enum):
    """Inventory availability status."""
    LIVE = "live"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class HealthStatus(str, Enum):
    """Health check status of a provider."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNCONFIGURED = "unconfigured"
    UNAVAILABLE = "unavailable"


class CacheStatus(str, Enum):
    """Cache lookup status."""
    HIT = "hit"
    MISS = "miss"
    STALE = "stale"


class ResultStatus(str, Enum):
    """Execution freshness status."""
    LIVE = "live"
    UNAVAILABLE = "unavailable"
    NEEDS_VERIFICATION = "needs_verification"


class HealthCheckResult(BaseModel):
    """Standardized health check result."""
    provider: str
    category: str
    status: HealthStatus
    message: str
    is_configured: bool
    latency_ms: Optional[float] = None
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)


class ProviderResultItem(BaseModel):
    """Individual normalized result item from a provider."""
    provider: str
    category: str
    mode: str = ProviderMode.OFFLINE.value
    retrieved_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_url: Optional[str] = None
    verification_level: str = "cross_checked"
    currency: Optional[str] = None
    price_status: str = PriceStatus.ESTIMATED.value
    availability_status: str = AvailabilityStatus.ESTIMATED.value
    requires_booking_verification: bool = True
    title: str = ""
    description: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    attribution: Optional[str] = None
    cache_status: Optional[str] = None
    result_status: Optional[str] = None


class ProviderSearchResult(BaseModel):
    """Standard container for provider query responses."""
    provider: str
    category: str
    mode: str = ProviderMode.OFFLINE.value
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    query: Dict[str, Any] = Field(default_factory=dict)
    total_results: int = 0
    items: List[ProviderResultItem] = Field(default_factory=list)
    source_metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    requires_booking_verification: bool = True
    attribution: Optional[str] = None
    cache_status: Optional[str] = None
    result_status: Optional[str] = None
    source_url: Optional[str] = None


class ProviderError(Exception):
    """Base exception for provider operations."""
    pass


class ProviderConfigurationError(ProviderError):
    """Raised when a live provider is requested but required credentials are missing."""
    pass


class ProviderNetworkError(ProviderError):
    """Raised on external communication failure."""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when an external API rate limit (e.g. 429) is encountered."""
    pass

