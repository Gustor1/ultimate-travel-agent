# Provider Rate Limits, Caching & Fair-Use Policy — `ultimate-travel-agent`

**Phase:** Phase 10 — Keyless Public Data Integrations  
**Status Date:** 2026-09-13  
**Architecture Policy:** Zero 429 Errors, Thread-Safe Concurrency, Responsible Open Data Stewardship  

---

## 1. Principles of Fair Use

Public open data services are shared community resources financed by non-profits, academic institutions, and public institutions. To prevent denial-of-service, abuse, or blacklisting of user IP addresses, `ultimate-travel-agent` implements **defense-in-depth rate limiting and caching**:

1. **Pre-emptive in-memory rate limiting**: HTTP requests are spaced out locally *before* being transmitted over the wire.
2. **Aggressive multi-tier caching**: Queries are cached in memory for durations aligned with upstream data volatility.
3. **Graceful degradation on 429**: If an upstream server responds with HTTP 429 (Too Many Requests), the client captures the error, attempts to serve stale cached data, and provides clear user feedback.

---

## 2. Rate Limit & Cache Specification Matrix

| Provider | Host Domain | Upstream Policy Limit | Local Rate Limiter Interval | Local Concurrency Protection | In-Memory Cache TTL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo** | `api.open-meteo.com`, `geocoding-api.open-meteo.com` | 10,000 calls / day (Free non-commercial) | **200 ms** (5 req/s max) | Domain Mutex | 1,800 s (30 minutes) |
| **European Central Bank** | `www.ecb.europa.eu` | Updated once per business day (~16:00 CET) | **500 ms** (2 req/s max) | Domain Mutex | 14,400 s (4 hours) |
| **Wikivoyage** | `en.wikivoyage.org` | Wikimedia API Etiquette (Max 200 req/s global) | **330 ms** (3 req/s max) | Domain Mutex | 86,400 s (24 hours) |
| **Nominatim (OSM)** | `nominatim.openstreetmap.org` | **Strict 1 req/s maximum** (OSM AUP) | **1,000 ms** (1 req/s strict) | Global Process Lock (`_NOMINATIM_WORKER_LOCK`) | 86,400 s (24 hours) |
| **Project OSRM** | `router.project-osrm.org` | Public demo server (No SLA) | **1,000 ms** (1 req/s strict) | Domain Mutex | 86,400 s (24 hours) |

---

## 3. Concurrency Protection & Process Mutexes

### 3.1 Nominatim 1 Req/Sec Process Mutex
The OpenStreetMap Nominatim Usage Policy strictly mandates:
> *No more than 1 request per second. Concurrency is strictly prohibited.*

To guarantee compliance even when multiple sub-agents run in parallel (e.g. Wave 1 parallel execution of `destination-researcher` and `transport-planner`), `NominatimProvider` uses a dedicated module-level lock:
```python
_NOMINATIM_WORKER_LOCK = threading.Lock()

with _NOMINATIM_WORKER_LOCK:
    time.sleep(1.0)
    # Execute request
```
This guarantees that no two concurrent threads can dispatch requests to `nominatim.openstreetmap.org` simultaneously or within 1 second of each other.

### 3.2 Domain-Level Token Rate Limiters
`KeylessHttpClient` maintains a thread-safe registry of `RateLimiter` instances keyed by netloc (domain + port). Each `RateLimiter` acquires a lock, checks elapsed time since the previous outbound call, and injects a deterministic `time.sleep` before yielding execution.

---

## 4. Cache Semantics: Hit, Miss, and Stale Fallback

Every cache entry tracks:
- `timestamp`: Unix epoch of retrieval
- `status_code`: HTTP status code
- `body`: Raw string payload
- `ttl_seconds`: Duration before expiry

### Request Lifecycle
```text
User / Agent Tool Call
          │
          ▼
   Check Cache? ──[ Valid (< TTL) ]──► Cache HIT (Served instantly)
          │
       [ Miss / Expired ]
          │
          ▼
   Apply Rate Limiter (Enforce gap)
          │
          ▼
   Dispatch HTTPS Request
          │
   ┌──────┴──────┐
   │             │
[ Success 200 ] [ 429 / 5xx / Timeout / Net Drop ]
   │             │
   ▼             ▼
Update Cache   Has Stale Cache Entry?
(Cache MISS)     ├── YES ──► Cache STALE (Served with advisory)
                 └── NO  ──► Raise ProviderRateLimitError or ProviderNetworkError
                             └──► Sub-agent falls back to deterministic mock
```

---

## 5. Configuration & Overrides

The following environment variables control timeouts and live availability:
```bash
# HTTP network timeout in seconds (default: 5.0)
TRAVEL_HTTP_TIMEOUT=5.0

# Master toggle for live keyless network calls (default: false)
TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=false

# Specific provider live toggles
TRAVEL_MCP_ENABLE_OPEN_METEO=true
TRAVEL_MCP_ENABLE_ECB=true
TRAVEL_MCP_ENABLE_WIKIVOYAGE=true
TRAVEL_MCP_ENABLE_NOMINATIM=false
TRAVEL_MCP_ENABLE_OSRM=false
```
When `TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=false` or an individual toggle is set to `false`, providers operate in offline mock mode without dispatching any network packets.
