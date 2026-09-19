# Offline Mode

Offline mode loads skills, validates local files, performs explicit arithmetic, and organizes user-provided facts. It does not contain a hidden travel database, deterministic itinerary engine, MCP server, FastAPI interface, live provider adapter, or current fare inventory.

## Supported offline work

- Parse and structure a trip brief.
- Build candidate day layouts from user-provided places and durations.
- Calculate typed budgets and safety reserves.
- Detect missing fields, duplicate identifiers, broken evidence references, arithmetic errors, and expired claims.
- Produce research and booking verification checklists.
- Install, validate, and remove the declarative bundle.

## Unsupported offline claims

Offline mode cannot confirm availability, current fares, opening hours, border rules, health requirements, disruptions, weather forecasts, cancellation terms, or live booking links.

Use `mode: inspiration`. Keep `readiness.booking_ready: false`. List every missing live check in `verification_required` and `readiness.blockers`.

Offline output may use clearly labeled estimates for rough budgeting. Never attach a current-looking verification date to an estimate that was not retrieved.
