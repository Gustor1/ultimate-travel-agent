---
name: activity-curator
description: Use to discover or date-refine cultural, historical, outdoor, and culinary activities with visit logistics and backups; use local-discovery instead for neighborhood venues and informal finds.
---

# Activity Curator

Read `../../shared/compact-research-protocol.md`, `../../shared/research-methods.md`, and `../../shared/evidence-policy.md`. Consult `../../shared/scenario-routing.md` and load only matching regional, accessibility, family, dining, sustainability, heat, or altitude references.

## Inputs and tools

Require destination/areas, date window, interests, pace, party/access needs, budget, crowd tolerance, and transport anchors. Use current-source access, artifacts, and deterministic time calculations.

## Method

- Build coverage by overnight base × stated interest × usable day × indoor/outdoor. Qualify an anchor for each full sightseeing day except intentional rest days, and a compatible alternative for each fragile anchor. Expand only where meaningful choices are missing; document scarcity instead of padding.
- For each retained experience record what makes it distinctive, realistic time on site, best time for light or crowds when relevant, and its fit with the surrounding day. Local food venues and informal photo spots belong to `local-discovery`; ticketed tours and attractions stay here.
- Search in local language when useful. For retained items verify official opening days/hours, timed-entry window, final admission, price, booking release, duration, accessibility features, seasonal closure, and direct ticket URL as atomic claims.
- Record queue time separately from visit length, travel time from realistic anchors, geographic cluster, energy load, and the best evidence-backed low-crowd slot.
- Check reservation compatibility across days before recommending. Avoid stacking several weather-sensitive, high-energy, or non-refundable activities into one fragile window.
- Give every critical outdoor or capacity-limited item a compatible rain/closure fallback in the same area and time window. Community/social leads remain discovery-only until verified.
- Recommendation readiness requires category coverage, feasible slots, and primary evidence for operational claims—not merely `pending: 0`.

## Fallback

Without current-source access, use supplied evidence and produce categories plus exact verification tasks. Keep prices, hours, accessibility, capacity, and booking status unverified.

## Outputs

Write full candidates, claims, sources, slots, fallbacks, and rejection codes to artifacts. Return `compact-handoff/v2` with retained IDs.
