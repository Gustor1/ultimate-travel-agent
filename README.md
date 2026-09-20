# Ultimate Travel Agent

A portable, runtime-agnostic **Travel Skills Pack** for AI coding agents and agentic development environments.

[![CI](https://github.com/Gustor1/ultimate-travel-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Gustor1/ultimate-travel-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills-First](https://img.shields.io/badge/Architecture-Skills--First-blue.svg)](#platform-approach)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[Documentation en Français](docs/install-in-any-project.fr.md) | [Catalogue des Skills (FR)](docs/skills-catalog.fr.md) | [Intégration Antigravity (FR)](docs/use-with-antigravity.fr.md)

---

> [!WARNING]
> **Status: Beta / Experimental.**  
> This project provides travel research and planning assistance only.  
> It **never** purchases, books, pays for, or executes transactions on behalf of a user.  
> Always verify prices, availability, visa rules, safety guidance, and booking conditions with official sources before taking action.

---

## Overview

**Ultimate Travel Agent** is a portable, skills-first travel research and planning pack for AI coding agents and agentic development environments.

The core product is a portable file-based skills pack rather than an application tied to one AI platform. Each compatible host still needs a runtime adapter that maps declared capabilities to its real tools and permission model.

The active branch contains no MCP server, provider API hub, booking engine, or FastAPI interface. Historical prototypes remain documented separately; future runtime integrations belong in optional packages.

---

## Main Capabilities

The toolkit organizes travel expertise into four core functional areas:

### 1. Research
- **Flight Search**: Structured 4-pass flight optimization (base, multi-airport, flexible dates, combined) with adaptive comparison-engine research and direct airline verification.
- **Flexible Flight Matrix**: Executable airport/date matrix generation up to ±3 days, regional and cross-border gateways, self-transfer safeguards, exact coverage reporting, and door-to-door offer ranking.
- **Accommodation Research**: Strategic neighborhood scouting, safety and noise vetting, transit accessibility, and cancellation policy checks.
- **Hotel Comparison**: Transit-first neighborhood screening, Google Hotels/Booking/Agoda/Trip.com discovery, normalized final prices, cancellation comparison, and official-direct preference.
- **Ground Transport Research**: Multi-modal transit planning (high-speed rail, regional trains, buses, ferries, car rental) with official operator schedules and fares.
- **Local Discovery**: Authentic neighborhood eateries, cultural venues, and community spots, with strict tagging of unconfirmed social sources.
- **Activity Curation**: Cultural, outdoor, and culinary experiences with anti-crowd tactics, booking requirements, and bad-weather contingencies.

### 2. Planning
- **Itinerary Construction**: Logical day-by-day sequencing with geographic clustering to eliminate backtracking and avoid traveler fatigue.
- **Budget & Booking Readiness**: Itemized expense consolidation, 10–15% safety reserves, and chronological pre-departure booking checklists.
- **Travel Safety & Preparation**: Country entry rules, visa exemptions, passport validity requirements, health advisories, and emergency protocols.
- **Advanced Planning Toolkit**: Persistent preference profiles, explainable scoring, uncertainty and contradiction tracking, progressive research gates, geographic/time feasibility, scenario budgets, decision history, portable exports, price-watch assessment, and pre-departure revalidation schedules.
- **Door-to-Door Optimization**: Scores hotel access to real trip anchors and compares full travel costs including transfers, baggage, time, extra nights, and self-transfer exposure.
- **Targeted Disruption Recovery**: Replaces only affected itinerary items while preserving fixed and unaffected bookings.
- **Adaptive & Group Planning**: Builds essential/rain/low-energy variants and ranks complete group ballots without overriding hard vetoes.
- **Advanced Route Optimization**: Uses sourced travel matrices, opening windows, and fixed appointments rather than straight-line proximity alone.
- **Neighborhood Quality**: Scores safety, noise, metro/tram, late service, essential shops, accessibility, and tourist pressure with dated evidence.
- **Controlled Booking & Trip Mode**: Verifies exact checkout handoffs and provides offline-aware current/next travel actions without handling payment data.
- **Secure Live Connectors**: Executes bounded HTTPS/JSON requests with environment-based credentials, host locking, and secret redaction.
- **Scheduled Signed Alerts**: Produces deduplicated price events and optionally delivers them to an explicitly configured HTTPS webhook.

### 3. Verification
- **Source Verification**: Enforcement of a strict 6-tier sourcing hierarchy (prioritizing official government portals and carrier websites over community blogs or social media).
- **Travel Quality Control**: Comprehensive pre-delivery audits verifying transit connection feasibility, pacing realism, arithmetic accuracy, and contingency coverage.

### 4. Coordination
- **Workflow Orchestration**: Multi-agent wave execution topologies, inter-agent data passing, and fallback states for autonomous planning teams.
- **Tool & Skill Auditing**: Independent security audits of external tools, skills, and model context protocol configurations to prevent permission overreach and prompt injection.

---

## Platform Approach

Ultimate Travel Agent is built on a portable, file-based architecture. Instead of embedding logic in a proprietary runtime or server application, the skills and workflows are expressed in open, declarative formats (Markdown and YAML).

The platform integration strategy distinguishes three tiers:
- **Designed for**: Runtime-agnostic, file-based skills usage across modern AI development environments that can consume local prompt instructions.
- **Tested integrations**: Environments with an end-to-end documented installation workflow and validation in the repository.
- **Planned integrations**: Target environments where native integration guides and end-to-end testing are planned for future releases.

### Current Validation & Compatibility Status

| Environment | Status | Notes |
|---|---|---|
| **Core skills pack** | Automated validation | Skills, installation lifecycle, `TravelDossier v1`, evidence links, and safety invariants |
| **Antigravity** | Documented / experimental | Documented installation and workflow integration via CLI installer (`.agents/`) |
| **Claude Code** | Planned | Integration guide to be added after end-to-end testing |
| **OpenAI Codex** | Planned | Integration guide to be added after end-to-end testing |
| **Cursor** | Planned | Integration guide to be added after end-to-end testing |
| **Qwen Code** | Planned | Integration guide to be added after end-to-end testing |

> [!NOTE]
> Integrations are validated progressively. Do not assume out-of-the-box native support for planned platforms until formal integration documentation and test coverage are released.

---

## Quick Start

The repository provides a Python CLI utility (`ultimate_travel_agent.cli`) to inspect, install, and validate skills into target projects.

### 1. Inspect Available Skills
```bash
# Clone the repository
git clone https://github.com/Gustor1/ultimate-travel-agent.git
cd ultimate-travel-agent

# Install the CLI and bundled declarative assets
python -m pip install -e .

# List all 14 travel skills
python -m ultimate_travel_agent.cli list-skills
```

### 2. Install into a Target Project
You can install the skills pack, agent definitions, and workflows into any project directory:
```bash
python -m ultimate_travel_agent.cli install-skills \
  --target /path/to/my-project \
  --include-agents \
  --include-workflows
```

The installer records SHA-256 hashes in `<target>/.agents/.ultimate-travel-agent-install.json`. Existing files are skipped by default. `--force` creates recoverable local backups; uninstallation restores overwritten files. Missing or malformed manifests fail closed.

### 3. Validate Skill Compliance
Verify that installed skills comply with YAML frontmatter rules, 6-tier sourcing standards, and safety invariants:
```bash
python -m ultimate_travel_agent.cli validate-skills
```

Validate a generated JSON/YAML dossier against the shared contract:
```bash
python -m ultimate_travel_agent.cli validate-dossier dossier.yaml
```

### 4. Non-Destructive Uninstallation
To cleanly remove installed files while preserving custom modifications and user-added skills:
```bash
python -m ultimate_travel_agent.cli uninstall-skills --target /path/to/my-project
```

For platform-specific setup details, see:
- [General Installation Guide](docs/install-in-any-project.md) (or [en français](docs/install-in-any-project.fr.md))
- [Using with Antigravity](docs/use-with-antigravity.md) (or [en français](docs/use-with-antigravity.fr.md))

---

## Skills Overview

The pack contains **14 core travel skills** located under [`.agents/skills/`](.agents/skills/) and mirrored in [`packages/travel-skills/skills/`](packages/travel-skills/skills/):

| Skill | Category | Role |
|---|---|---|
| [`travel-orchestrator`](.agents/skills/travel-orchestrator/SKILL.md) | Coordination | Coordinates the 5-wave planning lifecycle and consolidates the final sourced travel dossier. |
| [`travel-web-research`](.agents/skills/travel-web-research/SKILL.md) | Research | 12-step research protocol for climate, regional norms, crowd calendars, and official data. |
| [`flight-search`](.agents/skills/flight-search/SKILL.md) | Research | Structured 4-pass flight optimization with adaptive comparison and direct carrier booking links. |
| [`transport-research`](.agents/skills/transport-research/SKILL.md) | Research | Door-to-door multi-modal transit comparison (rail, road, ferry) with official operator channels. |
| [`accommodation-research`](.agents/skills/accommodation-research/SKILL.md) | Research | Vets strategic neighborhoods and curates lodging options with safety, transit, and cancellation terms. |
| [`activity-curator`](.agents/skills/activity-curator/SKILL.md) | Research | Curates cultural, outdoor, and culinary activities with anti-crowd tactics and rain backups. |
| [`local-discovery`](.agents/skills/local-discovery/SKILL.md) | Research | Scouts authentic neighborhood eateries and hidden gems, tagging community sources strictly for verification. |
| [`itinerary-builder`](.agents/skills/itinerary-builder/SKILL.md) | Planning | Assembles daily schedules with geographic clustering to eliminate backtracking. |
| [`budget-and-booking-checker`](.agents/skills/budget-and-booking-checker/SKILL.md) | Planning | Audits line items, adds a 10–15% safety reserve, and compiles pre-departure booking requirements. |
| [`travel-safety`](.agents/skills/travel-safety/SKILL.md) | Planning | Evaluates entry visas, passport validity, health prerequisites, and emergency preparedness. |
| [`source-verification`](.agents/skills/source-verification/SKILL.md) | Verification | Cross-checks claims, timetables, and fares against our strict 6-tier sourcing hierarchy. |
| [`travel-quality-control`](.agents/skills/travel-quality-control/SKILL.md) | Verification | Audits transit feasibility, pacing realism, budget arithmetic, and contingency coverage. |
| [`multi-agent-orchestration`](.agents/skills/multi-agent-orchestration/SKILL.md) | Coordination | Coordinates execution topologies, wave dependencies, and fallback states for agent teams. |
| [`mcp-skill-auditing`](.agents/skills/mcp-skill-auditing/SKILL.md) | Coordination | Audits external tools and MCP servers for security integrity, permission scope, and injection risks. |

The canonical assets live in `.agents/`. `packages/travel-skills/skills/` is a generated compatibility mirror checked by CI.

See the complete [Skills Catalog (EN)](docs/skills-catalog.md) or [Catalogue des Skills (FR)](docs/skills-catalog.fr.md).

---

## Demonstration Scenarios

Representative scenario briefs and validated output dossiers are available in [`examples/scenarios/`](examples/scenarios/):

1. **Barcelona Cultural City Break (4 Days)**: [Brief](examples/scenarios/city-break-europe.md) → [Expected Output](examples/expected-outputs/city-break-europe-output.md)
2. **Iceland Ring Road Nature Expedition (7 Days)**: [Brief](examples/scenarios/road-trip-nature.md) → [Expected Output](examples/expected-outputs/road-trip-nature-output.md)
3. **Brittany & Normandy Family Vacation (6 Days)**: [Brief](examples/scenarios/family-trip.md) → [Expected Output](examples/expected-outputs/family-trip-output.md)
4. **Vietnam Central Backpacking Adventure (10 Days)**: [Brief](examples/scenarios/backpacking-budget.md) → [Expected Output](examples/expected-outputs/backpacking-budget-output.md)
5. **Umbria Low-Crowd Cultural Exploration (5 Days)**: [Brief](examples/scenarios/low-crowd-cultural-trip.md) → [Expected Output](examples/expected-outputs/low-crowd-cultural-trip-output.md)
6. **London Corporate Trip & West End Evening (3 Days)**: [Brief](examples/scenarios/business-trip.md) → [Expected Output](examples/expected-outputs/business-trip-output.md)

Template briefs are provided in [`examples/trip-brief-template.md`](examples/trip-brief-template.md) and [`examples/trip-brief-template.fr.md`](examples/trip-brief-template.fr.md).

---

## Documentation

- **[Getting Started](docs/getting-started.md)**: Overview of CLI commands and workflow execution.
- **[Architecture](docs/architecture.md)**: Architectural design, multi-wave orchestration, and skills-first methodology.
- **[Skills Catalog](docs/skills-catalog.md)** ([Version FR](docs/skills-catalog.fr.md)): Detailed inventory of the 14 travel skills, tools, and outputs.
- **[Travel Workflow](docs/travel-workflow.md)**: The 5-wave lifecycle and multi-agent coordination pipeline.
- **[Security & Privacy Model](docs/security-model.md)**: Least-privilege agent permissions, untrusted web content isolation, and zero-PII policies.
- **[Source Verification Policy](docs/source-verification.md)**: The 6-tier sourcing hierarchy and official domain validation rules.
- **[TravelDossier v1](docs/travel-dossier-v1.md)**: Claim ledger, evidence taxonomy, freshness, typed money, and booking-readiness rules.
- **[Advanced Planning](docs/advanced-planning.md)**: Profiles, scoring, route/budget helpers, exports, and revalidation.
- **[Flexible Flight Search](docs/flexible-flight-search.md)**: Exhaustive four-pass matrices, gateway transfers, coverage proof, and CLI usage.
- **[Hotel Comparison](docs/hotel-comparison.md)**: Metro/tram-first access checks, comparable rates, cancellation terms, and direct-channel preference.
- **[Door-to-Door Optimization](docs/door-to-door-optimization.md)**: Weighted hotel mobility and complete travel-cost comparison.
- **[Disruption Recovery](docs/disruption-recovery.md)**: Verified, conflict-free replacement of affected itinerary items.
- **[Secure Live Connectors](docs/live-connectors.md)**: Credential-safe provider-neutral API calls.
- **[Adaptive & Group Planning](docs/adaptive-group-planning.md)**: Day variants, fair group decisions, and time-window route optimization.
- **[Booking & Trip Mode](docs/booking-and-trip-mode.md)**: Explicit checkout confirmation and offline next-action guidance.
- **[Known Limitations](docs/known-limitations.md)**: Current system boundaries, offline behavior, and manual verification requirements.
- **[Installation Guide](docs/install-in-any-project.md)** ([Version FR](docs/install-in-any-project.fr.md)): Step-by-step installation and uninstallation in any project.
- **[Antigravity Integration](docs/use-with-antigravity.md)** ([Version FR](docs/use-with-antigravity.fr.md)): Documentation for running within the Antigravity agentic environment.
- **[Historical Archives](docs/history/README.md)**: Preserved research and design documents from earlier pre-pivot phases.

---

## Scope & Limitations

- **Active Development**: This project is in beta. Formats, workflows, and skills may evolve as new agent platforms are tested.
- **Host Runtime Dependency**: The output quality depends on the host agent's reasoning capabilities and its access to web search or browser tools.
- **Volatile Travel Data**: Schedules, fares, entry requirements, and opening hours fluctuate frequently. AI-generated data must be treated as indicative.
- **Mandatory Human Review**: Generated travel plans and booking links must always be reviewed by a human before making reservations or non-refundable commitments.
- **Progressive Platform Validation**: Integrations with specific agent environments are validated incrementally; no universal compatibility is claimed.

---

## Contributing & License

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and pull request guidelines.

Distributed under the [MIT License](LICENSE).

