---
name: multi-agent-orchestration
description: Use when multiple travel specialists must coordinate, fan in evidence, recover, or resume; do not use for a single self-contained research task.
---

# Multi-Agent Orchestration

Read `../../shared/compact-research-protocol.md`, `../../shared/deterministic-tools.md`, and `../../shared/scenario-routing.md`.

## Inputs and tools

Use trip complexity, specialist capabilities, coverage obligations, dependency IDs, runtime limits, artifact paths, and existing run state. Build a dynamic dependency graph rather than dispatching every specialist by default.

## Method

- Classify complexity and active scenarios, then activate only applicable specialists. Put scenario IDs in the run manifest and pass each reference only to affected claim owners; an inapplicable domain becomes an explicit skipped obligation, not a silent omission. External-tool auditing is never part of ordinary travel planning.
- Assign one owner per claim family and create a shared source-demand map so several consumers can reuse one current source ID.
- Give each specialist an isolated brief slice, accepted decision IDs, its own artifact shard, and an exact coverage contract. Never forward full history or payloads.
- Run independent nodes concurrently. Fan in only after required gates pass; block dependents on unresolved date, area, critical claim, or evidence-sufficiency gates.
- Require `compact-handoff/v2`, enforce a small envelope size, and reject handoffs that embed research prose. Merge shards deterministically by stable ID/revision.
- Retries are idempotent: load terminal cells and execute only pending, expired, or explicitly invalidated work. A failed independent specialist degrades its section, not unrelated work.

## Fallback

When live-source tools are unavailable, continue deterministic stages from supplied fresh artifacts and mark research obligations pending or unverified. Never manufacture completion.

## Outputs

Write the DAG, ownership/source-demand map, stage state, merge decisions, and recovery actions. Return `compact-handoff/v2` with changed IDs and gates.
