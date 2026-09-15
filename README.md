# Ultimate Travel Agent

An open-source **Travel Skills Pack** for AI agents.

[![CI](https://github.com/Gustor1/ultimate-travel-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Gustor1/ultimate-travel-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills-First](https://img.shields.io/badge/Architecture-Skills--First-blue.svg)](#skills-first-approach)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[Documentation en Français](docs/install-in-any-project.fr.md) | [Catalogue des Skills (FR)](docs/skills-catalog.fr.md) | [Utilisation Antigravity (FR)](docs/use-with-antigravity.fr.md)

---

## ⚡ Quick Start (< 2 Minutes)

Install the 13 travel skills, 11 sub-agents, and 9 workflows directly into your Antigravity project:

```bash
# 1. Clone ultimate-travel-agent:
git clone https://github.com/Gustor1/ultimate-travel-agent.git
cd ultimate-travel-agent

# 2. Install everything into your target project:
python -m ultimate_travel_agent.cli install-skills \
  --target /path/to/my-project \
  --include-agents \
  --include-workflows
```

Then, open your project in Antigravity, copy a brief from [`examples/trip-brief-template.md`](examples/trip-brief-template.md) (or [`examples/trip-brief-template.fr.md`](examples/trip-brief-template.fr.md)), and prompt:

```text
Follow the workflow .agents/workflows/plan-complete-trip.md using this brief:
[Paste your brief here]
```

---

## What is Ultimate Travel Agent?

`ultimate-travel-agent` is an open-source, local-first toolkit that gives your AI assistant the capability to plan realistic, sourced, and well-budgeted trips without relying on expensive proprietary travel APIs or third-party cloud services.

### Skills-First Approach
- **No API keys or developer accounts required**: No Amadeus, Trip.com, TripAdvisor, Google Maps, or Viator subscriptions.
- **Tool-Adaptive**: The AI leverages the web search and browser tools already active in your environment (Antigravity, Claude Code, Cursor) to find real schedules and operator booking links.
- **Safe Offline Fallback**: If web search tools are unavailable, the skills execute a safe estimation protocol without inventing fares or hours.
- **Strict Safety Invariants**: The system **never** makes automatic purchases, **never** books rooms or flights, **never** asks for credit cards or passports, and **never** bypasses paywalls.
- **Manifest-Based Safe Uninstallation**: Only files installed by the toolkit are removed. Your custom skills, agents, and user-modified files are safely preserved.

> [!NOTE]
> The previous experimental remote MCP server, Docker virtualization, and commercial provider adapters are safely preserved on the archive branch:
> [`archive/mcp-api-prototype-v1.2`](https://github.com/Gustor1/ultimate-travel-agent/tree/archive/mcp-api-prototype-v1.2).

---

## The 13 Core Travel Skills

| Skill | Role |
|---|---|
| [`travel-orchestrator`](.agents/skills/travel-orchestrator/SKILL.md) | Coordinates the 5-wave planning lifecycle and consolidates the final travel dossier. |
| [`travel-web-research`](.agents/skills/travel-web-research/SKILL.md) | 12-step research protocol for climate, crowd calendars, and official operator data. |
| [`transport-research`](.agents/skills/transport-research/SKILL.md) | Door-to-door multi-modal transit comparison (air, rail, road, ferry) with official links. |
| [`accommodation-research`](.agents/skills/accommodation-research/SKILL.md) | Vets strategic neighborhoods and curates 3-5 accommodations with cancellation terms. |
| [`activity-curator`](.agents/skills/activity-curator/SKILL.md) | Curates cultural, culinary, and outdoor experiences with anti-crowd tactics and rain backups. |
| [`local-discovery`](.agents/skills/local-discovery/SKILL.md) | Scouts authentic neighborhood eateries and hidden gems, tagging community sources. |
| [`itinerary-builder`](.agents/skills/itinerary-builder/SKILL.md) | Assembles daily schedules with geographic clustering to eliminate backtracking. |
| [`budget-and-booking-checker`](.agents/skills/budget-and-booking-checker/SKILL.md) | Audits line items, adds a 10-15% safety reserve, and generates booking timelines. |
| [`travel-safety`](.agents/skills/travel-safety/SKILL.md) | Reviews entry visas, passport validity, health prerequisites, and emergency plans. |
| [`source-verification`](.agents/skills/source-verification/SKILL.md) | Cross-checks claims against our strict 6-tier sourcing hierarchy. |
| [`travel-quality-control`](.agents/skills/travel-quality-control/SKILL.md) | Audits transit feasibility, pacing realism, and budget arithmetic before delivery. |
| [`multi-agent-orchestration`](.agents/skills/multi-agent-orchestration/SKILL.md) | Provides execution topologies and dependency graphs for multi-agent teams. |
| [`mcp-skill-auditing`](.agents/skills/mcp-skill-auditing/SKILL.md) | Audits external tools and MCP servers for security and credential safety. |

See the complete [Skills Catalog (EN)](docs/skills-catalog.md) or [Catalogue des Skills (FR)](docs/skills-catalog.fr.md).

---

## 6 Realistic Demonstration Scenarios

Explore full scenario briefs and their corresponding expected outputs in [`examples/scenarios/`](examples/scenarios/):

1. [Barcelona 4-Day Cultural City Break](examples/scenarios/city-break-europe.md) → [Expected Output](examples/expected-outputs/city-break-europe-output.md)
2. [Iceland 7-Day Ring Road Nature Expedition](examples/scenarios/road-trip-nature.md) → [Expected Output](examples/expected-outputs/road-trip-nature-output.md)
3. [Brittany & Normandy 6-Day Family Vacation](examples/scenarios/family-trip.md) → [Expected Output](examples/expected-outputs/family-trip-output.md)
4. [Vietnam 10-Day Central Backpacking Adventure](examples/scenarios/backpacking-budget.md) → [Expected Output](examples/expected-outputs/backpacking-budget-output.md)
5. [Umbria 5-Day Low-Crowd Hill Town Exploration](examples/scenarios/low-crowd-cultural-trip.md) → [Expected Output](examples/expected-outputs/low-crowd-cultural-trip-output.md)
6. [London 3-Day Corporate Trip + West End Evening](examples/scenarios/business-trip.md) → [Expected Output](examples/expected-outputs/business-trip-output.md)

---

## Safe, Non-Destructive Uninstallation

Unlike naive installers, `ultimate-travel-agent` records every file it creates in `<target>/.agents/.ultimate-travel-agent-install.json` with SHA-256 hashes.

To uninstall:
```bash
python -m ultimate_travel_agent.cli uninstall-skills --target /path/to/my-project
```

- **User-Created Skills Protected**: Any skill you added yourself (e.g. `.agents/skills/my-ski-skill/`) is never touched.
- **User Modifications Protected**: If you edited an installed skill, it will **not** be deleted automatically.
- **Clean Empty Directories**: Folders are only removed if they become completely empty.

---

## Sourcing Hierarchy & Disclaimers

All agents follow our [6-Tier Sourcing Policy](docs/source-verification.md):
- **Tier 1**: Official government portals, tourism ministries, embassies.
- **Tier 2**: Direct transport operators (rail, airlines) and official museum box offices.
- **Tier 3**: Recognized regional tourism institutions and public park authorities.
- **Tier 4**: Authoritative editorial guides (Michelin, Lonely Planet).
- **Tier 5**: Community reviews (TripAdvisor, Google Reviews) for qualitative feedback only.
- **Tier 6**: Social media (TikTok, RedNote) tagged strictly as `social_discovery_only`.

> [!IMPORTANT]
> **No Guaranteed Fares or Availability**: The AI does not have real-time access to live airline seat inventory or hotel reservation databases. All prices and timetables must be verified by the user on the provided official operator links prior to travel.

---

## License & Contributing

Distributed under the [MIT License](LICENSE). Open to contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).
