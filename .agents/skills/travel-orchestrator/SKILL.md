---
name: travel-orchestrator
description: Use for an end-to-end trip plan spanning several research, budgeting, scheduling, and validation domains; use individual specialist skills for narrower requests.
---

# Travel Orchestrator

Read `../../shared/compact-research-protocol.md`, `../../shared/deterministic-tools.md`, and `../../shared/scenario-routing.md` before dispatch.

## Inputs and tools

Coordinate a privacy-minimal brief, complexity classification, runtime capabilities, run manifest, specialist IDs, decisions, and readiness target. Use filesystem state, deterministic commands, and available agent orchestration.

## Method

1. Create/reuse a run ID and brief fingerprint. Detect active scenario references from explicit brief facts, record their IDs, and ask only for missing facts that materially alter results; otherwise document reversible assumptions.
2. Build claim ownership, source-demand, coverage, and dependency maps. Activate only relevant specialists; preserve skipped reasons.
3. Run destination, transport, broad activity, and applicable safety research in isolated parallel contexts. Gate date-sensitive work on viable candidate dates.
4. Run accommodation, local discovery, and activity refinement only after the date/area gate. Reuse existing source IDs rather than reopening pages.
5. Verify only critical/stale/missing/conflicting claims, then calculate budget, construct itinerary, and perform quality control by artifact ID.
6. Require `compact-handoff/v2`; reject embedded full payloads. Resume only pending, expired, or invalidated cells.
7. Expand accepted artifacts once after all gates pass; preserve scenarios, rejections, conflicts, fallbacks, deadlines, and revalidation. Failed gates stay provisional with missing evidence named.
8. Run `validate-run`; run `validate-dossier` for JSON/YAML only. Report failed/unavailable checks. Critical blockers prevent booking readiness.

## Fallback

Without current sources, use supplied fresh evidence, calculations, and assumptions. Return inspiration mode with pending checks; insufficient comparisons prevent recommendation readiness.

## Outputs

Intermediate stages return `compact-handoff/v2`. Final dossier leads with route/nights, price or `unpriced`, difficult days, decisions, and readiness; then detail and checks. Link claims to evidence, never local paths as web links.
