# Workflow: Curate Activities and Experiences

## Purpose

Build a diverse, sourced activity pool with realistic slots, crowd strategy, access evidence, and weather/closure alternatives.

Read `../shared/compact-research-protocol.md`; preserve full candidates in artifacts and return `compact-handoff/v2` IDs.

## Agents Involved

- `activity-curator` using `activity-curator`
- `local-discovery-agent` for neighborhood/informal finds only
- `source-verification` for flagged claims only

## Process

1. Define overnight-base × interest × usable-day × indoor/outdoor coverage. Seek a qualified anchor per full sightseeing day and alternatives for fragile anchors; avoid a quota driven only by trip length.
2. Discover in user, English, and useful local-language variants; resolve duplicate venues before ranking.
3. Verify official opening/final-admission times, price, booking release, duration, access features, closure and direct ticket URL for retained items.
4. Test reservation compatibility, queue time, travel time, energy load, and geographic fit. Avoid several fragile items depending on one slot or weather condition.
5. Pair critical outdoor/capacity-limited items with a compatible fallback. Add nearby regional food and photo opportunities from `local-discovery-agent` without overloading the day. Keep community/social leads discovery-only until operationally verified.

## Deliverables

- Thematic candidate and rejection artifacts
- Feasible slot/crowd matrix
- Booking/revalidation and fallback IDs
