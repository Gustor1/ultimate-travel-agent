# Travel Skills Catalog

The pack contains 14 runtime-neutral, local-first skills. Each entrypoint loads shared policy progressively and returns artifact IDs through `compact-handoff/v2`; only final synthesis expands a complete `TravelDossier v1`.

| Skill | Distinct responsibility | Deterministic support |
|---|---|---|
| [`travel-orchestrator`](../.agents/skills/travel-orchestrator/SKILL.md) | Dynamic end-to-end DAG, ownership, gates, final synthesis | `validate-handoff`, `validate-dossier` |
| [`multi-agent-orchestration`](../.agents/skills/multi-agent-orchestration/SKILL.md) | Isolated contexts, source-demand fan-in, sharded recovery | Handoff validation |
| [`travel-web-research`](../.agents/skills/travel-web-research/SKILL.md) | Geography, climate, events, crowds, norms, regional context | Coverage/artifact checks |
| [`flight-search`](../.agents/skills/flight-search/SKILL.md) | Complete four-pass flight matrix and direct-carrier evidence | `flight-search-plan`, `flight-search-coverage` |
| [`transport-research`](../.agents/skills/transport-research/SKILL.md) | Non-flight/multimodal door-to-door Pareto comparison | `compare-total-cost` |
| [`accommodation-research`](../.agents/skills/accommodation-research/SKILL.md) | Neighborhoods and exact comparable room/rate plans | Hotel coverage, mobility, comparison, neighborhood commands |
| [`activity-curator`](../.agents/skills/activity-curator/SKILL.md) | Major activities, slots, access, crowd and weather fallback | Deterministic time checks |
| [`local-discovery`](../.agents/skills/local-discovery/SKILL.md) | Neighborhood venues, multilingual discovery, provenance | URL/entity deduplication |
| [`travel-safety`](../.agents/skills/travel-safety/SKILL.md) | Applicable entry, health, weather, insurance, emergency actions | `revalidation-plan` |
| [`source-verification`](../.agents/skills/source-verification/SKILL.md) | Atomic critical/stale/conflicting claim audit | `normalize-source-url` |
| [`budget-and-booking-checker`](../.agents/skills/budget-and-booking-checker/SKILL.md) | Atomic scenarios, financial exposure, risk reserve, user handoff | Cost, watch, revalidation, booking commands |
| [`itinerary-builder`](../.agents/skills/itinerary-builder/SKILL.md) | Time-window route, pace, slack, variants, disruption recovery | Route, adaptive-day, disruption commands |
| [`travel-quality-control`](../.agents/skills/travel-quality-control/SKILL.md) | Structure, arithmetic, feasibility, evidence, readiness audit | `validate-dossier` |
| [`mcp-skill-auditing`](../.agents/skills/mcp-skill-auditing/SKILL.md) | Optional static review of a proposed external component only | Filesystem inspection |

## Shared guarantees

- Required research cells and candidate obligations are never pruned for token savings.
- `pending: 0` proves execution, not evidence sufficiency; four readiness gates remain separate.
- Claims link to current sources by stable ID, authority, independence group, and applicability.
- Parallel writers use separate revisioned shards; handoffs contain IDs instead of copied evidence.
- Missing live evidence remains explicitly unverified. No skill purchases, reserves, bypasses access controls, or handles payment data.

## MCP tool safety annotations

All 29 deterministic CLI tools carry explicit safety hints for MCP clients. See [mcp-tool-annotations.md](mcp-tool-annotations.md) for the full classification and rationale.
