"""Consolidated Trip model for ultimate-travel-agent."""

from datetime import date
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.accommodation import Accommodation
from ultimate_travel_agent.models.activity import Activity
from ultimate_travel_agent.models.booking import BookingRequirement
from ultimate_travel_agent.models.budget import Budget, BudgetCategoryBreakdown
from ultimate_travel_agent.models.checklist import ChecklistItem
from ultimate_travel_agent.models.destination import Destination
from ultimate_travel_agent.models.enums import TripType, VerificationLevel
from ultimate_travel_agent.models.itinerary import DaySchedule
from ultimate_travel_agent.models.route import InterCityRoute
from ultimate_travel_agent.models.stage import TripStage
from ultimate_travel_agent.models.transport import TransportSegment
from ultimate_travel_agent.models.traveler import Traveler


class Trip(BaseModel):
    """Full travel dossier combining all aspects of a journey."""

    id: str = Field(..., description="Unique trip identifier")
    title: str = Field(..., description="Trip title")
    trip_type: TripType = Field(default=TripType.CITY_TRIP, description="Trip archetype")
    start_date: str = Field(..., description="ISO start date YYYY-MM-DD")
    end_date: str = Field(..., description="ISO end date YYYY-MM-DD")
    currency: str = Field(default="EUR", description="Primary currency ISO code")
    budget_cap: Optional[float] = Field(None, description="Optional target budget limit")
    travelers: List[Traveler] = Field(default_factory=list, description="Travelers in this party")
    destinations: List[Destination] = Field(default_factory=list, description="Target destinations")
    stages: List[TripStage] = Field(default_factory=list, description="Stages or stops of the journey (étapes)")
    transports: List[TransportSegment] = Field(default_factory=list, description="Transit connections")
    inter_city_routes: List[InterCityRoute] = Field(
        default_factory=list,
        description="Multi-option inter-city transit alternatives"
    )
    accommodations: List[Accommodation] = Field(default_factory=list, description="Lodging arrangements")
    activities: List[Activity] = Field(default_factory=list, description="Curated activities and POIs")
    itinerary: List[DaySchedule] = Field(default_factory=list, description="Chronological day schedules")
    checklists: List[ChecklistItem] = Field(default_factory=list, description="Preparation checklist items")
    reservations: List[BookingRequirement] = Field(default_factory=list, description="Booking requirements and reservations (réservations)")
    budget: Optional[Budget] = Field(None, description="Detailed itemized budget breakdown")

    @property
    def total_nights(self) -> int:
        """Calculate total number of nights from start_date to end_date."""
        try:
            d_start = date.fromisoformat(self.start_date)
            d_end = date.fromisoformat(self.end_date)
            diff = (d_end - d_start).days
            return max(0, diff)
        except ValueError:
            return 0

    @property
    def total_days(self) -> int:
        """Calculate total number of calendar days."""
        try:
            d_start = date.fromisoformat(self.start_date)
            d_end = date.fromisoformat(self.end_date)
            if d_end < d_start:
                return 0
            return (d_end - d_start).days + 1
        except ValueError:
            return 0

    def calculate_budget(self, safety_buffer_pct: float = 12.0) -> Budget:
        """Calculate and return itemized budget with safety reserve."""
        num_travelers = max(1, len(self.travelers))
        # Respect per-person vs vehicle/group pricing for transport
        transport_cost = sum(
            t.estimated_cost * (num_travelers if t.effective_is_per_person else 1)
            for t in self.transports
        )
        accommodation_cost = sum(a.total_cost for a in self.accommodations)
        activities_cost = sum(a.estimated_cost for a in self.activities) * num_travelers
        # Estimate meal cost per person per day (default 40 EUR/day if not explicitly modeled)
        days_count = max(1, self.total_days)
        meals_estimate = 40.0 * days_count * num_travelers
        misc_estimate = 15.0 * days_count * num_travelers

        categories: Dict[str, BudgetCategoryBreakdown] = {
            "transport": BudgetCategoryBreakdown(
                category="transport",
                amount=round(transport_cost, 2),
                currency=self.currency,
                verification_level=VerificationLevel.CROSS_CHECKED
            ),
            "accommodation": BudgetCategoryBreakdown(
                category="accommodation",
                amount=round(accommodation_cost, 2),
                currency=self.currency,
                verification_level=VerificationLevel.CROSS_CHECKED
            ),
            "activities": BudgetCategoryBreakdown(
                category="activities",
                amount=round(activities_cost, 2),
                currency=self.currency,
                verification_level=VerificationLevel.CROSS_CHECKED
            ),
            "meals": BudgetCategoryBreakdown(
                category="meals",
                amount=round(meals_estimate, 2),
                currency=self.currency,
                verification_level=VerificationLevel.UNVERIFIED,
                notes=["Estimated standard daily dining allowance"]
            ),
            "miscellaneous": BudgetCategoryBreakdown(
                category="miscellaneous",
                amount=round(misc_estimate, 2),
                currency=self.currency,
                verification_level=VerificationLevel.UNVERIFIED,
                notes=["Local transit passes, tips, emergency cash"]
            )
        }

        budget = Budget(
            currency=self.currency,
            safety_buffer_percentage=safety_buffer_pct,
            categories=categories
        )
        budget.recalculate(budget_cap=self.budget_cap)
        self.budget = budget
        return budget

    def validate_trip_coherence(self) -> List[str]:
        """Perform static quality checks on trip schedule and consistency."""
        issues: List[str] = []

        # 1. Date coherence
        d_start = None
        d_end = None
        try:
            d_start = date.fromisoformat(self.start_date)
            d_end = date.fromisoformat(self.end_date)
            if d_end < d_start:
                issues.append(f"Incoherent dates: end_date ({self.end_date}) precedes start_date ({self.start_date})")
        except ValueError as e:
            issues.append(f"Invalid date format: {e}")

        # 2. Accommodations cover nights
        total_booked_nights = sum(a.total_nights for a in self.accommodations)
        if total_booked_nights != self.total_nights:
            issues.append(
                f"Nights mismatch: Trip duration is {self.total_nights} night(s), but accommodations total {total_booked_nights} night(s)"
            )

        # 3. Destinations referenced
        dest_ids = {d.id for d in self.destinations}
        for a in self.accommodations:
            if a.destination_id not in dest_ids:
                issues.append(f"Accommodation '{a.name}' references unknown destination '{a.destination_id}'")
        for act in self.activities:
            if act.destination_id not in dest_ids:
                issues.append(f"Activity '{act.title}' references unknown destination '{act.destination_id}'")
        for stage in self.stages:
            if stage.destination_id not in dest_ids:
                issues.append(f"Stage '{stage.id}' references unknown destination '{stage.destination_id}'")

        # 4. Itinerary validation
        if self.itinerary:
            if self.total_days > 0 and len(self.itinerary) != self.total_days:
                issues.append(
                    f"Itinerary length mismatch: {len(self.itinerary)} day schedule(s) for a {self.total_days}-day trip"
                )

            known_ref_ids = (
                {a.id for a in self.activities}
                | {t.id for t in self.transports}
                | {acc.id for acc in self.accommodations}
                | {s.id for s in self.stages}
                | {chk.id for chk in self.checklists}
                | {r.id for r in self.reservations}
                | {r.id for r in self.inter_city_routes}
                | {opt.id for r in self.inter_city_routes for opt in r.options}
            )

            expected_day = 1
            for day in self.itinerary:
                if day.destination_id not in dest_ids:
                    issues.append(
                        f"Itinerary day {day.day_number} references unknown destination '{day.destination_id}'"
                    )
                if day.day_number != expected_day:
                    issues.append(
                        f"Itinerary day number sequence error: expected day {expected_day}, got {day.day_number}"
                    )
                expected_day += 1

                if day.date and d_start and d_end:
                    try:
                        d_day = date.fromisoformat(day.date)
                        if d_day < d_start or d_day > d_end:
                            issues.append(
                                f"Itinerary day {day.day_number} date ({day.date}) falls outside trip dates ({self.start_date} to {self.end_date})"
                            )
                    except ValueError:
                        issues.append(f"Itinerary day {day.day_number} has invalid date format: {day.date}")

                for item in day.items:
                    if item.reference_id and item.reference_id not in known_ref_ids:
                        issues.append(
                            f"Itinerary day {day.day_number} item '{item.title}' references unknown entity '{item.reference_id}'"
                        )

        # 5. Check traveler presence
        if not self.travelers:
            issues.append("Missing traveler profile: At least one traveler is required")

        return issues
