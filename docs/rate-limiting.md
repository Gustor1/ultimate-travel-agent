# Rate Limiting Architecture & Configuration

This guide describes how rate limiting is implemented in the Ultimate Travel MCP Server, how to tune its parameters, and how clients handle throttling.

---

## 1. Rate Limiting Algorithm

The server employs an **in-memory token bucket algorithm** (`InMemoryRateLimiter` in `src/ultimate_travel_agent/mcp/security.py`):

- Each unique client IP receives a dedicated token bucket initialized with a maximum token capacity (`burst`).
- Tokens replenish continuously at a steady rate (`rps` = requests per second).
- Every non-preflight HTTP request costs 1 token.
- If tokens fall below 1.0, the request is immediately rejected with HTTP status `429 Too Many Requests`.

### Client Identification
When deployed behind reverse proxies or cloud load balancers (Cloud Run, Railway, Render, Fly.io, Cloudflare), the client IP is extracted from the first entry of the `X-Forwarded-For` header. If absent, the direct socket connection host IP is used.

---

## 2. Configuration Parameters

Rate limiting is tuned via server environment variables:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `TRAVEL_MCP_RATE_LIMIT_ENABLED` | Boolean | `true` | Set to `false` to disable rate limiting (e.g. for offline benchmarking). |
| `TRAVEL_MCP_RATE_LIMIT_RPS` | Float | `20.0` | Sustained requests per second permitted per client IP. |
| `TRAVEL_MCP_RATE_LIMIT_BURST` | Integer | `50` | Maximum token burst capacity per client IP. |

### Recommended Production Values

- **Single Developer Workstation:** `rps: 10.0`, `burst: 30`
- **Team / Shared Remote Server:** `rps: 30.0`, `burst: 100`
- **High-Concurrency Automated Test Suite:** set `TRAVEL_MCP_RATE_LIMIT_ENABLED=false`

---

## 3. Throttled Response Format

When a client exceeds the allowable rate, the server returns:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 1
X-Request-ID: req-ab912cd34ef5

{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please throttle your requests.",
  "status_code": 429
}
```

Clients should observe the `Retry-After` header and apply exponential backoff.
