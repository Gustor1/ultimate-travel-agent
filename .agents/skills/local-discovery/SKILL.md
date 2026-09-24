---
name: local-discovery
description: Use after areas are selected to find local food, neighborhood culture, and photo spots with provenance; use activity-curator for major attractions and ticketed anchors.
---

# Local Discovery

Read `../../shared/compact-research-protocol.md`, `../../shared/research-methods.md`, and `../../shared/evidence-policy.md`. Consult `../../shared/scenario-routing.md` and load only matching accessibility, family, dining, connectivity, sustainability, or regional references.

## Inputs and tools

Require accepted areas/dates, interests, dietary/access needs, budget, crowd preference, and desired categories. Use current-source access, local-language queries, artifacts, and local calculations.

## Method

- Cover each meaningful overnight base with a regional dish, market, or food experience and a photo opportunity near the planned route, unless the user opts out. Expand to two qualified choices per priority category when food or photography is a trip objective; document scarcity instead of padding. Search useful local names and translations.
- Distinguish a local specialty from a specific place to eat it. For dishes record regional connection and what to order; for venues record branch and current operation. For photo spots record viewpoint, light/time, weather, crowd/access constraints, and any photography rules. Never promise a "secret" or crowd-free spot.
- Resolve entity aliases and branches. Detect chains, duplicate listings, relocation, and potentially closed venues before ranking.
- Record exact area, route fit, price band where relevant, known hours/status, discovery date, source type/authority, recency, and verification need. Cluster selections with planned visits; avoid detours for a generic venue or view.
- Separate local relevance from viral popularity. Weight recent recurring patterns more than raw review count; record suspicious bursts, tourism-only signals, and disagreement.
- Tier 5 community evidence supports qualitative patterns only; Tier 6 social evidence discovers candidates only. Verify operational facts on an official venue page or authoritative directory when available. Otherwise require two recent independent signals and keep the status unverified.
- Link each retained dish, venue, and view to source IDs. Use regional or cultural sources for specialty claims; label atmosphere and photo appeal as qualitative judgments.
- Recommendation readiness requires category coverage, current existence evidence, and explicit provenance—not generic popularity.

## Fallback

Without current-source access, provide discovery categories and local-language query plans. Keep prices, hours, popularity, existence, and availability unverified.

## Outputs

Write candidates, aliases, provenance, claims, sources, duplication signals, and rejection codes. Return `compact-handoff/v2` with retained venue IDs.
