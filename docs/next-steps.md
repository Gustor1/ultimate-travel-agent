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

## Delivered through v1.9.0

- Persistent traveler profiles, explainable scoring, uncertainty, research gates, and portable ICS/GeoJSON/PDF/offline exports.
- Four-pass flexible-flight matrices, alternative gateways, self-transfer controls, and exact coverage proof.
- Transit-first hotel comparison, weighted hotel-to-anchor mobility, and evidence-backed neighborhood scoring.
- Door-to-door true cost, scheduled price alerts, adaptive day variants, group vetoes, and time-window route optimization.
- Cascading disruption recovery, controlled booking handoffs, offline trip mode, and an edge-case regression catalog.
- Secure provider-neutral HTTPS/JSON connector with environment credentials, secret redaction, host/path locking, and bounded responses.

## Optional deployment extensions

1. Runtime adapters and end-to-end compatibility tests for Codex, Claude Code, Cursor, and other selected hosts.
2. A maintained live factual regression corpus covering more nationalities and provider accounts; the bundled catalog remains offline and deterministic.
3. Optional local read-only MCP wrapper as a separate package, never bundled implicitly with the skills core.
4. Provider-specific OAuth helpers and response normalizers, enabled only when the operator supplies accounts and accepts provider terms.
5. Domain ownership verification for airline, railway, hotel, and ticket links beyond blacklist checks.
6. Continuous evaluation dashboards for citation coverage, contradiction rate, arithmetic accuracy, freshness, and itinerary feasibility.
