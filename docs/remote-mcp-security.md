# Remote MCP Security Architecture

**System:** `ultimate-travel-agent` Remote Streamable HTTP MCP Server  
**Spec Compliance:** Model Context Protocol (Streamable HTTP / SSE 2024-11-05)  
**Security Posture:** Zero-Trust, Defense-in-Depth, Zero Financial Transactions  

---

## 1. Threat Model & Defense Principles

Exposing an MCP server over the public internet introduces distinct security challenges compared to local `stdio` processes:

| Threat Vector | Description | Countermeasure in `ultimate-travel-agent` |
| :--- | :--- | :--- |
| **API Quota Exhaustion** | Unauthorized actors flooding expensive third-party endpoints. | In-memory token-bucket rate limiting (default 20 rps / 50 burst) + API key authentication. |
| **Data Leakage & Secrets Exposure** | Leaking backend API keys (`AMADEUS_*`, `SNCF_*`, etc.) to client payloads or logs. | Strict architectural isolation: client only receives sanitized results; secrets scrubbed from logs via regex; `/health` probes return zero configuration secrets. |
| **Accidental or Malicious Bookings** | An autonomous agent initiating real ticket purchases or charges. | Architectural impossibility: zero booking, cart, checkout, or payment methods exist in the entire codebase. Only official portal URLs are returned. |
| **DNS Rebinding Attacks** | Browser-based agents tricked into querying local internal services. | Built-in DNS rebinding validation via `TransportSecuritySettings` (`allowed_hosts`, `allowed_origins`). |
| **Denial of Service (Oversized Payloads)** | Memory exhaustion via multi-megabyte JSON payloads. | Enforced 1MB request body limit returning `413 Payload Too Large`. |
| **Prompt Injection Vectors** | Adversarial text hidden in reviews or social discovery posts. | Social discovery outputs tagged `social_discovery_only`; anti-injection review screening per `mcp-skill-auditing` skill. |

---

## 2. Layered Defense Architecture

```text
Incoming HTTP Request
       │
       ▼
[1. DNS & Host Validation] ─── (Matches allowed_hosts / allowed_origins)
       │
       ▼
[2. Request Size Guard] ───── (Rejects bodies > 1MB with 413)
       │
       ▼
[3. Rate Limiter] ─────────── (Token-bucket per IP; rejects with 429)
       │
       ▼
[4. Authentication Guard] ─── (Validates Bearer token / X-API-Key; rejects with 401)
       │                       (Exempts /health, /ready, /version)
       ▼
[5. Request ID & Logging] ─── (Injects X-Request-ID; sanitizes logs)
       │
       ▼
[6. MCP Streamable Transport] ─ (Executes read-only travel tools)
       │
       ▼
Client Receives Sanitized Response
```

---

## 3. Server Configuration Reference

All security parameters are configurable strictly via environment variables:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `TRAVEL_MCP_API_KEY` | String | `None` | Shared secret for Bearer / X-API-Key token authentication. |
| `TRAVEL_MCP_AUTH_REQUIRED` | Boolean | `false` (auto-true if API key set) | Enforce authentication on `/mcp`. |
| `TRAVEL_MCP_RATE_LIMIT_ENABLED` | Boolean | `true` | Enables per-IP rate limiting. |
| `TRAVEL_MCP_RATE_LIMIT_RPS` | Float | `20.0` | Sustained requests per second allowed per IP. |
| `TRAVEL_MCP_RATE_LIMIT_BURST` | Integer | `50` | Maximum burst tokens per IP. |
| `TRAVEL_MCP_MAX_REQUEST_SIZE` | Integer | `1048576` (1MB) | Maximum allowed payload size in bytes. |
| `TRAVEL_MCP_ALLOWED_ORIGINS` | Comma list | `*` | Allowed CORS origins. |
| `TRAVEL_MCP_ALLOWED_HOSTS` | Comma list | `*` | Allowed Host header values for DNS protection. |
| `TRAVEL_MCP_DNS_PROTECTION` | Boolean | `false` | Enable strict host-header verification. |

---

## 4. Logging & Sanitization

The server logs all requests with their method, path, HTTP status, execution latency in milliseconds, and `X-Request-ID`.

All log lines pass through a sanitization regex filter:
- Bearer tokens (`Authorization: Bearer <token>`) are replaced with `[REDACTED]`.
- Sensitive query parameters (`key=...`, `token=...`, `secret=...`, `password=...`) are masked.
- Provider secrets are never logged under any circumstance.
