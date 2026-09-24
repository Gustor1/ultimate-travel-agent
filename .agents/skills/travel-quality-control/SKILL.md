---
name: travel-quality-control
description: Use as the final or post-change audit of itinerary feasibility, arithmetic, evidence, pacing, contingencies, and readiness; do not silently redo specialist research.
---

# Travel Quality Control

Read `../../shared/compact-research-protocol.md`, `../../shared/evidence-policy.md`, and `../../shared/deterministic-tools.md`. Resolve active scenario obligations through `../../shared/scenario-routing.md`; never load inactive references.

## Inputs and tools

Load dossier/artifact IDs, coverage and gate reports, accepted decisions, claims/sources/costs, itinerary constraints, prior findings, changed IDs, and readiness target. Use deterministic validators and calculations.

## Method

- **Structure:** validate schemas, IDs, links, revisions, duplicates, orphans, and ownership. Run `validate-run`; run `validate-dossier` for JSON/YAML only. Markdown cannot pass dossier validation.
- **Calculation:** independently recalculate subtotals, quantities, currency conversion, reserves, and door-to-door totals from atomic records.
- **Feasibility:** test chronology, opening windows, connection/check-in buffers, geography, walking/energy limits, meals/rest, night safety, accessibility, lodging nights, and fallback compatibility.
- **Evidence:** test claim atomicity, authority, independence, applicability, freshness, conflicts, active-scenario obligations, and all four coverage/readiness gates. `pending: 0` alone never passes.
- Reject `recommendation_ready` without coverage, evidence, artifacts, and comparable options. Record machine-check results.
- Red-team representative failures: delay, closure, bad weather, missed connection, payment/cancellation mismatch, and one critical claim becoming stale. Require recovery for material cascades.
- Write severity, affected/dependent IDs, evidence, required correction, and `APPROVED`, `MODIFICATIONS_REQUIRED`, or `BLOCKED`. After a correction, rerun affected checks and dependencies rather than the full unaffected dossier.

## Fallback

Live access is unnecessary for structural, arithmetic, and internal-feasibility checks. If external freshness cannot be rechecked, preserve those findings as unverified and refuse booking readiness without inventing facts.

## Outputs

Write findings and check results; never duplicate the dossier. Return `compact-handoff/v2` with finding IDs, blockers, gates, and decision.
