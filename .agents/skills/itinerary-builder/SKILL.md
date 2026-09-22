---
name: itinerary-builder
description: Use after transport, lodging, activities, and opening windows are established to build a feasible chronological itinerary; do not use it to invent or rediscover missing live facts.
---

# Itinerary Builder

Read `../../shared/compact-research-protocol.md`, `../../shared/evidence-policy.md`, and `../../shared/deterministic-tools.md`. Load accessibility, heat, or altitude scenario references only when relevant.

## Inputs and tools

Load accepted activity, lodging, route, meal, constraint, opening-window, fallback, and traveler-profile IDs plus arrival/departure times. Use artifacts and deterministic route/time commands.

## Method

- Model fixed reservations, opening windows, transfers, meals, rest, check-in/out, and fallbacks as temporal constraints. Never overlap blocks or schedule a closed item.
- Prioritize rigid reservations, then cluster flexible stops geographically. Run `route-optimize`; use sourced travel times rather than straight-line distance for final feasibility.
- Apply the profile's maximum activity hours, walking budget, mobility needs, pace, and jet-lag recovery. “2–3 major visits” is only a default for an unspecified balanced profile.
- Preserve visible slack for queues and disruptions instead of filling 100% of the day. Validate every connection and cascading effect of delay.
- Use `adaptive-day` for weather/energy variants and `disruption-plan` for recovery. A fallback must fit the same approximate area, time window, access needs, and budget.
- Link every factual block to existing claim/source IDs. Record rejected sequences and reasons without copying evidence into the handoff.

## Fallback

Current-source access is unnecessary when upstream records are complete and fresh. For missing or stale windows, leave an unscheduled placeholder and targeted verification task rather than inventing feasibility.

## Outputs

Write the full itinerary, constraints, route analysis, slack, variants, and rejection records. Return `compact-handoff/v2` with itinerary/change IDs.
