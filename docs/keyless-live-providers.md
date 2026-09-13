# Keyless Live Providers — `ultimate-travel-agent`

**Phase:** Phase 10 — Keyless Public Data Integrations  
**Status Date:** 2026-09-13  
**Architecture Policy:** Zero Developer Account, Zero API Key, Zero Credit Card, Zero Commercial Agreement  

---

## 1. Overview & Architectural Principles

Phase 10 introduces direct, live integrations with high-value public open data feeds. These sources require **no API keys, no user registration, no developer accounts, and no paid subscriptions**, making them universally accessible for local and remote MCP usage without licensing friction.

### Core Safeguards
1. **HTTPS-Only Transport**: Enforced at the transport layer (`KeylessHttpClient`). Any non-HTTPS URL is rejected immediately with `ProviderNetworkError`.
2. **Strict User-Agent Identification**: In compliance with Wikimedia, OpenStreetMap, and Open-Meteo fair-use policies, all outbound HTTP requests carry a compliant `User-Agent`:
   ```text
   ultimate-travel-agent/1.3.0 (https://github.com/Gustor1/ultimate-travel-agent; contact: open-source@ultimate-travel-agent.local)
   ```
3. **Thread-Safe In-Memory Rate Limiting**: Token/delay rate limiters enforce minimum gaps between HTTP calls on a per-domain basis, preventing 429 throttling and honoring upstream service limits.
4. **Three-Tier In-Memory TTL Cache**: Responses are cached with `cache_status`: `hit`, `miss`, or `stale`. In case of network errors (timeout, DNS, 5xx), the client serves stale cached data with `result_status="stale"` rather than failing.
5. **No Booking / Zero PII**: Absolutely no personal identifiable information is sent to external services; search queries contain only coarse geographic locations and public dates.

---

## 2. Keyless Provider Inventory

| Provider | Data Domain | Upstream Endpoint | Upstream License | Default Verification Level | Rate Limit Gap | Cache TTL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo** | 7-day weather forecasts & geocoding | `https://api.open-meteo.com/v1/forecast`, `https://geocoding-api.open-meteo.com/v1/search` | CC BY 4.0 | `cross_checked` | 200 ms (5 req/s max) | 1,800 s (30 min) |
| **European Central Bank (ECB)** | Daily reference foreign exchange rates | `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml` | Official ECB Open Data | `official_verified` | 500 ms (2 req/s max) | 14,400 s (4 hours) |
| **Wikivoyage** | Travel guides, highlights & local tips | `https://en.wikivoyage.org/w/api.php` | CC BY-SA 4.0 | `community_recommended` | 330 ms (3 req/s max) | 86,400 s (24 hours) |
| **Nominatim (OSM)** | Geocoding & address lookup | `https://nominatim.openstreetmap.org/search` | ODbL 1.0 / CC BY-SA 2.0 | `cross_checked` | 1,000 ms (1 req/s strict mutex) | 86,400 s (24 hours) |
| **Project OSRM** | Road routing, distances & driving duration | `https://router.project-osrm.org/route/v1/driving/` | ODbL / BSD 2-Clause | `cross_checked` | 1,000 ms (1 req/s max) | 86,400 s (24 hours) |

---

## 3. Provider Capabilities & Details

### 3.1 Open-Meteo (`OpenMeteoProvider`)
- **Geocoding**: Resolves city or destination queries to `(latitude, longitude)` coordinates.
- **Current Conditions & 7-Day Forecast**: Temperature (Celsius), precipitation sum (mm), precipitation probability (%), maximum wind speed (km/h), and WMO weather codes.
- **Activity Guidance**: Computes `rain_risk` (flagged if probability >= 40% or precipitation >= 2.0 mm), suggesting indoor Plan B alternatives (museums, covered markets, indoor galleries) and outdoor hazard warnings for high winds (>= 50 km/h).
- **Attribution**: Mandated CC BY 4.0 notice pointing to [open-meteo.com](https://open-meteo.com/).

### 3.2 European Central Bank (`ECBCurrencyProvider`)
- **Daily Reference Rates**: Parses daily XML feed published at ~16:00 CET on TARGET working days.
- **Cross-Currency Conversions**: Supports 30+ major world currencies (USD, JPY, GBP, CHF, CAD, AUD, NOK, SEK, etc.) relative to EUR or cross-rates between non-EUR currencies via EUR pivot.
- **Retail Surcharge Advisory**: Every conversion includes the mandatory consumer disclaimer:
  > *Retail credit card & ATM transactions typically incur a 1.5% to 3.5% foreign transaction fee above ECB reference rates.*
- **Fallback**: Static baseline rates embedded in code ensure uninterrupted conversions if the ECB feed is temporarily unreachable.

### 3.3 Wikivoyage (`WikivoyageProvider`)
- **MediaWiki OpenSearch & Content API**: Queries English Wikivoyage for destination overviews, neighborhood summaries, and cultural guidelines.
- **Verification Tier**: Automatically tagged as `VerificationLevel.COMMUNITY_RECOMMENDED`. Sub-agents are explicitly instructed to cross-check visa rules and operational prices with official consular or ticketing sources.
- **Attribution**: CC BY-SA 4.0 with direct article link.

### 3.4 Nominatim OpenStreetMap (`NominatimProvider`)
- **Status**: **Limited / Disabled by default** (`TRAVEL_MCP_ENABLE_NOMINATIM=false`).
- **Policy Compliance**: Strictly abides by the [OpenStreetMap Foundation Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/).
- **Concurrency Mutex**: Protected by `_NOMINATIM_WORKER_LOCK` to ensure no concurrent worker can trigger more than 1 request per second across the entire process.
- **Attribution**: Mandatory ODbL notice: *© OpenStreetMap contributors*.

### 3.5 Project OSRM (`OSRMProvider`)
- **Status**: **Experimental / Disabled by default** (`TRAVEL_MCP_ENABLE_OSRM=false`).
- **Use Case**: Car routing distance (km) and estimated drive time (minutes) between known coordinates or major cities.
- **Safety Checks**: Automatically flags itineraries exceeding 4 hours of continuous driving with driver fatigue rest alerts (recommending a 20-minute pause every 2 hours).
- **Advisory**: Clearly marked as demo routing without production SLA; suitable for high-level travel planning, not turn-by-turn vehicle navigation.

---

## 4. MCP Tools & Web Endpoints

### MCP Tools
- `geocode_destination(destination, mode="offline")`
- `get_weather_forecast(destination, days=7, mode="offline")`
- `get_weather_activity_advice(destination, target_date=None, mode="offline")`
- `get_exchange_rates(base_currency="EUR", symbols=None, mode="offline")`
- `convert_currency_live(amount, from_currency="EUR", to_currency="USD", mode="offline")`
- `search_wikivoyage_destination(query, mode="offline")`
- `get_wikivoyage_summary(destination, mode="offline")`
- `get_limited_route_options(origin, destination, mode="offline")`
- `get_keyless_provider_status()`

### Web UI REST Endpoints
- `GET /api/integrations/keyless/status`
- `GET /api/integrations/weather?city={city}&days={days}`
- `GET /api/integrations/currency/convert?amount={amount}&from_curr={curr}&to_curr={curr}`
- `GET /api/integrations/guides/destination?destination={city}`

---

## 5. Commercial Services Exclusion

The following commercial travel platforms remain **strictly disabled** or simulated via deterministic mock providers in Phase 10:
- **Flights**: Google Flights, Amadeus (Commercial Live API).
- **Lodging**: Booking.com, Trip.com / StayAPI, Airbnb.
- **Tours & Activities**: Viator, GetYourGuide, TripAdvisor Terra.
- **Maps**: Google Maps Platform, Mapbox (paid credit tiers).

These services will be addressed in subsequent dedicated phases with secure credential isolation, OAuth / developer partner agreements, and strict PII safeguards.
