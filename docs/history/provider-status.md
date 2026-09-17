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
| `osrm` | Map | ⚠️ Experimental | Live (Disabled) | No | Project OSRM Demo |
| `nominatim` | Map | ⚠️ Limited | Live (Disabled) | No (User-Agent req) | OpenStreetMap AUP |
| `mock_weather` | Weather | ✅ Ready | Offline / Mock | No | No |
| `open_meteo` | Weather | 🟢 Live Ready | Live (Keyless) | No | Open-Meteo (CC BY 4.0)|
| `openweathermap`| Weather | 🟡 Prepared | Live (Disabled) | Yes (`OPENWEATHERMAP_API_KEY`)| Free Tier |
| `mock_currency` | Currency | ✅ Ready | Offline / Mock | No | No |
| `ecb_currency` | Currency | 🟢 Live Ready | Live (Keyless) | No | ECB Euro Reference |
| `mock_guide` | Guide | ✅ Ready | Offline / Mock | No | No |
| `wikivoyage` | Guide | 🟢 Live Ready | Live (Keyless) | No | Wikimedia MediaWiki |
| `social_discovery`| Social | ✅ Ready | Offline / Mock | No | Output tagged strictly |

---

## 2. Phase 10 Keyless Live Provider Toggles

Keyless live providers can be toggled via environment variables:
- `TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=false` (Master toggle for all keyless live feeds)
- `TRAVEL_MCP_ENABLE_OPEN_METEO=true` (Weather & Geocoding: approved)
- `TRAVEL_MCP_ENABLE_ECB=true` (Daily Reference Exchange Rates: approved)
- `TRAVEL_MCP_ENABLE_WIKIVOYAGE=true` (Editorial Guides & Context: approved)
- `TRAVEL_MCP_ENABLE_NOMINATIM=false` (Limited to 1 req/s; disabled by default for public MCP)
- `TRAVEL_MCP_ENABLE_OSRM=false` (Experimental demo server; disabled by default for public MCP)

---

## 3. Health & Inspection

Providers can be inspected at runtime via:
- MCP Tool: `get_keyless_provider_status()`
- MCP Tool: `get_provider_status(provider_name="open_meteo")`
- MCP Tool: `list_integration_providers(category="weather")`
- HTTP Endpoint: `GET /ready` returns aggregate configured count.

