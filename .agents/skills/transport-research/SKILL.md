---
name: transport-research
description: Use for live non-flight or multimodal rail, bus, ferry, driving, rental, and transfer comparison; use flight-search for the complete airfare matrix.
---

# Transport Research

Read `../../shared/compact-research-protocol.md`, `../../shared/research-methods.md`, `../../shared/evidence-policy.md`, and `../../shared/deterministic-tools.md`. Consult `../../shared/scenario-routing.md` and load only matching rail-pass, driving, ferry, separate-ticket, accessibility, family, sustainability, or regional references.

## Inputs and tools

Require endpoints, direction, dates/windows, party, luggage/access needs, acceptable duration, pass/rental constraints, and linked flight IDs. Use current-source access, artifacts, and deterministic cost/time commands.

## Method

- Predeclare viable rail, bus, ferry, car/rental, taxi/shuttle, and local-transfer cells; preserve unavailable and rejected modes with reasons.
- Build a time-expanded journey: origin access, check-in/security, wait, ride, transfer, border/formality, last mile, recovery buffer, first/last usable departure, and frequency. Research both directions when they differ.
- Verify schedule, operating dates, final fare, booking window, luggage, reservations, accessibility features, strike/seasonal caveats, cancellation, and deep direct-operator URL.
- Separate-ticket journeys require protection, re-entry/recheck, terminal changes, last recovery, missed-connection and overnight analysis. Driving includes fuel/charging, tolls, parking, restricted zones, fatigue, insurance/excess, deposit, border and one-way fees.
- Compare a Pareto frontier of true cost, duration, robustness, comfort, luggage, accessibility, and environmental impact. Keep per-person and per-vehicle values distinct; run `compare-total-cost` for arithmetic.
- Recommendation readiness requires at least two genuinely viable modes when the market provides them, current operational evidence, and no hidden infeasible connection.

## Fallback

Without current-source access, provide the complete mode plan and clearly bounded supplied estimates. Keep fares, schedules, restrictions, availability, and booking status unverified.

## Outputs

Write journeys, legs, schedules, formulas, claims, sources, Pareto status, and rejection codes. Return `compact-handoff/v2` with retained route IDs.
