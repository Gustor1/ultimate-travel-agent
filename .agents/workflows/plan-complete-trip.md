# Workflow: Plan Complete Trip

## Purpose

Produce one sourced `TravelDossier v1` through an evidence-preserving, token-efficient workflow. Research breadth is preserved; repeated context and duplicate source work are removed.

## Agents Involved

- `travel-orchestrator` leads.
- Applicable destination, transport, activity, safety, accommodation, local, budget, itinerary, verification, and quality specialists are selected dynamically.
- `mcp-skill-auditor` runs only when an external component is proposed, never for ordinary planning.

## Input / Output Contract

Input is a privacy-minimal brief and runtime capability status. Intermediate stages use `compact-handoff/v2`; final output is one validated `TravelDossier v1`.

Read `../shared/compact-research-protocol.md`. Start every specialist with isolated context and its own artifact shard. Never forward full conversation history, transcripts, raw pages, or dossier fragments. Never prune a required query, candidate, source check, or search cell.

## Process

1. Create/reuse the run ID and brief fingerprint. Resolve active scenario IDs from explicit brief facts, then resolve only materially blocking gaps; document reversible assumptions.
2. Build a dynamic dependency graph, coverage ledger, source-demand map, and one owner for every claim family. Mark inapplicable domains skipped with reasons.
3. Run independent destination, transport, broad-activity, and applicable safety obligations concurrently. When air travel applies, `flight-search` owns its complete four-pass matrix. Gate date-sensitive stages on viable dates.
4. `accommodation-researcher` depends on viable dates from `flight-search` or other transport ownership; then run applicable accommodation, local discovery, and activity refinement after date/area gates. Reuse source IDs requested by multiple consumers.
5. Audit critical, stale, missing, or contradictory claims; do not repeat successful owner research.
6. Calculate scenarios/reserve, build the constrained itinerary, and quality-audit structure, arithmetic, feasibility, and evidence.
7. Validate every handoff with `validate-handoff` and the final dossier with `validate-dossier`. Resume only pending, expired, or invalidated cells.
8. Expand accepted artifacts once. Keep `mode: inspiration` unless coverage, evidence, recommendation, and booking gates all pass.

## Deliverables

- Sourced itinerary, transport, lodging, activity, budget, safety, and contingency dossier
- Claim/source ledger, rejected options, decisions, blockers, and revalidation plan
- Explicit user-controlled booking actions; no automatic purchase or reservation
