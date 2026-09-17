# Phase 10: Keyless Public Data Integrations — Feasibility & Governance Audit

**Version:** 1.0.0  
**Status:** Approved & Enforced  
**Date:** 2026-09-13  
**Target:** Local Engine, Provider Hub V1.2, and Remote MCP Server

---

## Executive Summary

Phase 10 introduces live public data integrations for `ultimate-travel-agent` that require:
- **Zero API key**
- **Zero developer account**
- **Zero credit card / payment method**
- **Zero commercial partnership or contractual review**

These integrations inject authentic real-world data into travel itineraries while respecting strict open data licenses, acceptable use policies (AUP), rate limits, attribution mandates, and traveler privacy.

Commercial providers (Amadeus, Google Flights, Booking.com, Trip.com, TripAdvisor Terra, Viator, GetYourGuide, Google Maps) remain strictly deactivated in this phase as they require keys, commercial contracts, or billing setups.

---

## Provider Feasibility Matrix

| Provider | Category | Official Endpoint | Auth / Key | Rate Limit | Local Cache TTL | Attribution | License | MCP Public Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo** | Weather & Geocoding | `https://api.open-meteo.com/v1/forecast`<br>`https://geocoding-api.open-meteo.com/v1/search` | None | Up to 10,000 daily calls, ~5 req/s burst | 30 min (forecast)<br>7 days (geocoding) | "Weather data by Open-Meteo.com under CC BY 4.0" | CC BY 4.0 | **Approved** (Live by default if live keyless enabled) |
| **European Central Bank (ECB)** | Currency Exchange | `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml` | None | Daily publish; ~2 req/s safe | 12–24 hours | "Source: European Central Bank (ECB) euro reference exchange rates" | Open ECB Data | **Approved** (Live by default if live keyless enabled) |
| **Wikivoyage (MediaWiki)** | Editorial Guides | `https://en.wikivoyage.org/w/api.php` | None | ~3 req/s safe; custom User-Agent mandatory | 24 hours | "Text from Wikivoyage under CC BY-SA 4.0" | CC BY-SA 4.0 | **Approved** (Live by default if live keyless enabled) |
| **Nominatim (OSM)** | Geocoding | `https://nominatim.openstreetmap.org/search` | None | **Strict Max 1 req/sec**; single-thread worker | 7 days | "Data © OpenStreetMap contributors, ODbL 1.0" | ODbL 1.0 | **Limited** (Disabled by default; max 1 req/s mutex lock) |
| **OSRM (Demo)** | Road Routing | `https://router.project-osrm.org/route/v1` | None | Demo server; no SLA; low volume only | 2 hours | "Routing © Project OSRM / OpenStreetMap contributors" | BSD 2-Clause / ODbL | **Experimental** (Disabled by default; self-hosting recommended) |
| **Amadeus / Booking / Google / Viator / GYG** | Flights / Rail / Hotels / Tours | Various commercial APIs | API Key / Account / Contract | Varies | Varies | Commercial | Proprietary | **Rejected for Phase 10** (Deferred to Phase 11+) |

---

## Detailed Provider Analysis & Governance

### 1. Open-Meteo (Weather & Geocoding)
- **Official Endpoint:**
  - Forecast: `https://api.open-meteo.com/v1/forecast`
  - Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- **Data Available:** Current temperature, humidity, precipitation, weather code, wind speed; 7-day daily high/low temperatures, precipitation probability, daily weather codes; destination latitude, longitude, country, and timezone.
- **Key Required:** None for non-commercial open data usage.
- **Terms & Limits:** Free access under 10,000 daily requests. Local rate limiting set to max 5 requests per second.
- **Attribution Requirement:** Explicit attribution to `Open-Meteo.com` and CC BY 4.0.
- **Safety Rule:** Weather forecasts beyond 7–14 days must never be presented as guaranteed; marked as seasonal estimates.
- **Decision:** **Approved**. High uptime, low latency, clean JSON REST API.

### 2. European Central Bank (ECB Daily Reference Rates)
- **Official Endpoint:** `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml`
- **Data Available:** Euro reference exchange rates against 30+ major global currencies (USD, JPY, GBP, CHF, CAD, AUD, ISK, SEK, NOK, etc.), published every TARGET working day around 16:00 CET.
- **Key Required:** None.
- **Terms & Limits:** Public XML feed mirrored globally on Akamai CDN. Local cache TTL set to 12 hours.
- **Attribution Requirement:** "Source: European Central Bank (ECB) euro reference exchange rates".
- **Financial Safety Rule:** All converted amounts must explicitly state that ECB rates are official reference rates and not retail consumer credit card or foreign exchange counter rates (which typically include a 1.5%–3.5% banking markup).
- **Decision:** **Approved**. Deterministic, highly reliable, zero developer account required.

### 3. Wikivoyage / Wikimedia API
- **Official Endpoint:** `https://en.wikivoyage.org/w/api.php`
- **Data Available:** Destination search, encyclopedic introductions, sections on culture ("Understand"), sights ("See"), activities ("Do"), local cuisine ("Eat"), and safety alerts ("Stay safe").
- **Key Required:** None.
- **Usage Policy:** Strictly complies with Wikimedia User-Agent Policy. Requires a descriptive User-Agent with project repository URL. No bulk downloading, respect maxlag and cache responses.
- **Attribution Requirement:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
- **Reliability Rule:** Marked as `community_recommended`. Must never be used as the sole source for legal visa entry requirements, real-time ticket prices, or urgent diplomatic travel advisories.
- **Decision:** **Approved**. Provides rich contextual travel knowledge with zero commercial tracking.

### 4. Nominatim OpenStreetMap (Limited Geocoding)
- **Official Endpoint:** `https://nominatim.openstreetmap.org/search`
- **Data Available:** Reverse and forward geocoding, coordinates, bounding boxes, administrative boundaries.
- **Usage Policy:** Strict OpenStreetMap Foundation Acceptable Use Policy:
  - Absolute maximum of **1 request per second**.
  - Single-threaded request worker (never send concurrent requests).
  - Valid, unique, non-generic User-Agent.
  - Mandatory client-side caching.
  - Strict prohibition against search-as-you-type or bulk address parsing.
- **Attribution Requirement:** "© OpenStreetMap contributors, ODbL 1.0 (https://osm.org/copyright)".
- **Public MCP Server Risk:** In a shared or multi-user remote MCP server, concurrent user calls could easily violate the 1 req/s threshold and trigger IP blacklisting.
- **Decision:** **Limited (Disabled by Default)**. Protected by an in-memory Mutex rate limiter (1.0s minimum gap). Disabled by default (`TRAVEL_MCP_ENABLE_NOMINATIM=false`). Production deployments should point to a self-hosted Nominatim or a dedicated tile server.

### 5. Project OSRM Demo Server (Experimental Routing)
- **Official Endpoint:** `https://router.project-osrm.org/route/v1/driving/`
- **Data Available:** Road transit distance (meters), transit duration (seconds), simplified route geometry.
- **Usage Policy:** The public OSRM server is explicitly a **demo server with no SLA**. It must not be relied upon for production workloads.
- **Attribution Requirement:** "Routing data © Project OSRM / OpenStreetMap contributors".
- **Decision:** **Experimental (Disabled by Default)**. Kept disabled by default (`TRAVEL_MCP_ENABLE_OSRM=false`). Full mock and offline fallbacks are always active. Documentation clearly outlines how to connect a self-hosted OSRM container or professional routing provider.

---

## Technical Architecture & Safety Controls

All keyless live providers inherit common safety controls implemented in `src/ultimate_travel_agent/integrations/http_client.py`:
1. **HTTPS Only:** Rejects unencrypted plain HTTP calls (local test URLs excepted).
2. **Short Timeouts:** Default timeout of 5.0 seconds (configurable via `TRAVEL_HTTP_TIMEOUT`).
3. **Structured Rate Limiting:** Thread-safe TokenBucket / LeakyBucket enforcing per-domain throughput caps.
4. **TTL Cache with Hit/Miss/Stale States:** Serves cached data on repeat queries; returns gracefully tagged stale data on network disruptions.
5. **Zero Secrets / Zero PII:** No personal traveler identifiers, passports, or payment details are ever sent to remote public endpoints.
6. **Graceful Degradation:** Automatic fallback to local mock/offline providers on 429, 5xx, or network unavailability.

---

## Conclusion & Next Steps

Open-Meteo, ECB, and Wikivoyage provide a solid, ethical, keyless live foundation for weather, exchange rates, and destination guides. Nominatim and OSRM are safely encapsulated under limited/experimental toggles. Phase 11 will address commercial providers requiring developer keys (Amadeus, OpenRouteService) under authenticated enterprise modes.
