# Workflow: Find Accommodation

## Purpose

Compare neighborhoods and 3–5 qualified properties using exact stay parameters, final cost, real-anchor mobility, quietness, access, and cancellation evidence.

Read `../shared/compact-research-protocol.md`; return `compact-handoff/v2` IDs, gates, and coverage without booking.

## Agents Involved

- `accommodation-researcher` using `accommodation-research`
- `source-verification` only for flagged critical claims

## Process

1. Gate on viable dates/areas. Compare 2–4 neighborhoods using safety/noise evidence and `hotel-mobility` journeys to weighted trip anchors; transport mode is not a fixed ranking.
2. Generate provider tasks with `hotel-search-plan`. Search identical dates, occupancy, room/bed, meals, payment, and cancellation class across the required provider roles.
3. Resolve property aliases and branches. Normalize taxes, mandatory fees, breakfast, deposit, payment timing, and refundable deadline.
4. Verify each retained matching rate and property rule on the direct site. Treat recent room-specific review patterns as qualitative evidence only.
5. Run `hotel-search-coverage`, `hotel-compare`, and `neighborhood-score`. Coverage completion does not imply sufficient comparable evidence.

## Deliverables

- Neighborhood and weighted-mobility assessment
- Comparable 3–5 property shortlist or evidenced scarcity
- Final-price, policy, provider, and gate report
