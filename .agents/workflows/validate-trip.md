# Workflow: Validate Trip Quality and Feasibility

## Purpose

Audit `TravelDossier v1` structure, arithmetic, feasibility, evidence, contingencies, and readiness without silently redoing research.

Read `../shared/compact-research-protocol.md`; write findings once and return `compact-handoff/v2` IDs.

## Agents Involved

- `quality-controller` using `travel-quality-control`
- `budget-analyst` or `source-verification` only for targeted corrections

## Process

1. Run `validate-dossier`; check schemas, unique IDs, links, revisions, duplicates, and orphans.
2. Recalculate typed totals, quantities, exchange rates, reserves, and door-to-door formulas.
3. Test chronology, opening windows, connections, check-in, geography, walking/energy, rest, access, lodging nights, and fallback compatibility.
4. Audit claim atomicity, authority, independence, applicability, freshness, and conflicts.
5. Evaluate `coverage_complete`, `evidence_sufficient`, `recommendation_ready`, and `booking_ready` independently; `pending: 0` cannot imply later gates.
6. Red-team a delay, closure, bad weather, payment/cancellation mismatch, and stale critical claim. After correction, rerun affected findings and dependencies only.

## Deliverables

- Severity-ranked finding IDs and corrections
- Gate report and `APPROVED`, `MODIFICATIONS_REQUIRED`, or `BLOCKED` decision
