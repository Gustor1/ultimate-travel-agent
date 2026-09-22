# Architecture

`ultimate-travel-agent` is a declarative Travel Skills Pack. The active branch contains skills, agent definitions, workflows, a safe installer, and validators. It does not contain the archived MCP server, provider adapters, or FastAPI interface.

## Canonical assets

`.agents/` is the single source of truth:

- 14 skills;
- 12 agent definitions;
- 9 workflows;
- one shared compact-research protocol;
- one bundle manifest.

The Python wheel bundles the canonical `.agents` assets as `ultimate_travel_agent.bundle`, so installation does not depend on a Git checkout and no duplicate source tree is maintained.

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
