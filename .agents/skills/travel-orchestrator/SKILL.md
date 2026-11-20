---
name: travel-orchestrator
description: Use for an end-to-end trip plan spanning several research, budgeting, scheduling, and validation domains; use individual specialist skills for narrower requests.
---

# Travel Orchestrator

Read `../../shared/planning-depth.md`, `../../shared/compact-research-protocol.md`, `../../shared/deterministic-tools.md`, and `../../shared/scenario-routing.md` before dispatch.

## Inputs and tools

Coordinate a privacy-minimal brief, depth mode, runtime capabilities, specialist IDs, decisions, and readiness target. Use the host's real tools as routed in `planning-depth.md`, filesystem state in `exhaustive` mode, deterministic commands, and agent orchestration when available.

## Method

1. If origin, dates, budget, pace, or interests are missing, run `trip-intake` first. Fix the depth mode and record active scenario IDs from explicit brief facts; document reversible assumptions instead of re-asking.
2. Build claim ownership and dependencies. Activate only relevant specialists; preserve skipped reasons. In `exhaustive` mode create the run ID, coverage, and source-demand maps.
3. Run destination, applicable safety, broad activity, and relevant transport research. For international trips the entry check is never skipped. When rail, coach, or ferry is credible for the main corridor, compare it against air door-to-door before choosing. Use `flight-search` when the user requests fares or flight choice controls dates/route. Otherwise record assumed gateways and keep air costs and schedules unverified.
4. Gate date-sensitive lodging and visit logistics on candidate dates. Run local discovery and activity refinement for selected areas; reuse sources.
5. Verify only critical/stale/missing/conflicting claims, then calculate budget, construct itinerary, and perform quality control.
6. In `exhaustive` mode require `compact-handoff/v2`, reject embedded payloads, resume only pending, expired, or invalidated cells, and run `validate-run` (plus `validate-dossier` for JSON/YAML). Report failed or unavailable checks.
7. Render the final plan with `../../shared/trip-output-template.md`: lead with feasible experiences, blockers, the dated booking calendar, and decisions for the user. Distinguish planning readiness from booking readiness; critical blockers prevent `prêt à réserver`.

## Fallback

Without current sources, use supplied fresh evidence, calculations, and assumptions. Return `quick` mode output with every live fact marked unverified; insufficient comparisons prevent recommendation readiness.

## Outputs

The user-facing plan follows the template, in the user's language. Intermediate stages in `exhaustive` mode return `compact-handoff/v2`. Link claims to evidence, never local paths as web links.
