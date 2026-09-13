"""Health checking utilities for travel data providers."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ultimate_travel_agent.integrations.models import (
    HealthCheckResult,
    HealthStatus,
)


def create_health_report(
    provider_name: str,
    category: str,
    is_configured: bool,
    mode: str,
    message: Optional[str] = None,
    latency_ms: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None,
) -> HealthCheckResult:
    """Create a standardized HealthCheckResult for a provider."""
    if not is_configured and mode == "live":
        status = HealthStatus.UNCONFIGURED
        msg = message or f"Provider '{provider_name}' requires credentials for live queries."
    else:
        status = HealthStatus.HEALTHY
        msg = message or f"Provider '{provider_name}' operating in {mode} mode."

    return HealthCheckResult(
        provider=provider_name,
        category=category,
        status=status,
        message=msg,
        is_configured=is_configured,
        latency_ms=latency_ms,
        checked_at=datetime.now(timezone.utc).isoformat(),
        details=details or {},
    )
