---
name: accommodation-research
description: Use after candidate dates and areas are known to compare neighborhoods and lodging with exact room, total-price, transit, accessibility, and policy evidence; do not use for general destination inspiration.
---

# Accommodation Research

Read `../../shared/compact-research-protocol.md`, `../../shared/research-methods.md`, `../../shared/evidence-policy.md`, and `../../shared/deterministic-tools.md`. Consult `../../shared/scenario-routing.md` and load only matching accessibility or regional references.

## Inputs and tools

Require dates, occupancy/rooms, budget basis, itinerary anchors, mobility/quietness/amenity needs, and cancellation tolerance. Use current-source access, filesystem artifacts, and packaged deterministic commands.

## Method

1. Compare 2–4 viable neighborhoods using dated safety/noise evidence and weighted journeys to actual trip anchors. Mode labels alone do not determine quality: record named metro, tram, commuter rail, and bus stops, walking time, frequency, transfers, service hours, and step-free fit.
2. Generate a coverage plan with `hotel-search-plan`; discover 3–5 qualified properties across Google Hotels, Booking.com, and Agoda or Trip.com, adapting unavailable providers by region without silently reducing provider roles.
3. Resolve duplicate entities across names/platforms. Compare the same occupancy, dates, room/bed, meals, payment timing, and cancellation class. Reject incomparable rates rather than averaging them.
4. Normalize final stay cost: `base_rate + city_tax + cleaning_fee + service_fee + breakfast_cost + mandatory_charges`. Preserve original currency, inclusions, deposit, and `free_until` cancellation deadline.
5. Verify each retained matching room/rate on the property site. Prefer official direct when equal to or cheaper; keep an intermediary only for a documented total or policy advantage.
6. Separate property rules from rate-plan rules. Record availability, check-in/out, accessible-room features, foreign-guest eligibility where relevant, and room-specific quietness patterns using recent reviews only as qualitative evidence.
7. Run `hotel-search-coverage`, `hotel-compare`, `hotel-mobility`, and `neighborhood-score` as applicable. `pending: 0` closes execution; recommendation readiness additionally requires comparable totals, transit evidence, and at least three qualified properties unless scarcity is evidenced.

Store all candidates and rejection codes; hand off retained IDs only.

## Fallback

Without current-source access, compare only supplied fresh records. Otherwise provide area criteria and a pending coverage plan; keep live price, availability, policy, and walking claims unverified.

## Outputs

Write property, rate, transit, claim, source, rejection, and coverage records. Return `compact-handoff/v2` from the shared protocol.
