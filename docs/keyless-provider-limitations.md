# Limitations & Safe Usage of Keyless Open Providers — `ultimate-travel-agent`

**Phase:** Phase 10 — Keyless Public Data Integrations  
**Status Date:** 2026-09-13  
**Audience:** Travelers, Developers, MCP Integrators  

---

## 1. Executive Summary

Keyless open data providers unlock remarkable value for trip planning without requiring API keys, accounts, or payments. However, open data services are **informational reference feeds**, not commercial reservation systems. Users and client agents must clearly understand what these providers **can** and **cannot** deliver.

---

## 2. Inherent Limitations by Provider

### 2.1 Open-Meteo (Weather)
- **7-Day Horizon**: Weather forecasts are highly reliable for days 1–3, moderately indicative for days 4–7, and subject to significant divergence beyond day 7.
- **Microclimate Variations**: Mountain valleys, coastal micro-climates, and sudden localized squalls may deviate from grid-based numerical weather models.
- **Indoor Plan B Requirement**: A forecast indicating low rain probability does not guarantee dry weather. Outdoor excursions must always maintain indoor alternatives.

### 2.2 European Central Bank (Currency)
- **Reference Rates Only**: ECB rates are wholesale financial benchmark rates established on TARGET working days at ~16:00 CET.
- **Retail Surcharge**: Commercial travelers cannot exchange cash or make credit card payments at ECB reference rates. Retail credit cards, foreign ATM withdrawals, and airport currency exchanges impose margins typically ranging between **+1.5% and +3.5%** (and up to 8% at airport counters).
- **Weekend/Holiday Freezes**: ECB rates are frozen over weekends and official bank holidays; Friday rates apply until Monday afternoon.
- **Unsupported Minor Currencies**: Currencies not tracked by the ECB (e.g., Icelandic Króna ISK during certain historical reporting periods, localized pegged currencies) fall back to static reference tables.

### 2.3 Wikivoyage (Guides & Context)
- **Community-Maintained Content**: Articles are written and edited by volunteers. Opening hours, entry ticket prices, and local transport line numbers may be outdated.
- **Visa & Entry Rules**: Wikivoyage guidelines on visas, passports, and health requirements are non-authoritative editorial summaries. They **must never replace** official embassy, consular, or IATA Timatic databases.
- **Subjectivity**: Cultural tips, culinary favorites, and safety warnings represent crowd consensus rather than certified administrative advice.

### 2.4 Nominatim OpenStreetMap (Geocoding)
- **Disabled by Default**: Due to the OSM Foundation Acceptable Use Policy (strict 1 req/s maximum), live Nominatim is disabled by default in multi-user MCP environments.
- **No Autocomplete / Bulk Batching**: Nominatim is unsuitable for live keystroke autocompletion or high-speed batch enrichment.
- **Address Ambiguity**: Searching for ambiguous names without country context (e.g., "Springfield" or "Saint-Martin") may return unexpected locations.

### 2.5 Project OSRM (Road Routing)
- **Demo Server Status**: The public endpoint `router.project-osrm.org` is a demonstration server with no uptime guarantees, no service level agreement (SLA), and zero support for commercial volumes.
- **No Real-Time Traffic**: Drive times are calculated using baseline road speed categories from OpenStreetMap tags. Real-time traffic jams, holiday rush hours, road construction, and weather closures are **not included**.
- **No Toll Calculation**: OSRM does not compute toll costs, vignette requirements, or environmental low-emission zone fines.

---

## 3. What Phase 10 Keyless Providers DO NOT Provide

| Travel Planning Need | Keyless Live Available? | Solution in Ultimate Travel Agent |
| :--- | :--- | :--- |
| **Real-time flight seat inventory** | ❌ No | Deterministic offline estimation + Direct official airline links |
| **Real-time hotel room availability** | ❌ No | Deterministic offline estimation + Official direct hotel portal links |
| **Direct booking / payment** | ❌ **Strictly Prohibited** | User must complete reservation directly on official platforms |
| **Official Visa certification** | ❌ No | Preparation checklists with explicit consular verification advisory |
| **Turn-by-turn vehicle GPS** | ❌ No | High-level driving distance & time estimation only |
| **Live monument ticket gates** | ❌ No | Pre-departure booking requirement flags with official links |

---

## 4. Fallback Matrix on Failure

If any keyless service encounters a network dropout, DNS failure, 5xx server error, or rate-limit throttle (429):

```text
Outbound HTTP Request
         │
    [ Failure ]
         │
         ├── Stale cache entry available (< 24-48h)?
         │         └── Serve STALE cache with advisory notice
         │
         └── No stale cache?
                   └── Graceful fallback to deterministic offline mock
                       (Result tagged VerificationLevel.UNVERIFIED or CROSS_CHECKED)
```

This ensures that the travel planning engine never crashes or blocks the user from generating a complete itinerary.
