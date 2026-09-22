---
name: source-verification
description: Use to audit critical, stale, missing, or contradictory travel claims against authoritative sources; do not repeat successful broad discovery or reverify unchanged current evidence.
---

# Source Verification

Read `../../shared/compact-research-protocol.md`, `../../shared/research-methods.md`, and `../../shared/evidence-policy.md`.

## Inputs and tools

Load assigned claim/source IDs, criticality, applicability, freshness requirement, candidate URLs, dates, and artifacts. Use current-source access and deterministic schema/deduplication checks.

## Method

- Split compound statements into atomic claims before verification. Audit only critical, stale, missing, contradictory, changed, or sampled non-critical claims; reuse unchanged current owner evidence.
- Verify exact dates, traveler category, jurisdiction, product/rate, and direction on the responsible direct page. A root domain, search result, or generic homepage does not verify an entity.
- Record normalized fact, original and canonical URL, source type, authority, independence group, `retrieved_at`, effective period, `expires_at`, status, and confidence rationale.
- Cross-check critical, ambiguous, volatile, or contradictory claims using an independent authoritative origin when available. Two pages using one upstream feed are not independent.
- Resolve contradictions by applicability, responsibility, and effective date. Preserve both claims; if material uncertainty remains, block rather than average or silently choose.
- Update by stable ID/revision. Record dead, redirected, blocked, or unavailable pages and the exact remaining verification action.

## Fallback

Without current-source access, validate structure and freshness only; mark affected claims `unverified` or `stale` and keep their prior evidence intact.

## Outputs

Write updated atomic claims, sources, conflicts, and checks. Return `compact-handoff/v2` with changed IDs and blockers only.
