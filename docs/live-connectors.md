# Secure Live Connectors

Version 1.9 provides a provider-neutral HTTPS/JSON connector that can call flight, hotel, transit, activity, or weather APIs without storing credentials in project files.

```console
ultimate-travel-agent connector-fetch connector-request.yaml
```

The payload contains a `config` and a `request`. Authentication can use a bearer token, custom header, query parameter, or no credential. Credentials are read from the named environment variable and are removed from the returned source URL.

Security controls are mandatory: HTTPS only, fixed destination host, allowed path prefix, 60-second maximum timeout, bounded response size, JSON-only response, no inline authorization/cookie headers, and rejection of cross-host redirects. Provider-specific OAuth token acquisition remains external; the connector accepts the resulting short-lived token through an environment variable.

Live calls remain subject to each provider's account, terms, rate limits, schema, and availability. Results record provider, domain, source URL, retrieval timestamp, status code, and raw JSON payload. An optional declarative `normalization` block maps provider-specific dotted paths to stable string, integer, boolean, or exact-decimal fields; invalid required records are rejected with visible issues.
