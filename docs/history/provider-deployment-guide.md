# Provider Deployment & Configuration Guide

This guide explains how to configure travel data providers when deploying the Ultimate Travel MCP Server.

---

## 1. Operating Rules

1. **Offline / Mock by Default**: Out of the box, all 10 categories operate with zero external API calls, zero credit cards, and zero API keys.
2. **Fail-Closed Live Mode**: When `mode="live"` is requested, an unconfigured provider will immediately return a `ProviderConfigurationError` indicating exactly which environment variables are missing.
3. **Secrets Remain Server-Side**: Neither API keys nor tokens are ever transmitted to MCP clients or exposed in health endpoints.
4. **Zero Automated Transactions**: Direct bookings, seat reserves, cart additions, or payments are architecturally impossible.

---

## 2. Activating Live Providers via Server Environment

You can selectively configure providers using environment variables on your cloud host (Railway, Render, Fly.io, Cloud Run):

### Category Selection
```bash
# Set which provider is active for each category
TRAVEL_PROVIDER_FLIGHTS=amadeus
TRAVEL_PROVIDER_TRAINS=sncf
TRAVEL_PROVIDER_HOTELS=amadeus_hotels
TRAVEL_PROVIDER_REVIEWS=stayapi
TRAVEL_PROVIDER_ACTIVITIES=viator
TRAVEL_PROVIDER_MAPS=openrouteservice
TRAVEL_PROVIDER_WEATHER=open_meteo
TRAVEL_PROVIDER_CURRENCY=ecb
TRAVEL_PROVIDER_GUIDES=wikivoyage
```

### Credentials Reference

| Provider | Category | Required Environment Variables | Pricing / Tier |
| :--- | :--- | :--- | :--- |
| **Amadeus Flight** | Flights | `AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET` | Free sandbox (2,000 queries/month) |
| **Aviation Edge** | Flights | `AVIATION_EDGE_API_KEY` | Paid API subscription |
| **SNCF Connect** | Trains | `SNCF_API_KEY` | Free developer account (data.sncf.com) |
| **Navitia Rail** | Trains | `NAVITIA_API_KEY` | Free developer tier |
| **Amadeus Hotels** | Accommodations | `AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET` | Shared with Amadeus Flights |
| **StayAPI** | Reviews | `STAYAPI_KEY` | Commercial review aggregator |
| **TripAdvisor** | Reviews | `TRIPADVISOR_API_KEY` | Partner content API |
| **Viator** | Activities | `VIATOR_API_KEY` | Partner distribution API |
| **OpenTripMap** | Activities | `OPENTRIPMAP_API_KEY` | Free community tier |
| **OpenRouteService**| Maps | `OPENROUTESERVICE_API_KEY` | Free open-source tier (2,000 req/day) |
| **Google Maps** | Maps | `GOOGLE_MAPS_API_KEY` | Pay-as-you-go ($200/mo free credit) |
| **Open-Meteo** | Weather | `ENABLE_LIVE_KEYLESS_APIS=true` | Free, zero key required |
| **ECB Currency** | Currency | *None required* | Public European Central Bank daily XML |
| **Wikivoyage** | Guides | *None required* | Public MediaWiki open API |

---

## 3. Declarative Configuration via YAML

Alternatively, you can supply `config/providers.yaml` (copy from `config/providers.example.yaml`) or point `TRAVEL_PROVIDERS_CONFIG=/path/to/custom-providers.yaml`.

Example:
```yaml
default_mode: "offline"
providers:
  weather:
    active_provider: "open_meteo"
  maps:
    active_provider: "openrouteservice"
  flights:
    active_provider: "amadeus"
```
