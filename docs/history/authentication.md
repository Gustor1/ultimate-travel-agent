# Remote MCP Authentication Guide

This document details the authentication schemes supported by the Ultimate Travel MCP Server, how to configure them, and how client applications authenticate.

---

## 1. Supported Authentication Methods

The server implements a modular authentication pipeline defined in `src/ultimate_travel_agent/mcp/auth.py`:

1. **Static API Key / Development Token (Recommended for single-user / private deployments)**:
   - Configured via server environment variable `TRAVEL_MCP_API_KEY`.
   - Verified in constant time using `secrets.compare_digest` to eliminate timing attacks.
   - Accepts either `Authorization: Bearer <API_KEY>` or `X-API-Key: <API_KEY>` HTTP headers.

2. **Extensible OAuth 2.1 / OIDC Hook (Future Enterprise Ready)**:
   - Designed around the abstract `TokenValidator` interface.
   - Allows drop-in validation for RS256/ES256 signed JSON Web Tokens (JWT) issued by identity providers (Auth0, Keycloak, Google Workspace, Okta).

---

## 2. Server Configuration

To activate authentication on your deployed server:

```bash
# Set your server API key
export TRAVEL_MCP_API_KEY="YOUR_MCP_API_KEY"

# Optional: explicitly enforce authentication requirement
export TRAVEL_MCP_AUTH_REQUIRED="true"
```

When `TRAVEL_MCP_API_KEY` is defined, all requests to `/mcp` without valid credentials will receive:

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
WWW-Authenticate: Bearer realm="ultimate-travel-mcp"

{
  "error": "Unauthorized",
  "message": "Missing credentials. Provide 'Authorization: Bearer <token>' or 'X-API-Key' header.",
  "status_code": 401
}
```

### Unauthenticated Endpoint Exemptions
The following endpoints are **exempt** from authentication to allow load balancers and orchestrators (Cloud Run, Railway, Render, Kubernetes) to monitor server health without leaking credentials:
- `GET /health`
- `GET /ready`
- `GET /version`

---

## 3. Client Connection Examples

### A. Antigravity Configuration (`mcp_config.json`)

```json
{
  "mcpServers": {
    "ultimate-travel-agent-remote": {
      "url": "https://YOUR-TRAVEL-MCP-DOMAIN/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

### B. Claude Code Configuration (`settings.json` or CLI)

```json
{
  "mcpServers": {
    "ultimate-travel-agent": {
      "transport": "http",
      "url": "https://YOUR-TRAVEL-MCP-DOMAIN/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

### C. Cursor Configuration (`cursor-mcp.json`)

```json
{
  "mcpServers": {
    "travel-agent": {
      "url": "https://YOUR-TRAVEL-MCP-DOMAIN/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

### D. Curl Verification

```bash
curl -X POST https://YOUR-TRAVEL-MCP-DOMAIN/mcp \
  -H "Authorization: Bearer YOUR_MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "curl", "version": "1.0"}}}'
```
