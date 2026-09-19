# Phase 11 — Skills-First Pivot Audit Report

> Archive de décision : instantané du pivot initial, remplacé pour l'état courant par l'architecture v1.4 et `docs/travel-dossier-v1.md`. Les nombres et garanties ci-dessous sont historiques.

## 1. Executive Summary & Strategic Rationale

Following the completion of Phases 0 through 10, `ultimate-travel-agent` had evolved into a multi-tiered repository containing:
1. A local multi-agent system and workflow engine;
2. A Streamable HTTP MCP server with security tokens;
3. Docker containers and cloud deployment manifests (Railway, Render, Fly.io, Cloud Run);
4. A Provider Hub with 25+ integration adapters (mock, keyless, and commercial candidates);
5. A lightweight local FastAPI web interface.

While technically functional (162 unit tests passing, clean CI), maintaining commercial travel APIs (e.g. Amadeus, Trip.com, TripAdvisor Terra, Google Maps, Viator, GetYourGuide) introduced structural problems:
- **Commercial API friction**: Required mandatory developer accounts, credit cards, partnership vetting, and recurring API costs.
- **Maintenance overhead**: Rapidly changing third-party schemas and deprecations.
- **Target audience mismatch**: Users and AI developers want a free, open-source, local-first travel assistant that runs effortlessly inside AI coding environments (Antigravity, Claude Code, Cursor) without cloud subscriptions.

**Strategic Pivot Decision**:
The project officially pivots to a **Skills-First Architecture**.
The core deliverable is now the **Travel Skills Pack**: a modular, self-contained suite of 13 AI skills, 11 sub-agents, and 9 end-to-end workflows that enable any Antigravity-compatible AI to research, cross-reference, plan, and verify travel plans directly using runtime web/browser tools and local algorithms.

All heavy cloud infrastructure, remote MCP servers, Docker files, and commercial API adapters are preserved on the dedicated archive branch:
`archive/mcp-api-prototype-v1.2`

---

## 2. Component Categorization & Inventory

### A. Elements Preserved & Refocused on `main`
- **`.agents/skills/`**: Expanded from 6 legacy skills to 13 modular, standardized skills with uniform frontmatter, 6-tier sourcing hierarchy, strict safety invariants, and offline fallback protocols.
- **`.agents/agents/`**: All 11 specialized sub-agents preserved and refocused on executing travel skills rather than querying internal mock APIs.
- **`.agents/workflows/`**: 9 end-to-end and modular travel workflows providing deterministic procedural guidance for complex itineraries.
- **`packages/travel-skills/`**: Distributable package mirroring the 13 skills, with cross-platform installer scripts and JSON manifest.
- **`examples/`**: Universal trip brief template and 3 rich, realistic scenario briefs (city-break, road-trip, nature/low-crowd).
- **`src/ultimate_travel_agent/cli.py`**: Lightweight CLI supporting `install-skills`, `uninstall-skills`, and `list-skills`.
- **`docs/`**: Comprehensive guides covering cross-project installation, Antigravity integration, browser tool adaptation, sourcing hierarchy, and skills catalog.
- **`tests/`**: Fast, robust test suite verifying installation integrity, overwrite safety, frontmatter validity, safety policies, and zero-secret invariants.
- **`docs/history/research/`**: All historical foundational research from Phase 0 preserved for historical reference.

### B. Elements Archived to `archive/mcp-api-prototype-v1.2`
The following components were safely branched and removed from the active `main` branch to eliminate clutter and false promises:
- `src/ultimate_travel_agent/mcp/`: Remote HTTP MCP server, authentication middleware, and 30 MCP tool registrations.
- `src/ultimate_travel_agent/integrations/`: Provider Hub (flights, trains, hotels, activities, maps, weather, currency, reviews, guides).
- `src/ultimate_travel_agent/web/`: FastAPI web server and static assets.
- `deployment/`: Cloud deployment manifests for Railway, Render, Fly.io, and Google Cloud Run.
- `Dockerfile` & `docker-compose.yml`: Container virtualization files.
- `railway.json`, `.dockerignore`, `.env.example`: Cloud configuration templates.

### C. Elements Improved During Pivot
1. **Skill Quality**: Every skill now contains role-specific inputs, outputs, concrete examples, and strict safety rules (no purchases, no bookings, no private data).
2. **Offline Fallback**: Standardized behavior across all skills when `web_search` or `browser` tools are unavailable, preventing hallucinated pricing or hours.
3. **Cross-Project Installation**: Single CLI command to install skills, agents, and workflows into any target Antigravity project.
4. **Transparent Sourcing**: Enforced 6-tier sourcing hierarchy across all agent recommendations.

---

## 3. Tool Capability Matrix: Online vs Offline

| Travel Capability | Without Web Search / Browser (Offline Fallback) | With Web Search & Browser Enabled |
|---|---|---|
| **Destination Scoping** | General seasonal advice based on historical climate; flagged as estimated. | Current weather outlooks, live municipal alerts, upcoming festivals. |
| **Transport Routing** | High-level corridor comparison (rail vs flight); estimated durations. | Exact timetables, direct carrier booking links, advance booking windows. |
| **Lodging Scouting** | Strategic neighborhood recommendations and lodging style criteria. | Vetted shortlists of specific active hotels with direct links and cancellation terms. |
| **Activity Curation** | Classic sights, anti-crowd strategies, and rainy day backup ideas. | Timed-entry booking requirements, current ticket prices, museum holiday closures. |
| **Itinerary Construction** | Geographic clustering, day pacing, rest buffers, and meal planning. | Fully operational and optimized locally without network access. |
| **Budget Analysis** | Line-item estimations with 10-15% safety reserve; tagged as unconfirmed. | Exact reference currency conversions and verified baseline ticket prices. |
| **Safety & Entry Rules** | General guidance on passport validity and emergency protocol templates. | Official embassy visa policies, entry forms, and health advisories. |
| **Quality Assurance Gate** | Validates connection buffers, pacing, rest times, and budget math. | Validates opening days and cross-checks claims against live Tier 1/2 sources. |

---

## 4. Verification & Integrity Checklist

- [x] Working tree clean of temporary generated files and leftover scripts.
- [x] Zero hardcoded Windows personal paths (`c:\Users\...`) across all repository files.
- [x] Zero active API keys, secrets, or tokens versioned in Git.
- [x] All 14 automated tests passing in under 1 second.
- [x] Branch `archive/mcp-api-prototype-v1.2` preserves the full Phase 10 state (`f9a3aac`).
- [x] Permissive MIT License and Open Source standards maintained.
