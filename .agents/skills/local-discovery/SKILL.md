---
name: local-discovery
description: Use after areas are selected to find neighborhood food, markets, culture, and emerging venues with provenance; use activity-curator for major attractions and ticketed itinerary anchors.
---

# Local Discovery

Read `../../shared/compact-research-protocol.md`, `../../shared/research-methods.md`, and `../../shared/evidence-policy.md`. Consult `../../shared/scenario-routing.md` and load only matching accessibility, family, dining, connectivity, sustainability, or regional references.

## Inputs and tools

Require accepted areas/dates, interests, dietary/access needs, budget, crowd preference, and desired categories. Use current-source access, local-language queries, artifacts, and local calculations.

## Method

- Define coverage by neighborhood × requested category and seek at least two qualified, non-duplicate candidates per requested category in each relevant area when the market supports them. Search in the user's language, English, and useful local names/transliterations; document scarcity instead of padding.
- Resolve entity aliases and branches. Detect chains, duplicate listings, relocation, and potentially closed venues before ranking.
- Record exact area, why it fits, price band, known hours/status, discovery date, source type/authority, recency, and verification need. Spread retained candidates geographically unless clustering is requested.
- Separate local relevance from viral popularity. Weight recent recurring patterns more than raw review count; record suspicious bursts, tourism-only signals, and disagreement.
- Tier 5 community evidence supports qualitative patterns only; Tier 6 social evidence discovers candidates only. Verify operational facts on an official venue page or authoritative directory when available. Otherwise require two recent independent signals and keep the status unverified.
- Recommendation readiness requires category coverage, current existence evidence, and explicit provenance—not generic popularity.

## Fallback

Without current-source access, provide discovery categories and local-language query plans. Keep prices, hours, popularity, existence, and availability unverified.

## Outputs

Write candidates, aliases, provenance, claims, sources, duplication signals, and rejection codes. Return `compact-handoff/v2` with retained venue IDs.
