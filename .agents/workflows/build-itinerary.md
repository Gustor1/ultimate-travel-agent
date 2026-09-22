# Workflow: Build and Optimize Itinerary

## Purpose

Turn accepted evidence IDs into a feasible chronological plan with geographic coherence, traveler-specific pace, slack, and compatible fallbacks. It does not rediscover missing live facts.

Read `../shared/compact-research-protocol.md`; return the itinerary artifact ID via `compact-handoff/v2`.

## Agents Involved

- `itinerary-optimizer` using `itinerary-builder`
- `activity-curator` or `transport-planner` only for a targeted blocked claim

## Process

1. Load accepted IDs and model reservations, opening windows, lodging, meals, transfers, access constraints, and fallbacks as temporal constraints.
2. Prioritize rigid reservations, then run `route-optimize` with sourced travel times to cluster flexible stops.
3. Apply profile-derived slack, maximum walking/activity load, rest, jet-lag recovery, and connection buffers; do not use a universal 20–30 minute cushion.
4. Run `adaptive-day` for weather/energy variants and `disruption-plan` for material cascades. Each fallback must fit its area, window, access, and budget.
5. Leave missing/stale facts as targeted verification tasks. Store rejected sequences and return only itinerary/change IDs.

## Deliverables

- Chronological itinerary artifact
- Route, load, slack, and constraint checks
- Compatible contingency/recovery variants
