# Workflow: Compare Transport Options

## Purpose

Compare all applicable air, rail, bus, ferry, driving, rental, and local-transfer modes door to door using complete coverage and current operator evidence.

Read `../shared/compact-research-protocol.md`; return `compact-handoff/v2` IDs, gates, and exact coverage.

## Agents Involved

- `transport-planner` using `flight-search` and/or `transport-research`
- `source-verification` only for critical, stale, missing, or contradictory claims

## Process

1. Predeclare mode and direction cells. For flights, generate the four-pass matrix with `flight-search-plan`; skip flexibility passes only when dates are fixed.
2. Execute every required cell, normalize duplicate/code-share itineraries, and close coverage with `flight-search-coverage` where applicable.
3. Build time-expanded door-to-door journeys including access, formalities, waits, transfers, last mile, recovery, and first/last usable departure.
4. Normalize baggage, mandatory fees, overnight, per-person/per-vehicle costs, and run `compare-total-cost`.
5. Retain a Pareto frontier across total cost, duration, robustness, access, comfort, luggage, and environmental impact. Verify retained operational claims on direct operator pages.

## Deliverables

- Coverage and gate report
- Door-to-door Pareto comparison
- Official channel and revalidation IDs
