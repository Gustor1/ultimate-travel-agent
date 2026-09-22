---
name: travel-orchestrator
description: Use for an end-to-end trip plan spanning several research, budgeting, scheduling, and validation domains; use individual specialist skills for narrower requests.
---

# Travel Orchestrator

Read `../../shared/compact-research-protocol.md` and `../../shared/deterministic-tools.md` before dispatch.

## Inputs and tools

Coordinate a privacy-minimal brief, complexity classification, runtime capabilities, run manifest, specialist IDs, decisions, and readiness target. Use filesystem state, deterministic commands, and available agent orchestration.

## Method

1. Create/reuse a run ID and brief fingerprint. Ask only for missing facts that materially alter results; otherwise document reversible assumptions.
2. Build claim ownership, source-demand, coverage, and dependency maps. Activate only relevant specialists; preserve skipped reasons.
3. Run destination, transport, broad activity, and applicable safety research in isolated parallel contexts. Gate date-sensitive work on viable candidate dates.
4. Run accommodation, local discovery, and activity refinement only after the date/area gate. Reuse existing source IDs rather than reopening pages.
5. Verify only critical/stale/missing/conflicting claims, then calculate budget, construct itinerary, and perform quality control by artifact ID.
6. Require `compact-handoff/v2`; reject embedded full payloads. Resume only pending, expired, or invalidated cells.
7. After coverage, evidence, recommendation, and quality gates pass, expand accepted artifacts once into `TravelDossier v1`. Preserve scenarios, rejected options/reasons, conflicts, fallbacks, booking deadlines, and revalidation tasks.
8. Run `validate-dossier`; `booking_ready` remains false whenever a critical blocker exists.

## Fallback

Without current-source access, continue only from supplied fresh evidence, deterministic calculations, and explicit assumptions. Return an inspiration-mode dossier plus exact pending verification; never manufacture readiness.

## Outputs

Intermediate stages return `compact-handoff/v2`. Final output is one complete validated `TravelDossier v1`, not repeated dossier fragments.
