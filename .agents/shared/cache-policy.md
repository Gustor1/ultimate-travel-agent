# Evidence cache and resume policy

Reuse work only when it remains applicable and current; caching must never turn stale data into confidence.

## Cache identity

Build a content-addressed key from the normalized query intent, source/provider identity, relevant date/product/direction dimensions, and a non-PII applicability fingerprint of the brief. Cosmetic wording changes must not create a new key; different dates, occupancy, traveler eligibility, fare/rate class, or jurisdiction must.

Store the normalized result, stable claim/source IDs, retrieval time, `expires_at`, source validator metadata when available, and the terminal coverage cell. Never cache credentials, cookies, personal/document/payment data, full browser sessions, or raw pages containing unnecessary user data.

## Reuse and invalidation

- Reuse a record only when its applicability fingerprint matches and it is not expired.
- Resume terminal current cells; rerun pending, failed, expired, contradicted, or explicitly invalidated cells.
- Invalidate when the source reports a change, the brief changes a relevant dimension, a dependent decision changes, or a newer authoritative claim conflicts.
- Durable context may use the evidence-policy freshness window. Availability, live price, cancellation, entry, health, safety, and disruption records use their short window.
- Recheck critical claims at the final readiness gate even if an earlier cache entry remains technically current when the policy requires a newer pre-departure check.

Record `cache_hit`, originating run/source IDs, and invalidation reason. A cache miss is normal; never widen the key until unlike facts collide merely to increase hit rate.
