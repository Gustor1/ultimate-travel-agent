# Architecture

`ultimate-travel-agent` is a declarative Travel Skills Pack with deterministic Python
utilities and an optional stdio MCP adapter. The MCP server is intentionally thin: it
validates Pydantic request envelopes, dispatches directly to existing functions, and
returns structured results. It is not a FastAPI service or booking engine.

## Canonical assets

`.agents/` is the single source of truth:

- 14 skills;
- 12 agent definitions;
- 9 workflows;
- one shared compact-research protocol;
- one bundle manifest.

The Python wheel bundles the canonical `.agents` assets as `ultimate_travel_agent.bundle`, so installation does not depend on a Git checkout and no duplicate source tree is maintained.

## MCP adapter

`mcp_tools.py` is the statically auditable catalogue. Each declaration contains four
inline safety booleans. `mcp/schemas.py` derives input and output JSON Schemas from
Pydantic contracts, `mcp/handlers.py` owns bounded dispatch and filesystem containment,
and `mcp/server.py` provides initialization, `tools/list`, and `tools/call` over stdio.
No call is routed through a shell or CLI subprocess.

The normal package has no MCP runtime dependency. Installing the `mcp` extra adds the
SDK and the `ultimate-travel-agent-mcp` entry point.

## Execution graph

1. Brief gate: `travel-orchestrator` detects missing critical constraints.
2. Wave 1A, parallel: destination, transport, safety, and broad activity research.
3. Date gate: transport options establish candidate effective dates.
4. Wave 1B, parallel: accommodation, local discovery, and date-sensitive activity refinement.
5. Evidence gate: `source-verification` creates claim/source links and freshness windows.
6. Budget: `budget-analyst` consolidates typed cost components.
7. Schedule: `itinerary-optimizer` builds the chronological plan.
8. Quality gate: `quality-controller` checks feasibility, arithmetic, freshness, and readiness.
9. Synthesis: `travel-orchestrator` emits `TravelDossier v1`.

## Context transport

Specialists do not exchange full dossier fragments or conversation histories. They persist full-fidelity evidence once under a run artifact directory and return `compact-handoff/v2` envelopes containing paths, stable IDs, blockers, coverage counts, and distinct readiness gates. Downstream stages load only the referenced records required for their decision. See [Token efficiency](token-efficiency.md).

`mcp-skill-auditor` runs only when an external skill, MCP server, API, or new tool is proposed. It is not part of ordinary trip planning.

## Twelve agents

- `travel-orchestrator`
- `destination-researcher`
- `transport-planner`
- `accommodation-researcher`
- `activity-curator`
- `local-discovery-agent`
- `travel-preparation-agent`
- `budget-analyst`
- `itinerary-optimizer`
- `source-verification`
- `quality-controller`
- `mcp-skill-auditor`

## Contract

All stages use [`TravelDossier v1`](travel-dossier-v1.md). Specialized outputs remain under `recommendations`; factual claims link to exact source IDs. Legacy envelopes are accepted during migration but cannot pass the booking-readiness gate without claim-level evidence.

## Host responsibility

Markdown instructions do not enforce sandboxing. The host runtime controls real tools, network access, filesystem scope, and user approvals. Agent frontmatter documents requested capabilities only.

## Conditional capability decision

The pack extends existing owners before adding specialists. Family/minors, dining, connectivity/remote work, loyalty/awards, and sustainable travel are conditional shared references selected from the brief. They do not create new agents, alter the fixed handoff envelope, or load during unrelated trips.

Assumptions: users may omit these dimensions; sources and web capabilities vary by host; privacy-minimal local artifacts remain the durable state. The main risks are overlapping ownership, prompt growth, stale operational claims, and false precision. They are controlled through one claim owner, explicit routing, existing freshness rules, bounded references, and deterministic validation. A standalone skill is justified later only if one domain develops an independent research lifecycle that cannot be represented cleanly by the current owners.

Decision log: modular conditional references were chosen over five new agents and over an adaptive telemetry subsystem. This preserves portability and token efficiency while allowing the methods to evolve independently.
