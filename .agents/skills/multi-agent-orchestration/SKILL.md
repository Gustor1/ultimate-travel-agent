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
   - **Wave 1**: Parallel exploration (zero intra-wave blocking).
   - **Wave 2**: Budget consolidation (requires Wave 1 completion).
   - **Wave 3**: Itinerary optimization (requires Wave 1 & 2 completion).
   - **Wave 4**: Quality control & security audit (independent verification of candidate trip).
   - **Wave 5**: Final synthesis and dossier delivery.

2. **Strict Context Budgeting**:
   - Sub-agents receive only the fields of data relevant to their task.
   - Outputs are strictly validated into `AgentResult` schemas before passing to downstream agents.

3. **Deterministic Fallback**:
   - In offline mode, agents use local deterministic providers and rule engines rather than non-deterministic LLM calls.
