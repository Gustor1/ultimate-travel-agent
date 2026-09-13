# Ultimate Travel Agent 🌍✈️

> **A generic, privacy-first, multi-agent travel planning system generating verified, realistic, day-by-day itineraries with budget estimation and zero required external accounts.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## Highlights

- **Universal & Generic**: Adapts to any trip style (city-trip, road-trip, nature/landscape, multi-city, solo, couple, family, friends, slow travel).
- **11 Specialized Agents**: Coordinated in structured waves (exploration, budgeting, scheduling, quality control, orchestration).
- **Offline & Privacy-First**: 100% functional out-of-the-box using local mock data. No mandatory API keys, no tracking, zero sensitive credentials stored in Git.
- **Evidence-Based & Sourced**: Every recommendation flags its verification level (`official_verified`, `cross_checked`, `community_recommended`, `social_discovery_only`, `unverified`, `outdated`).
- **Safety First**: **Never** books or makes irreversible payments automatically. All recommendations provide verified official booking links for user control.
- **MCP Server Included**: Model Context Protocol interface exposing read-only and computation tools for Claude Desktop, Cursor, or any MCP client.

---

## Multi-Agent Architecture

```text
Wave 1 (Parallel Exploration)
  ├── destination-researcher       Geographic context & quiet travel periods
  ├── transport-planner            Door-to-door transit & official booking links
  ├── accommodation-researcher     Strategic neighborhood curation
  ├── activity-curator             Crowd-aware activity planning
  ├── local-discovery-agent        Local gems & authentic dining (flagged as unverified)
  └── travel-preparation-agent     Visa, health, and entry requirements checklist

Wave 2 (Budget Consolidation)
  └── budget-analyst               Multi-currency breakdown & safety buffers

Wave 3 (Itinerary Optimization)
  └── itinerary-optimizer          Day-by-day scheduling with weather contingency

Wave 4 (Quality & Safety Gate)
  ├── quality-controller           Consistency checks & pacing balance
  └── mcp-skill-auditor            URL allowlist audit & prompt injection defense

Wave 5 (Synthesis)
  └── travel-orchestrator          Final trip dossier compilation
```

---

## Quick Start

### 1. Installation

```bash
git clone https://github.com/ultimate-travel-agent/ultimate-travel-agent.git
cd ultimate-travel-agent

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package and dependencies
pip install -e .
```

### 2. Run Tests

```bash
pytest
```

### 3. Run a Trip Planning Workflow

```bash
# Run the automated 5-wave demo with local mock data
python examples/demo_run.py

# Validate an example trip
python -m ultimate_travel_agent.cli validate examples/city-trip/trip.json

# Calculate budget for a trip
python -m ultimate_travel_agent.cli budget examples/city-trip/trip.json

# Generate itinerary summary across all 5 waves
python -m ultimate_travel_agent.cli plan examples/city-trip/trip.json

# Export complete Markdown travel dossier
python -m ultimate_travel_agent.cli export examples/city-trip/trip.json --output reports/barcelona.md
```

### 4. Start Local MCP Server

```bash
python -m ultimate_travel_agent.mcp.server
```

See [docs/getting-started.md](docs/getting-started.md) and [docs/use-this-template.md](docs/use-this-template.md) for full setup guides.

---

## Repository Structure

```text
ultimate-travel-agent/
├── README.md                          # Project overview and quick start
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                   # Contribution guidelines
├── SECURITY.md                        # Security policy and threat model
├── CODE_OF_CONDUCT.md                 # Contributor covenant
├── .env.example                       # Sample environment variables
├── pyproject.toml                     # Python dependencies & tooling
├── .agents/
│   ├── agents/                        # 11 Agent definitions and system prompts
│   ├── skills/                        # Core capabilities
│   └── workflows/                     # Multi-agent orchestrations
├── data/
│   ├── schemas/                       # JSON Schemas for validation
│   └── examples/                      # Reference trip data
├── src/ultimate_travel_agent/
│   ├── models/                        # Pydantic v2 data models
│   ├── agents/                        # Agent implementations
│   ├── mcp/                           # Local MCP server
│   └── integrations/                  # Optional external service adapters
├── tests/                             # Pytest test suite
├── docs/                              # Technical documentation
└── examples/
    ├── city-trip/                     # Barcelona 3-day example
    └── road-trip/                     # Iceland / Norway road-trip example
```

---

## Verification Levels

Every element (lodging, transport, activity, rule) carries an explicit verification status:
- `official_verified`: Directly verified against official government or ticketing source.
- `cross_checked`: Confirmed across multiple reputable guidebooks or platforms.
- `community_recommended`: Highly rated by travel communities (e.g. forums, blogs).
- `social_discovery_only`: Discovered via social media (TikTok, RedNote, Instagram), requiring verification.
- `unverified`: Preliminary finding not yet independently corroborated.
- `outdated`: Previously valid information that requires refreshing.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
