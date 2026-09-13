# Connecting Ultimate Travel Agent from Any AI Project

This guide explains how to import and use Ultimate Travel Agent's capabilities (Travel Skills Pack and Ultimate Travel MCP Server) inside any third-party AI project (Antigravity, Claude Code, Cursor, Windsurf, or custom agent frameworks).

---

## 1. Architecture Overview

```text
Any AI Project (Antigravity / Claude Code / Cursor)
       │
       ├── 1. Travel Skills Pack (installed into .agents/skills/)
       │      Provides reasoning directives: safety, budgeting, crowd avoidance, source verification
       │
       └── 2. MCP Connection (Local stdio OR Remote Streamable HTTP)
              Provides 21 query and validation tools via Model Context Protocol
```

---

## 2. Step 1 — Installing the Travel Skills Pack

Skills provide your AI agent with structured guidelines for travel calculations and safety audits without needing to install the Python codebase in your target workspace.

From the `ultimate-travel-agent` directory:

```bash
# Using CLI
ultimate-travel-agent install-skills --target /path/to/your-project

# Or using the portable python script directly
python packages/travel-skills/install.py --target /path/to/your-project
```

This copies the 6 travel skills into `<your-project>/.agents/skills/`:
- `travel-planning`
- `source-verification`
- `budget-validation`
- `travel-safety`
- `multi-agent-orchestration`
- `mcp-skill-auditing`

Existing skills in your project will **not** be overwritten unless `--force` is specified.

---

## 3. Step 2 — Connecting the Local MCP Server (Stdio)

If you have `ultimate-travel-agent` installed on your machine and want to run it as a local process:

### Antigravity (`~/.antigravity/mcp_config.json`)
```json
{
  "mcpServers": {
    "ultimate-travel-agent-local": {
      "command": "python",
      "args": ["-m", "ultimate_travel_agent.mcp.server"]
    }
  }
}
```

### Claude Code (`~/.claude/settings.json`)
```json
{
  "mcpServers": {
    "ultimate-travel-agent": {
      "command": "python",
      "args": ["-m", "ultimate_travel_agent.mcp.server"]
    }
  }
}
```

---

## 4. Step 3 — Connecting the Remote MCP Server (HTTPS)

If the server is deployed to Railway, Render, Fly.io, Cloud Run, or your private cloud:

### Antigravity (`~/.antigravity/mcp_config.json`)
```json
{
  "mcpServers": {
    "ultimate-travel-agent-remote": {
      "url": "https://YOUR-TRAVEL-MCP-DOMAIN/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TRAVEL_MCP_API_KEY"
      }
    }
  }
}
```

### Claude Code (`~/.claude/settings.json`)
```json
{
  "mcpServers": {
    "ultimate-travel-agent-remote": {
      "type": "http",
      "url": "https://YOUR-TRAVEL-MCP-DOMAIN/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TRAVEL_MCP_API_KEY"
      }
    }
  }
}
```

### Cursor (`~/.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "ultimate-travel-mcp": {
      "url": "https://YOUR-TRAVEL-MCP-DOMAIN/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TRAVEL_MCP_API_KEY"
      }
    }
  }
}
```

---

## 5. Step 4 — Using MCP Tools in Prompts

Once connected, your AI client has access to 21 travel planning and data tools. You can query them naturally in your conversations:

- **Compare flights:**
  > "Use `search_flight_options` for a round-trip from Paris (PAR) to Barcelona (BCN) departing 2026-10-15 and returning 2026-10-19 for 2 passengers."

- **Find quiet accommodations:**
  > "Use `search_accommodation_options` to find hotels in Barcelona in quiet neighborhoods under 180 EUR per night."

- **Check weather and contingencies:**
  > "Use `get_weather_outlook` for Barcelona in October and suggest indoor Plan B options."

- **Calculate budget with safety reserves:**
  > "Use `calculate_budget` with safety buffer percentage 12.0."

---

## 6. Step 5 — Understanding Operational Modes

Every travel query tool accepts a `mode` parameter:

| Mode | Behavior | Use Case |
| :--- | :--- | :--- |
| **`offline`** *(default)* | Uses deterministic local heuristics and fallback models. No network queries. | Fast local development, CI pipelines, unit testing, privacy-sensitive offline use. |
| **`mock`** | Returns rich simulated payloads mirroring real airline/train/hotel API structures with representative fares and booking URLs. | Interface prototyping, agent prompt engineering, integration demonstrations. |
| **`live`** | Queries external partner APIs (Amadeus, SNCF, OpenRouteService, etc.). Requires backend API keys. | Real-time production trip planning. Fails closed with `ProviderConfigurationError` if unconfigured. |

---

## 7. Step 6 — Disconnecting or Removing

### Removing Skills from Target Project
```bash
# Using CLI
ultimate-travel-agent uninstall-skills --target /path/to/your-project

# Or using Python script
python packages/travel-skills/uninstall.py --target /path/to/your-project
```

### Removing MCP Server Connection
Delete the `ultimate-travel-agent` entry from your client configuration file (`mcp_config.json`, `settings.json`, or `mcp.json`).
