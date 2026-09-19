# TravelDossier v1

`TravelDossier v1` is the shared output contract for skills, agents, workflows, examples, and validators.

Machine-readable schema: [`src/ultimate_travel_agent/schemas/travel_dossier_v1.schema.json`](../src/ultimate_travel_agent/schemas/travel_dossier_v1.schema.json).

Illustrative, deliberately non-live fixture: [`examples/travel-dossier-v1.example.yaml`](../examples/travel-dossier-v1.example.yaml).

## Modes

- `inspiration`: may contain estimates and unverified discoveries. Never present this mode as purchase-ready.
- `booking_ready`: every critical price, schedule, entry rule, cancellation rule, and availability-dependent statement must be current and linked to primary evidence. Any blocker keeps the dossier out of this mode.

## Minimal envelope

```yaml
schema_version: travel-dossier/v1
mode: inspiration
status: partial
summary: ""
recommendations: []
claims: []
sources: []
costs: []
assumptions: []
missing_information: []
verification_required: []
risks: []
readiness:
  booking_ready: false
  blockers: []
```

## Claim ledger

Every factual statement that can change or cause financial, legal, health, or operational harm gets a stable `claim_id`.

```yaml
claims:
  - claim_id: flight.af123.price
    text: "Illustrative total fare is EUR 420 for two travelers."
    status: official_verified
    source_ids: [airline.af.booking]
    critical: true
    observed_at: 2026-09-19
    expires_at: 2026-09-20
```

`status` values: `official_verified`, `cross_checked`, `community_recommended`, `social_discovery_only`, `estimated`, `unverified`, `outdated`.

## Evidence model

Source type and authority are independent. A comparison engine is not an editorial source. A community review can still provide useful discovery evidence without becoming authoritative.

```yaml
sources:
  - source_id: airline.af.booking
    name: Air France booking engine
    url: https://wwws.airfrance.fr/search/open-dates
    source_type: direct_operator
    authority: primary
    retrieved_at: 2026-09-19
    expires_at: 2026-09-20
```

Supported `source_type` values: `government`, `direct_operator`, `tourism_institution`, `comparison_engine`, `editorial`, `community`, `social`.

Supported `authority` values: `primary`, `secondary`, `discovery_only`.

Legacy `tier` remains optional for display compatibility. It does not replace `source_type` or `authority`.

## Freshness defaults

Apply a shorter expiry when the source itself indicates faster change.

- Live fare or availability: same day, maximum 24 hours.
- Timetable, opening hours, ticket policy: 7 days.
- Entry, visa, health, or safety rule: 24 hours before final delivery and recheck before departure.
- Cancellation terms: 24 hours.
- Climate normals or durable cultural context: 180 days.
- Community or social discovery: 30 days, never booking proof.

## Money

Store money as exact values, not formatted prose.

```yaml
costs:
  - amount: "65.00"
    currency: EUR
    quantity: "2"
    total: "130.00"
```

Formatted explanations may appear in `recommendations`, but totals must be calculated from atomic cost records.

## Legacy migration

The validator accepts old envelopes containing `source_log`. It converts them to v1 in memory and keeps `booking_ready: false` until claim-level evidence exists. No destructive migration occurs.

Validate a dossier:

```bash
ultimate-travel-agent validate-dossier dossier.yaml
```
