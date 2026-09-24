# Token efficiency without research loss

The pack reduces model context by changing how research is carried between stages. It preserves every cell required by the selected task. Activity breadth follows usable days and interests rather than a fixed number of candidates per calendar day.

## What changed

1. Every skill now points to one shared [`compact-research-protocol`](../.agents/shared/compact-research-protocol.md).
2. Specialists start with isolated context: relevant brief fields, accepted decision IDs, artifact paths, and a coverage obligation—not the full chat history.
3. Search cells, claims, sources, prices, policies, rejected candidates, and checks are written once to full-fidelity JSONL/YAML artifacts.
4. Agents return `compact-handoff/v2`, which contains paths, IDs, blockers, coverage counts, and readiness gates rather than another copy of the research.
5. Independent searches may be batched into fewer tool calls, but no required query or cell may be pruned.
6. Deterministic local code handles grids, arithmetic, sorting, deduplication, and validation. Model context is reserved for discovery, ambiguity, trade-offs, and synthesis.
7. Only the final orchestrator expands accepted evidence into the complete user-facing `TravelDossier v1`.
8. Current evidence is reused through an applicability-aware cache; pending, expired, contradicted, or invalidated cells are the only ones rerun.
9. Each claim family has one owner and a shared source-demand map, so several specialists can use one source without reopening it.

## Static prompt measurement

Measured as UTF-8 text characters in the canonical `.agents/` tree:

| Corpus | Before | After | Reduction |
|---|---:|---:|---:|
| 14 primary skills | 121,605 | 36,392 | 70.1% |
| 12 agent definitions | 27,102 | 11,136 | 58.9% |
| 9 workflows | 19,528 | 13,790 | 29.4% |
| Skills + agents + workflows | 168,235 | 61,318 | 63.6% |

Shared methods are progressively disclosed: research, evidence, cache, deterministic-tool, regional, and scenario references are loaded only when applicable. The entrypoint corpus therefore shrank even while claim-first planning, contradiction resolution, multilingual queries, Pareto comparison, source independence, concurrency safety, and machine-validatable handoffs were added. Character counts are a stable repository regression metric, not provider-billed token measurements. Actual Codex or Claude quota savings depend on host caching, model reasoning, web-result size, and subagent implementation.

Reproduce the current corpus measurement with `ultimate-travel-agent prompt-audit`. Its token column is the explicit `characters / 4` comparison proxy, never a claim about billed usage.

## Why precision remains intact

- When flight comparison is requested or controls the route, it still creates the complete four-pass coverage ledger, including flexible dates and gateways. Other trips keep flights explicitly unpriced and continue experience planning from candidate dates.
- Activity research covers each usable sightseeing day and its fragile anchors. It expands choices where needed without a trip-length-only quota.
- Accommodation still covers required neighborhoods, transit evidence, Google Hotels, Booking.com, Agoda/Trip.com, and official-property verification.
- Destination research retains its complete topic × period × area × traveler-constraint × source-role coverage lattice.
- Every required cell must end as `searched`, `unavailable`, or justified `skipped`; `pending: 0` closes execution but does not falsely imply evidence sufficiency.
- Evidence remains recoverable at full fidelity with stable claim/source IDs, original/canonical URLs, retrieval/expiry/effective dates, independence groups, formulas, conflicts, and rejection reasons.
- `coverage_complete`, `evidence_sufficient`, `recommendation_ready`, and `booking_ready` are independent gates.
- Existing domain validators and exhaustive flight/hotel tests remain active. Token-budget tests prevent prompt bloat from returning.

## Portable validation

`compact-handoff/v2` is defined by an installed JSON Schema and a stricter Pydantic validator. Run `ultimate-travel-agent validate-handoff <file>` for an intermediate result and `validate-dossier <file>` for the final dossier. The handoff validator rejects inconsistent coverage arithmetic, impossible gate progression, duplicate IDs, blocker-free blocked states, and booking-ready states that still contain blockers.

## Codex Desktop use

Open the repository as the task workspace and request the `travel-orchestrator` skill. Keep the run inside that task so agents share the workspace artifacts. The orchestrator must dispatch specialists with isolated context and collect `compact-handoff/v2` results. If interrupted, resume from the run manifest and search only cells still marked `pending`.

## Other hosts

Claude Code, Cursor, Antigravity, and compatible Markdown-skill hosts use the same files. A host without filesystem writes may map the artifact layout to its own durable state facility while preserving the same IDs and handoff schema.

Conditional capabilities follow the same rule: family, dining, connectivity, loyalty, and sustainable-travel references are loaded only when explicit brief facts trigger them. They add research obligations without enlarging unrelated prompts or creating extra agents.

## Optional Caveman layer

Caveman can be used outside this repository to compress verbose tool output seen by a supported agent. It remains optional because the travel pack contains no direct LLM API callsite to route through a gateway, and mandatory host-specific infrastructure would reduce portability. Review Caveman's license, telemetry, recovery, and measured-versus-inferred savings before enabling it.
