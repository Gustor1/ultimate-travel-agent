"""Offline deterministic mock flight provider."""

from datetime import datetime, timezone
import os
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


class MockFlightProvider(Provider):
    """Deterministic offline flight provider simulating realistic flight schedules."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_flight",
            category=ProviderCategory.FLIGHT,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["*"],
            capabilities=[
                "search_roundtrip",
                "search_oneway",
                "filter_stops",
                "sort_price",
                "sort_duration",
                "sort_stops",
                "sort_comfort",
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
            source_url=raw.get("official_booking_url"),
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=f"{raw.get('airline', 'Airline')} {raw.get('flight_number', '')}: {raw.get('origin')} -> {raw.get('destination')}",
            description=f"{raw.get('stops', 0)} stop(s), duration {raw.get('duration_minutes', 120)} min, cabin {raw.get('cabin', 'Economy')}",
            price=raw.get("price_per_person"),
            rating=raw.get("comfort_score", 4.0),
            details=raw,
        )

    def search(
        self,
        origin: str = "PAR",
        destination: str = "BCN",
        departure_date: str = "2026-10-15",
        return_date: Optional[str] = None,
        passengers: int = 1,
        max_budget: Optional[float] = None,
        currency: str = "EUR",
        sort_by: str = "price",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        """Search flight offers deterministically."""
        base_offers = [
            {
                "airline": "Air France",
                "flight_number": "AF1148",
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_time": f"{departure_date}T07:15:00",
                "arrival_time": f"{departure_date}T09:05:00",
                "duration_minutes": 110,
                "stops": 0,
                "price_per_person": 129.0,
                "currency": currency,
                "cabin": "Economy Light",
                "comfort_score": 4.5,
                "official_booking_url": "https://www.airfrance.com",
            },
            {
                "airline": "Vueling",
                "flight_number": "VY8245",
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_time": f"{departure_date}T13:40:00",
                "arrival_time": f"{departure_date}T15:30:00",
                "duration_minutes": 110,
                "stops": 0,
                "price_per_person": 79.0,
                "currency": currency,
                "cabin": "Basic",
                "comfort_score": 3.8,
                "official_booking_url": "https://www.vueling.com",
            },
            {
                "airline": "Iberia Express",
                "flight_number": "IB3712",
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_time": f"{departure_date}T18:00:00",
                "arrival_time": f"{departure_date}T21:45:00",
                "duration_minutes": 225,
                "stops": 1,
                "price_per_person": 95.0,
                "currency": currency,
                "cabin": "Economy",
                "comfort_score": 4.0,
                "official_booking_url": "https://www.iberia.com",
            },
        ]

        if return_date:
            for offer in base_offers:
                offer["return_date"] = return_date
                offer["price_per_person"] = round(offer["price_per_person"] * 1.85, 2)
                offer["is_roundtrip"] = True

        # Filter budget
        if max_budget is not None:
            base_offers = [o for o in base_offers if o["price_per_person"] * passengers <= max_budget]

        # Sort
        if sort_by == "duration":
            base_offers.sort(key=lambda x: x["duration_minutes"])
        elif sort_by == "stops":
            base_offers.sort(key=lambda x: x["stops"])
        elif sort_by == "comfort":
            base_offers.sort(key=lambda x: x["comfort_score"], reverse=True)
        else:  # price
            base_offers.sort(key=lambda x: x["price_per_person"])

        items = [self.normalize_result(o) for o in base_offers]

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers,
                "max_budget": max_budget,
                "currency": currency,
                "sort_by": sort_by,
            },
            total_results=len(items),
            items=items,
            source_metadata=self.get_source_metadata(),
            warnings=["Offline deterministic estimate: verify live seat inventory and prices before payment."],
            requires_booking_verification=True,
        )
