# Roadmap

## Delivered in v1.4.0

- Fail-closed installer and uninstaller with path containment, atomic manifests, symlink refusal, and overwrite restoration.
- One canonical asset tree under `.agents/`; generated compatibility mirror.
- Wheel packaging for all 14 skills, 12 agents, and 9 workflows.
- Unified versioning.
- `TravelDossier v1`, JSON Schema, typed money, claim ledger, evidence taxonomy, freshness, and booking-readiness gate.
- Legacy dossier expansion without destructive conversion.
- Corrected agent dependency graph.
- Explicit `inspiration` and `booking_ready` modes.
- Documentation aligned with the Skills-First active branch.
- Adaptive flight comparison that expands research only when coverage or confidence requires it.
- Regression coverage for China, London, Portugal, flight arithmetic, stale evidence, installer attacks, and compatibility migration.
- CI checks for mirror drift, tests, lint, strict types, and wheel contents.

## Optional extensions beyond the v1.4 remediation

1. Runtime adapters and end-to-end compatibility tests for Codex, Claude Code, Cursor, and other selected hosts.
2. A maintained factual regression corpus covering representative destinations, nationalities, trip types, and stale-source cases.
3. Optional ICS, GeoJSON, and printable PDF exporters consuming validated `TravelDossier v1` files.
4. Optional local read-only MCP wrapper as a separate package, never bundled implicitly with the skills core.
5. Domain ownership verification for airline, railway, hotel, and ticket links beyond blacklist checks.
6. Evaluation metrics for citation coverage, contradiction rate, arithmetic accuracy, freshness, and itinerary feasibility.
