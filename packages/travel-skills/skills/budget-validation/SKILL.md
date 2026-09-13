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

4. **Multi-Currency Conversions & ECB Reference Rates**:
   - Conversions must cite the official European Central Bank (`ECBCurrencyProvider`) reference rate publication date.
   - Bank / Credit Card Markup Advisory: Always notify the traveler that ECB rates represent institutional benchmark mid-market rates. Retail credit card purchases and foreign ATM withdrawals typically incur an additional **+1.5% to +3.5% markup** plus transaction fees.
   - If a target currency is absent from the official ECB feed, use a static fallback rate and flag it as an estimated rate (`VerificationLevel.CROSS_CHECKED`).

