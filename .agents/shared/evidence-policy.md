# Evidence policy

Record source category, authority, independence, applicability, and freshness separately.

## Classification

`source_type`: `government`, `direct_operator`, `tourism_institution`, `comparison_engine`, `editorial`, `community`, or `social`.

`authority`: `primary`, `secondary`, or `discovery_only`. The legacy Tier 1 through Tier 6 label may be displayed but is not a confidence score and never replaces these fields.

`independence_group` identifies the upstream publisher or inventory feed. Two pages in one group count as one corroborating origin.

## Claim record

Each changeable or consequential fact has one atomic `claim_id`, exact normalized value, applicability, source IDs, status, `observed_at`, effective period when known, `expires_at`, confidence rationale, conflicts, and fallback. A source list without claim linkage is insufficient.

Primary evidence is required for legal, health, safety, price, schedule, cancellation, admission, availability, and accessibility claims used operationally. Community evidence may support qualitative patterns; social evidence discovers candidates only. Cross-check critical claims when an independent authoritative source exists.

## Default freshness

- Live fare or availability: same day, at most 24 hours.
- Cancellation or payment terms: 24 hours.
- Timetable, opening hours, admission, or access policy: 7 days.
- Entry, health, or safety rule: verify within 24 hours of final delivery and again before departure.
- Climate normals and durable context: 180 days.
- Community or social discovery: 30 days and never booking proof.

Use a shorter window when the publisher or event indicates faster change. An inaccessible, redirected, or login-blocked page does not verify a claim.

## Evidence sufficiency

`pending: 0` proves execution only. A recommendation also needs the skill's minimum qualified set, comparable fields, primary evidence for critical facts, and no unresolved material conflict. State `INSUFFICIENT_EVIDENCE` when these conditions fail.
