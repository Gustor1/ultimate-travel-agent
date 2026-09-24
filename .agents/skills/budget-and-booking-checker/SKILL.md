---
name: budget-and-booking-checker
description: Use after priced evidence exists to calculate trip scenarios, financial exposure, reserves, and user-controlled booking actions; do not use to discover missing live prices.
---

# Budget and Booking Checker

Read `../../shared/compact-research-protocol.md`, `../../shared/evidence-policy.md`, and `../../shared/deterministic-tools.md`. Consult `../../shared/scenario-routing.md` and load loyalty or family references only when triggered.

## Inputs and tools

Load atomic cost/claim IDs, party allocation, budget caps, risk tolerance, dated exchange rates, and cancellation terms. Use filesystem records and packaged deterministic commands; never calculate totals from prose.

## Method

- Normalize per-person, per-room, per-vehicle, per-night, and one-time costs without double counting. Preserve quantity, tax/fee inclusion, exchange-rate spread, card/payment fee, original currency, and exact decimal arithmetic.
- Classify costs as committed, refundable, non-refundable, optional, or contingent. Keep emergency money separate from spendable budget.
- Produce low/likely/high scenarios while preserving correlated risks such as airfare and lodging moving together. State assumptions; avoid false precision.
- Derive reserve from volatility, refundability, destination risk, and evidence gaps. Use 10–15% only as a documented default when no better policy exists.
- Run `compare-total-cost` for door-to-door alternatives and `revalidation-plan` for expiry tasks. Use `price-watch` only from timestamped observations; never predict a fare from repetition.
- Identify the smallest evidence-backed adjustments needed to meet caps without silently deleting required items.
- A `booking-handoff` needs an item-specific HTTPS URL, unchanged total/currency, quote timestamp/expiry, source IDs, cancellation summary, and explicit user confirmation. The user performs checkout.

## Fallback

Use complete, fresh supplied records without live access. For missing/stale values, mark unverified, calculate defensible bounds or label `unpriced`; list missing fare, room, intercity, activity, and daily costs for revalidation.

## Outputs

Write atomic calculations, scenarios, exposure, decisions, and revalidation tasks. Return `compact-handoff/v2` with budget/check IDs only.
