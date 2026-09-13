---
name: budget-validation
description: Rules and formulas for estimating total trip expenditure, applying multi-currency conversions, factoring safety reserves, and detecting cost overruns.
---

# Budget Validation Skill

## Overview
This skill provides deterministic financial formulas and rules to ensure no hidden costs derail the trip budget.

## Core Rules

1. **Safety Contingency Reserve**:
   - For standard city trips: apply **+10% to +12%** contingency buffer.
   - For road trips or nature expeditions (fuel price fluctuations, adverse weather): apply **+15%** contingency buffer.
   - Formula:
     $$\text{Grand Total} = \text{Total Estimated Cost} \times (1 + \text{Safety Buffer Percentage} / 100)$$

2. **Categorical Completeness**:
   - Ensure none of the core categories are omitted:
     - `transport`: flights, trains, car rental, fuel, tolls, city transit cards.
     - `accommodation`: nights * nightly rate + city tourist taxes.
     - `activities`: museum admissions, guide fees, park permits.
     - `meals`: baseline daily dining allocation * total days * traveler count.
     - `miscellaneous`: emergency cash, local SIM/eSIM, luggage storage.

3. **Cap Enforcement**:
   - If `grand_total > budget_cap`, issue an explicit blocking or warning notification detailing the exact overage and candidate reductions.
