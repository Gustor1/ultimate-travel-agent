"""Social discovery integrations package."""

from ultimate_travel_agent.integrations.social_discovery.adapter import SocialDiscoveryAdapter
from ultimate_travel_agent.integrations.social_discovery.mock import SocialDiscoveryProvider

__all__ = [
    "SocialDiscoveryAdapter",
    "SocialDiscoveryProvider",
]
