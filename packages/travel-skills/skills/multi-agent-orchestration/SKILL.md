---
name: multi-agent-orchestration
description: Directives for scheduling, wave synchronization, context budget management, and DAG pipeline execution across specialized sub-agents.
---

# Multi-Agent Orchestration Skill

## Overview
This skill governs the coordination of the 11 specialized sub-agents to avoid compounding error rates and context window exhaustion.

## Orchestration Patterns

1. **Wave-Based Synchronization (Wave DAG)**:
   - Synchronous barriers prevent downstream agents from starting before upstream dependencies are satisfied.
   - **Wave 1**: Parallel exploration via Provider Hub (zero intra-wave blocking):
     - `destination-researcher`: editorial guides (`WikivoyageProvider`), local etiquette, seasonal weather outlook.
     - `transport-planner`: flight offers (`AmadeusFlightProvider` / `MockFlightProvider`), rail schedules (`SNCFTrainProvider` / `MockTrainProvider`), door-to-door buffers.
     - `accommodation-researcher`: curated lodging in quiet areas, review sentiment strictly isolated from inventory (`StayAPIReviewProvider` / `TripadvisorReviewProvider`). Zero booking.
     - `activity-curator`: cultural & nature activities, indoor rain Plan B, crowd avoidance windows.
     - `local-discovery-agent`: authentic culinary gems and social discovery trends (strictly tagged `social_discovery_only`).
     - `travel-preparation-agent`: pre-departure checklists, health requirements, and emergency contacts.
   - **Wave 2**: Budget consolidation (`budget-analyst`):
     - Consolidates itemized expenses, verifies currency reference dates (`ECBCurrencyProvider`), enforces safety buffer (+10-15%), and tracks price status distribution (`confirmed`, `estimated`, `needs_verification`).
   - **Wave 3**: Itinerary optimization (`itinerary-optimizer`):
     - Day-by-day scheduling with geographic clustering, transit feasibility checks, and indoor Plan B integration.
   - **Wave 4**: Quality control & security audit:
     - `quality-controller`: anti-hallucination gate (blocks any recommendation presented as confirmed if derived from mock or social discovery), unconfigured provider audit, pacing fatigue detection.
     - `mcp-skill-auditor`: URL allowlist validation, anti-injection scanning, and strict zero-booking assurance.
   - **Wave 5**: Final synthesis and dossier delivery (`travel-orchestrator`).

2. **Strict Context Budgeting**:
   - Sub-agents receive only the fields of data relevant to their task.
   - Outputs are strictly validated into `AgentResult` schemas before passing to downstream agents.

3. **Deterministic Fallback & Provider Modes**:
   - In `offline` mode (default), agents use local deterministic providers and rule engines rather than non-deterministic LLM calls.
   - In `mock` mode, rich simulated payloads matching live API schemas are returned.
   - In `live` mode, external partner APIs are queried only if configured; unconfigured providers fail closed or trigger explicit advisory notes.
