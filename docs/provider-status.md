# Provider Status & Integration Inventory

**System:** `ultimate-travel-agent`  
**Current Hub Release:** V1.2+ Remote MCP Architecture  
**Status Date:** 2026-09-13  

---

## 1. Provider Readiness Matrix

| Provider Name | Category | Current Status | Default Mode | Key Required? | Commercial Agreement? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `mock_flight` | Flight | ✅ Ready | Offline / Mock | No | No |
| `amadeus_flight` | Flight | 🟡 Prepared | Live (Disabled) | Yes (`AMADEUS_*`) | Free Sandbox |
| `aviation_edge` | Flight | 🟡 Prepared | Live (Disabled) | Yes (`AVIATION_EDGE_API_KEY`) | Paid |
| `mock_train` | Train | ✅ Ready | Offline / Mock | No | No |
| `sncf_train` | Train | 🟡 Prepared | Live (Disabled) | Yes (`SNCF_API_KEY`) | Free Open Data |
| `navitia_train` | Train | 🟡 Prepared | Live (Disabled) | Yes (`NAVITIA_API_KEY`) | Free Tier |
| `mock_accommodation`| Hotel | ✅ Ready | Offline / Mock | No | No |
| `amadeus_hotel` | Hotel | 🟡 Prepared | Live (Disabled) | Yes (`AMADEUS_*`) | Free Sandbox |
| `booking` | Hotel | 🔴 Partner Req | Live (Disabled) | Yes | Affiliate / Commercial |
| `mock_review` | Review | ✅ Ready | Offline / Mock | No | No |
| `stayapi_review` | Review | 🟡 Prepared | Live (Disabled) | Yes (`STAYAPI_KEY`) | Commercial |
| `tripadvisor_review`| Review | 🔴 Partner Req | Live (Disabled) | Yes (`TRIPADVISOR_API_KEY`) | Commercial Partner |
| `mock_activity` | Activity | ✅ Ready | Offline / Mock | No | No |
| `viator_activity` | Activity | 🔴 Partner Req | Live (Disabled) | Yes (`VIATOR_API_KEY`) | Commercial Partner |
| `getyourguide_activity`| Activity | 🔴 Partner Req | Live (Disabled) | Yes | Partner Program |
| `opentripmap_activity`| Activity | 🟡 Prepared | Live (Disabled) | Yes (`OPENTRIPMAP_API_KEY`)| Free Tier |
| `mock_maps` | Map | ✅ Ready | Offline / Mock | No | No |
| `openrouteservice`| Map | 🟡 Prepared | Live (Disabled) | Yes (`OPENROUTESERVICE_API_KEY`)| Free Tier |
| `google_maps` | Map | 🟡 Prepared | Live (Disabled) | Yes (`GOOGLE_MAPS_API_KEY`)| Free Tier Credit |
| `osrm` | Map | ✅ Ready | Live (Keyless) | No | Self-Host / Public |
| `nominatim` | Map | ✅ Ready | Live (Keyless) | No (User-Agent req) | OpenStreetMap |
| `mock_weather` | Weather | ✅ Ready | Offline / Mock | No | No |
| `open_meteo` | Weather | ✅ Ready | Live (Keyless) | No | Open Data |
| `openweathermap`| Weather | 🟡 Prepared | Live (Disabled) | Yes (`OPENWEATHERMAP_API_KEY`)| Free Tier |
| `mock_currency` | Currency | ✅ Ready | Offline / Mock | No | No |
| `ecb_currency` | Currency | ✅ Ready | Live (Keyless) | No | Public ECB XML |
| `mock_guide` | Guide | ✅ Ready | Offline / Mock | No | No |
| `wikivoyage` | Guide | ✅ Ready | Live (Keyless) | No | Public MediaWiki |
| `social_discovery`| Social | ✅ Ready | Offline / Mock | No | Output tagged strictly |

---

## 2. Health & Inspection

Providers can be inspected at runtime via:
- MCP Tool: `get_provider_status(provider_name="amadeus_flight")`
- MCP Tool: `list_integration_providers(category="weather")`
- HTTP Endpoint: `GET /ready` returns aggregate configured count.
