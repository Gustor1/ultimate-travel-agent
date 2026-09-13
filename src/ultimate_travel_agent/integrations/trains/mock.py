"""Deterministic offline rail provider with door-to-door estimates."""

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


class MockTrainProvider(Provider):
    """Deterministic offline rail provider with door-to-door transit modeling."""

    def __init__(self, mode: ProviderMode = ProviderMode.OFFLINE) -> None:
        super().__init__(
            name="mock_train",
            category=ProviderCategory.TRAIN,
            mode=mode,
            requires_api_key=False,
            requires_partner_approval=False,
            requires_payment_setup=False,
            privacy_level="strict_no_pii",
            supported_countries=["FR", "ES", "DE", "IT", "CH", "IS", "*"],
            capabilities=[
                "door_to_door",
                "transfers",
                "price_comparison",
                "booking_required",
                "co2_estimation",
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
            source_url=raw.get("official_booking_url", "https://www.sncf-connect.com"),
            verification_level=VerificationLevel.CROSS_CHECKED.value,
            currency=raw.get("currency", "EUR"),
            price_status=PriceStatus.ESTIMATED.value,
            availability_status=AvailabilityStatus.ESTIMATED.value,
            requires_booking_verification=True,
            title=f"{raw.get('train_type', 'Train')} {raw.get('service_number', '')}: {raw.get('origin')} -> {raw.get('destination')}",
            description=(
                f"{raw.get('transfers', 0)} transfer(s), duration {raw.get('duration_minutes', 180)} min "
                f"(door-to-door ~{raw.get('door_to_door_minutes', 240)} min)"
            ),
            price=raw.get("price_per_person"),
            rating=raw.get("punctuality_rating", 4.5),
            details=raw,
        )

    def search(
        self,
        origin: str = "Paris",
        destination: str = "Barcelona",
        date: str = "2026-10-15",
        time_of_day: str = "morning",
        **kwargs: Any,
    ) -> ProviderSearchResult:
        """Return realistic rail connections."""
        options = [
            {
                "operator": "SNCF / Renfe",
                "train_type": "TGV INOUI",
                "service_number": "9713",
                "origin": f"{origin} (Gare de Lyon)",
                "destination": f"{destination} (Sants)",
                "departure_time": f"{date}T09:42:00",
                "arrival_time": f"{date}T16:34:00",
                "duration_minutes": 412,
                "door_to_door_minutes": 472,  # includes 30 min station arrival + 30 min arrival buffer
                "transfers": 0,
                "seat_reservation_required": True,
                "price_per_person": 89.0,
                "currency": "EUR",
                "co2_kg": 2.4,
                "punctuality_rating": 4.6,
                "official_booking_url": "https://www.sncf-connect.com",
            },
            {
                "operator": "Renfe",
                "train_type": "AVE Direct",
                "service_number": "9731",
                "origin": f"{origin} (Gare de Lyon)",
                "destination": f"{destination} (Sants)",
                "departure_time": f"{date}T14:42:00",
                "arrival_time": f"{date}T21:27:00",
                "duration_minutes": 405,
                "door_to_door_minutes": 465,
                "transfers": 0,
                "seat_reservation_required": True,
                "price_per_person": 105.0,
                "currency": "EUR",
                "co2_kg": 2.2,
                "punctuality_rating": 4.7,
                "official_booking_url": "https://www.renfe.com",
            },
        ]

        items = [self.normalize_result(opt) for opt in options]

        return ProviderSearchResult(
            provider=self.name,
            category=self.category.value,
            mode=self.mode.value,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            query={"origin": origin, "destination": destination, "date": date, "time_of_day": time_of_day},
            total_results=len(items),
            items=items,
            source_metadata=self.get_source_metadata(),
            warnings=["Door-to-door transit times include station arrival and egress buffers."],
            requires_booking_verification=True,
        )
