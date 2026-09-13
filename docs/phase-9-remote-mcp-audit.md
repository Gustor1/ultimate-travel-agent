# Phase 9 Transition Audit: Remote MCP & Reusable Skills Pack

**Date:** 2026-09-13  
**Status:** Transition from V1.1/V1.2 Local Architecture to Remote MCP & Skills Distribution  
**System:** `ultimate-travel-agent`  
**Git Baseline:** Branch `main`, 100 passing pytest unit tests, working tree clean  

---

## 1. Executive Summary & Objective

`ultimate-travel-agent` has successfully completed its local foundations (V1.0 CLI & core engine, V1.1 local web UI & contingency planning, V1.2 Provider Hub & 11 travel data integration tools).

The objective of Phase 9 is to decouple the system into two independently reusable artifacts:
1. **Travel Skills Pack (`packages/travel-skills`)**: An installable collection of 6 travel planning, verification, safety, budgeting, and orchestration skills for any Antigravity or compatible agentic workspace.
2. **Ultimate Travel MCP Server (Remote Streamable HTTP)**: A secure, containerized, remote MCP server adhering to the Model Context Protocol specifications (Streamable HTTP / SSE transport), deployable to cloud platforms (Railway, Render, Fly.io, Cloud Run, Docker) and connectable from Antigravity, Claude Code, Cursor, and other MCP clients.

---

## 2. Transition Inventory: Local vs Mock vs Live vs Deployable

| Domain | What Works Locally | What Is Mocked / Offline | What Is Ready for Remote Deploy | What Requires External API Key / Partnership |
| :--- | :--- | :--- | :--- | :--- |
| **CLI & Web UI** | Full CLI (`validate`, `budget`, `plan`, `export`, `serve`) + local FastAPI web UI. | Offline itinerary synthesis, local heuristic budget, fallback weather & transit. | Web UI runnable in Docker; CLI packaged via entrypoint. | None. Zero network required. |
| **Skills Pack** | 6 local agent skills in `.agents/skills/`. | Local instructions and formatting guidance. | Standalone package in `packages/travel-skills` with cross-platform installer. | None. |
| **MCP Server** | Stdio transport (`mcp.server.mcpserver`), 21 tools. | All 11 Provider Hub tools return rich deterministic mocks when in `offline`/`mock` mode. | Streamable HTTP endpoint (`/mcp`) + health endpoints (`/health`, `/ready`, `/version`). | Remote hosting provider + optional dev API key. |
| **Flights** | `MockFlightProvider` (AF, Vueling, Icelandair offers). | Simulated fares, baggage options, official portal URLs. | Fallback pipeline ready; fails closed safely if live key missing. | `AMADEUS_CLIENT_ID` / `AMADEUS_CLIENT_SECRET` or `AVIATION_EDGE_API_KEY`. |
| **Trains** | `MockTrainProvider` (SNCF, Renfe, ICE). | Simulated timetables, door-to-door buffers, transfer warnings. | Fallback pipeline ready. | `SNCF_API_KEY` or `NAVITIA_API_KEY`. |
| **Accommodations** | `MockAccommodationProvider` (Barcelona, Reykjavik, Paris, Rome). | Curated quiet-neighborhood lodgings with simulated prices. | Fallback pipeline ready. Zero auto-booking. | Amadeus Hotel API or Booking.com affiliate/RapidAPI. |
| **Hotel Reviews** | `MockReviewProvider` (sentiment, rating, tags). | Curated reviews (ratings 4.3 - 4.7/5). | Fallback pipeline ready. | `STAYAPI_KEY` or `TRIPADVISOR_API_KEY`. |
| **Activities** | `MockActivityProvider` (indoor Plan B, opening hours). | Curated sights with crowd avoidance & rainy-day backups. | Fallback pipeline ready. | Viator API, GetYourGuide partner API, or OpenTripMap key. |
| **Maps & Routing** | `MockMapsProvider` (haversine distances, multi-modal). | Matrix calculation with transit fatigue warnings. | OpenRouteService or local self-hosted OSRM container. | `OPENROUTESERVICE_API_KEY` or `GOOGLE_MAPS_API_KEY`. |
| **Weather** | `MockWeatherProvider` (seasonal historical climate). | Monthly temperature & precipitation distributions. | Open-Meteo adapter (no key required for non-commercial). | `OPENWEATHERMAP_API_KEY` (optional). |
| **Currency** | `MockCurrencyProvider` (hardcoded base rates). | Reference rates with +5% bank conversion margin. | ECB XML feed adapter (no key required, public ECB data). | Live real-time commercial forex API (optional). |
| **Guides & Editorial**| `MockGuideProvider` (neighborhood tips, etiquette). | Curated cultural notes, transport guidelines. | Wikivoyage API adapter (public MediaWiki API). | None. |
| **Social Trends** | `SocialDiscoveryProvider`. | Curated trends tagged `social_discovery_only`. | Strict verification tagging in place. | Social media scrapers/APIs (read-only only). |

---

## 3. Strict Verification & Safety Policy

1. **Zero Secret Leakage**: Provider API keys, credentials, and internal host details must never appear in MCP tool outputs, log files, or health endpoint responses.
2. **Never Mask Mocks as Live**: Any data returned from a mock provider or fallback must explicitly declare `mode: "mock"` or `mode: "offline"` and `verification_level: "unverified"` or `"community_recommended"`.
3. **Fail-Closed Live Mode**: When `mode="live"`, unconfigured providers must immediately raise or return `ProviderConfigurationError` explaining which configuration or key is absent.
4. **Zero Automated Transactions**: direct bookings, payment authorizations, cart checkouts, and PNR creations remain strictly forbidden across both stdio and remote HTTP interfaces.

---

## 4. Required Deliverables for Phase 9

1. `packages/travel-skills/` containing:
   - 6 audited travel skills (`travel-planning`, `source-verification`, `budget-validation`, `travel-safety`, `multi-agent-orchestration`, `mcp-skill-auditing`).
   - `manifest.json` describing package metadata, skills, version, and dependencies (none).
   - `install.py` & `uninstall.py` scripts executable without third-party dependencies.
   - Example consuming workspaces (`minimal-project`, `travel-project`).
2. CLI enhancements:
   - `ultimate-travel-agent install-skills --target <path> [--force]`
   - `ultimate-travel-agent uninstall-skills --target <path>`
   - `ultimate-travel-agent list-skills`
   - `ultimate-travel-agent mcp-http --host <host> --port <port>`
3. Secure Remote MCP Server:
   - `src/ultimate_travel_agent/mcp/http_server.py`: Streamable HTTP server on `/mcp` with `/health`, `/ready`, `/version`.
   - `src/ultimate_travel_agent/mcp/auth.py`: Token verification, API key authentication, and extensible OAuth/OIDC hooks.
   - `src/ultimate_travel_agent/mcp/config.py`: Environment-driven server configuration with validation and safe defaults.
   - `src/ultimate_travel_agent/mcp/health.py`: Sanitized health reporting.
4. Server Security:
   - Request size limiting, in-memory rate limiting, CORS configuration, request ID injection, credential redaction in logs.
5. Provider Hub Registry Configuration:
   - `config/providers.example.yaml`: Declarative provider selection and credential mapping.
   - Dynamic provider selection via environment variables (`TRAVEL_PROVIDER_*`).
6. Cloud Deployment & Containerization:
   - `Dockerfile` (non-root user, lightweight multi-stage or slim python), `docker-compose.yml`, `.dockerignore`.
   - Deployment templates for Railway, Render, Google Cloud Run, and Fly.io.
7. Ready-to-use Client Configurations:
   - Antigravity (local stdio & remote HTTP).
   - Claude Code (local stdio & remote HTTP).
   - Cursor (remote HTTP).
8. Comprehensive Verification:
   - 100% offline unit tests covering skills installer, MCP HTTP endpoints, auth, security middleware, provider registry, and client config files.
