# Source Verification Policy

Travel recommendations use claim-level evidence. A source's category, authority, freshness, and supported claims are recorded independently.

## Classification

`source_type` describes what the source is:

- `government`: immigration, foreign affairs, public health, municipal administration.
- `direct_operator`: airline, railway, hotel, museum, transport authority, official ticket office.
- `tourism_institution`: recognized destination board, UNESCO, national park authority.
- `comparison_engine`: metasearch or comparison service used for discovery, not final booking proof.
- `editorial`: established guide, journalist, critic, or research publication.
- `community`: reviews, forums, community maps.
- `social`: social posts and personal blogs used only for discovery.

`authority` describes how the source may support a claim:

- `primary`: entity responsible for the policy, service, schedule, price, or venue.
- `secondary`: independent corroboration or comparison.
- `discovery_only`: lead requiring stronger evidence before operational use.

The legacy Tier 1-6 hierarchy remains available for readers, but it no longer overloads source type and authority.

## Evidence rules

1. Visa, health, border, safety, fare, schedule, cancellation, and admission claims require primary evidence.
2. Important operational claims should be cross-checked when independent authoritative sources exist.
3. Comparison engines may discover options and price discrepancies. They do not prove final airline price or booking terms.
4. Community and social evidence may support noise, atmosphere, accessibility observations, and discovery. It cannot prove legal or operational facts.
5. Each claim lists exact `source_ids`. A source list without claim linkage is insufficient.
6. Every time-sensitive source and claim records `retrieved_at` and `expires_at`.
7. A redirected, dead, login-blocked, or inaccessible page remains unverified unless another primary source confirms the fact.

## Booking-readiness gate

A dossier may set `mode: booking_ready` only when:

- every critical claim is `official_verified` or `cross_checked`;
- every critical claim references at least one current source;
- no referenced critical source is expired;
- `readiness.blockers` is empty;
- prices and totals use typed money records;
- the traveler still performs all purchases and reservations manually.

Otherwise use `mode: inspiration` and list exact verification actions.

See [`travel-dossier-v1.md`](travel-dossier-v1.md) for the schema and default freshness windows.
