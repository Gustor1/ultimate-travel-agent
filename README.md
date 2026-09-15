# Ultimate Travel Agent

An open-source **Travel Skills Pack** for AI agents.

[![CI](https://github.com/Gustor1/ultimate-travel-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Gustor1/ultimate-travel-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills-First](https://img.shields.io/badge/Architecture-Skills--First-blue.svg)](#skills-first-approach)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

---

## Skills-First Approach

`ultimate-travel-agent` is an open-source, local-first travel planning toolkit designed for AI coding environments like **Antigravity**, Claude Code, and Cursor.

Following our Phase 11 architectural pivot, the project focuses entirely on a **Skills-First** model:
- **No commercial API keys required**: No Amadeus, Trip.com, TripAdvisor, Google Maps, or Viator accounts needed.
- **No mandatory cloud servers or SaaS subscriptions**: Operates locally on your machine.
- **Tool-Adaptive**: The AI leverages the web search and browser tools already present in its runtime environment to find up-to-date travel information.
- **Safe Offline Fallback**: If web search tools are absent, the skills execute a safe estimation protocol without inventing fares or hours.
- **Strict Safety Invariants**: The system **never** makes purchases, **never** books rooms or flights, **never** collects credit card or passport details, and **never** bypasses paywalls.

> [!NOTE]
> The previous experimental remote MCP server, Docker manifests, and commercial provider adapters have been safely preserved on the archive branch:
> [`archive/mcp-api-prototype-v1.2`](https://github.com/Gustor1/ultimate-travel-agent/tree/archive/mcp-api-prototype-v1.2).

---

## The 13 Core Travel Skills

The repository distributes 13 specialized, modular skills:

1. **`travel-orchestrator`**: Master coordinator managing the 5-wave planning lifecycle and assembling the final travel dossier.
2. **`travel-web-research`**: Researches destination climate, regional norms, and seasonal crowd windows.
3. **`transport-research`**: Compares door-to-door transit options (air, rail, road, ferry) with official links.
4. **`accommodation-research`**: Vets strategic neighborhoods and curates a shortlist of 3-5 accommodations.
5. **`activity-curator`**: Curates cultural, culinary, and outdoor experiences with anti-crowd tactics and rain backups.
6. **`local-discovery`**: Scouts authentic neighborhood eateries and hidden gems, tagging community sources.
7. **`itinerary-builder`**: Assembles chronological daily schedules with geographic clustering to prevent backtracking.
8. **`budget-and-booking-checker`**: Audits line-item costs, enforces 10-15% safety reserves, and lists booking deadlines.
9. **`travel-safety`**: Reviews visa rules, passport validity, health advisories, and emergency protocols.
10. **`source-verification`**: Cross-checks facts, hours, and fares against a strict 6-tier sourcing hierarchy.
11. **`travel-quality-control`**: Audits transit feasibility, pacing realism, and budget arithmetic before delivery.
12. **`multi-agent-orchestration`**: Provides execution topologies and dependency graphs for multi-agent teams.
13. **`mcp-skill-auditing`**: Audits external tools and MCP servers for security and credential safety.

See the complete [Skills Catalog](docs/skills-catalog.md) for detailed descriptions.

---

## Installation in Any Antigravity Project

You can install this Travel Skills Pack into any other Antigravity project with a single command:

```bash
# Clone or navigate to ultimate-travel-agent:
git clone https://github.com/Gustor1/ultimate-travel-agent.git
cd ultimate-travel-agent

# Install the 13 skills into your target project:
python -m ultimate_travel_agent.cli install-skills --target /path/to/my-project
```

### Installing Sub-Agents and Workflows

To also install the 11 specialized sub-agents and 9 end-to-end workflows:

```bash
python -m ultimate_travel_agent.cli install-skills \
  --target /path/to/my-project \
  --include-agents \
  --include-workflows
```

See [Installation Guide](docs/install-in-any-project.md) for full documentation.

---

## How to Plan a Complete Trip

### Step 1: Fill Out a Trip Brief
Copy the universal template from [`examples/trip-brief-template.md`](examples/trip-brief-template.md):

```markdown
Destination(s): Tokyo & Kyoto, Japan
Dates or duration: October 18 - October 24 (7 days)
Origin: Paris (CDG)
Travelers: 2 adults (couple)
Budget and currency: €3,000 EUR
Pace preference: balanced
Interests: Gastronomy, historic temples, modern architecture
```

Explore full realistic examples:
- [Tokyo & Kyoto City Break](examples/city-break-brief.md)
- [Scottish Highlands Road Trip](examples/road-trip-brief.md)
- [Western Norway Fjords Solo Trip](examples/nature-low-crowd-brief.md)

### Step 2: Trigger the Workflow in Antigravity
Prompt Antigravity:

```text
Follow the workflow .agents/workflows/plan-complete-trip.md using this brief:
[Paste your filled brief here]
```

### Step 3: Receive Your Sourced Travel Dossier
The agents will execute across 5 waves, producing:
- A day-by-day chronological itinerary clustered by neighborhood.
- Door-to-door transit plans with official operator links.
- Vetted lodging recommendations with cancellation terms.
- Rainy day backup plans (Plan B) for every outdoor activity.
- An itemized budget with a 15% safety contingency reserve.
- A pre-departure checklist for visas, vaccinations, and currency.
- A pre-booking verification action list with direct official links.

---

## Sourcing Hierarchy

All agents strictly follow our [6-Tier Sourcing Policy](docs/source-verification.md):

- **Tier 1**: Official government portals, tourism ministries, embassies.
- **Tier 2**: Direct transport operators (rail, airlines) and official museum box offices.
- **Tier 3**: Recognized regional tourism institutions and public park authorities.
- **Tier 4**: Authoritative editorial guides (Michelin, Lonely Planet).
- **Tier 5**: Community reviews (TripAdvisor, Google Reviews) for qualitative feedback only.
- **Tier 6**: Social media (TikTok, RedNote) tagged strictly as `social_discovery_only`.

---

## Example Structured Output

```yaml
summary: "7-day balanced cultural and culinary itinerary in Tokyo and Kyoto for 2 adults (€2,950 total estimated)."
recommendations:
  - transit: "Tokaido Shinkansen Hikari between Tokyo and Kyoto (2h15m, mountain-side window seats for Mt Fuji view)."
  - lodging: "Traditional boutique ryokan in Kyoto Karasuma district with quiet courtyard rooms."
  - activity: "Dawn hike at Fushimi Inari Taisha (07:00 entry to avoid peak tour bus crowds)."
  - rain_plan_b: "Museum of Fine Arts and indoor Mercado de Triana craft market."
source_log:
  - name: "Kyoto City Official Travel Guide"
    tier: 1
    url: "https://kyoto.travel/en/"
verification_required:
  - "Verify Shinkansen oversized baggage rules if luggage exceeds 160 cm linear dimensions."
  - "Confirm tea ceremony timed slot 30 days in advance."
risks:
  - "Autumn foliage peak can cause crowded transit between Gion and Arashiyama."
```

---

## Safety & Invariants

- **No Bookings or Payments**: The agent provides direct links; you book directly with the provider.
- **No Personal Data Stored**: No passport numbers, credit cards, or passwords required.
- **Transparent Verification**: Unconfirmed estimates are explicitly flagged.
- **Open Source**: Released under the permissive [MIT License](LICENSE).

---

## Project Documentation

- [Skills Catalog](docs/skills-catalog.md)
- [How to Use with Antigravity](docs/use-with-antigravity.md)
- [Using with Browser Tools & Offline Fallback](docs/use-with-browser-tools.md)
- [Sourcing Hierarchy & Verification](docs/source-verification.md)
- [Cross-Project Installation](docs/install-in-any-project.md)
- [Skills-First Pivot Audit](docs/skills-first-pivot-audit.md)
- [Archived MCP/API Prototype](https://github.com/Gustor1/ultimate-travel-agent/tree/archive/mcp-api-prototype-v1.2)
