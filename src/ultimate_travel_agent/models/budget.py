"""Budget and expense models for ultimate-travel-agent."""

from typing import Dict, List
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import VerificationLevel


class BudgetCategoryBreakdown(BaseModel):
    """Breakdown of expenses for a specific category."""

    category: str = Field(..., description="Category: transport, accommodation, activities, meals, miscellaneous")
    amount: float = Field(..., description="Estimated cost amount")
    currency: str = Field(default="EUR", description="Currency code")
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.UNVERIFIED,
        description="Overall verification status of prices in this category"
    )
    notes: List[str] = Field(default_factory=list, description="Explanatory notes or cost ranges")


class Budget(BaseModel):
    """Overall consolidated budget for the trip."""

    currency: str = Field(default="EUR", description="Primary currency")
    total_estimated_cost: float = Field(default=0.0, description="Sum of estimated itemized expenses")
    safety_buffer_percentage: float = Field(default=12.0, description="Recommended buffer percentage (10-15%)")
    safety_buffer_amount: float = Field(default=0.0, description="Calculated contingency reserve amount")
    grand_total: float = Field(default=0.0, description="Total including contingency buffer")
    categories: Dict[str, BudgetCategoryBreakdown] = Field(
        default_factory=dict,
        description="Breakdown mapped by category name"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Budget warnings (e.g. over budget cap, unverified estimates)"
    )

    def recalculate(self, budget_cap: float | None = None) -> None:
        """Recalculate totals and check against budget cap."""
        self.total_estimated_cost = sum(cat.amount for cat in self.categories.values())
        self.safety_buffer_amount = round(self.total_estimated_cost * (self.safety_buffer_percentage / 100.0), 2)
        self.grand_total = round(self.total_estimated_cost + self.safety_buffer_amount, 2)
        self.warnings.clear()
        if budget_cap is not None and self.grand_total > budget_cap:
            overage = round(self.grand_total - budget_cap, 2)
            self.warnings.append(
                f"Budget cap exceeded by {overage} {self.currency} (Estimated: {self.grand_total}, Cap: {budget_cap})"
            )
