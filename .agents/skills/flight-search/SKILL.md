---
name: flight-search
description: Use for live flight comparison across exact or flexible dates and nearby gateways with direct-carrier verification and door-to-door costs; use transport-research for non-flight-only journeys.
---

# Flight Search

Read `../../shared/compact-research-protocol.md`, `../../shared/research-methods.md`, `../../shared/evidence-policy.md`, and `../../shared/deterministic-tools.md`. Consult `../../shared/scenario-routing.md` and load only matching separate-ticket, border, accessibility, family, loyalty, or sustainability references.

## Inputs and tools

Require origin region, destination, date windows, `dates_fixed`, `one_way`/round trip/multi-city legs, passengers, baggage, cabin, budget, transit constraints, and `max_flight_stops` (maximum 2). `departure_airports_flexible` defaults false. Use current-source access, artifacts, and packaged commands.

## Adaptive discovery and four passes

Generate stable cells with `flight-search-plan`. Use at least one available comparison engine—Google Flights, Skyscanner, or Trip.com—for discovery; add another only for material coverage, price, route, or confidence gaps. Record every used, unavailable, blocked, or skipped engine in source records. OTAs/aggregators never replace retained direct-airline evidence.

1. **Pass 1 — base:** exact dates/principal airports; choose the single best conforming result as unique `REF`.
2. **Pass 2 — multi-airport:** exact dates and nearby arrival gateways, max 5, with access/onward transport. Cross-border gateways require entry, currency, border, and last-connection checks.
3. **Pass 3 — flexible dates:** principal airports and the complete Cartesian departure × return grid through requested flexibility, up to ±3 days. For one_way, search every valid departure once.
4. **Pass 4 — combined:** every valid flexible pair × every retained gateway, max 5. Use cheap structured discovery for the complete bounded matrix, then direct verification for the Pareto frontier and required fallbacks.

If `dates_fixed: true`, Passes 3–4 are `skipped` with reasons. Multi-city applies coverage per flexible leg and rejects chronological impossibilities. Run `flight-search-coverage`; the `coverage_report` requires `pending: 0`, but recommendation readiness also needs a verified REF and sufficient comparable offers.

## Normalization and verification

Resolve code-shares and duplicate itineraries. Store ordered segments, marketing/operating carrier, flight number, airport code, terminal when known, and offset-aware timestamps. Detect airport changes, date-line effects, overnight connections, and impossible chronology.

Verify retained fare, seats, baggage, payment/cancellation, and schedule on a deep direct-airline URL, not a root homepage. Separate tickets require protection disclosure, immigration, terminal change, baggage reclaim/recheck, check-in closure, missed-connection risk, last recovery, and overnight fallback. Start from a configurable 120-minute buffer and increase it for friction. Never assume through-checked baggage.

Inventories beyond 330 days / 11 months are `unopened inventory` with a range, never a false exact fare.
If inventory is unopened or budget unknown, retain comparable route/date options and pricing inputs. Label `unpriced`; historical schedules do not prove fares.

## Door-to-door decision

Keep the line-by-line breakdown:

`flight + checked_baggage + cabin_baggage + origin_access_cost + destination_transfer + mandatory_fees + overnight + transfer_time_penalty`.

Make value of time configurable. Only when absent, apply the documented default `transfer_time_penalty = 15 EUR/hour` to extra time beyond 4h versus REF; always show raw cost and time separately. Use a verified overnight price or a clearly labeled local estimate. Retain an alternative when it saves at least 20% or EUR 50 versus REF, plus non-dominated robustness/accessibility alternatives. Sort by total while preserving Pass 1 → 4 provenance.

## Fallback

Without current-source access, output the full pending matrix and assumptions only. Keep prices, availability, schedules, baggage, and booking status unverified.

## Outputs

Write cells, offers, segments, formulas, claims, sources, duplicates, and rejection codes. Return `compact-handoff/v2` with IDs and gates only.
