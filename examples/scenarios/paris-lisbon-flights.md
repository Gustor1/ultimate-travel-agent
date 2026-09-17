# Scenario: Paris → Lisbon Flight Search (4-Pass, Flexible Dates)

## 1. User Brief
- **Origin**: Paris, France (airports CDG, ORY, BVA)
- **Destination**: Lisbon, Portugal (airport LIS)
- **Departure Date**: October 10, 2026
- **Return Date**: October 17, 2026
- **Travelers**: 2 adults
- **Cabin Class**: Economy
- **Dates Fixed**: `false` (flexible ±3 days)
- **Budget**: No strict cap, but seeking best value
- **Baggage**: 1 carry-on each + 1 checked bag

## 2. Skills Mobilized
- `flight-search`: 4-pass progressive air travel scan
- `transport-research`: Ground transfer comparison for alternative airports
- `source-verification`: Cross-check operator URLs and fares

## 3. Sub-Agents to Launch
- Wave 1: `transport-planner` (executing `flight-search` skill first, then `transport-research`)
- Wave 1 (after flight-search): `accommodation-researcher` (dates confirmed by flight results)

## 4. Expected 4-Pass Behavior
1. **Pass 1 (Base)**: Search CDG/ORY → LIS on exact dates 10-17 Oct. Record TAP, Air France, easyJet, Transavia direct flights with prices.
2. **Pass 2 (Multi-Airport, fixed dates)**: Same dates, also check OPO (Porto) with CP train transfer, FAO (Faro) with Rede Expressos bus transfer. Compute door-to-door costs. Retain only if saving ≥ 20% or ≥ €50.
3. **Pass 3 (Flexible Dates, principal airport)**: Test ±1, ±2, ±3 day shifts on departure AND return independently for LIS. Report price delta vs Pass 1.
4. **Pass 4 (Combined)**: Combine date flexibility with alternative airports from Pass 2.

## 5. Key Verification Points
- [ ] All passes executed in order 1 → 2 → 3 → 4
- [ ] Pass 1 always visible as REF row in synthesis table
- [ ] Every flight option has a direct airline booking link (not OTA/aggregator)
- [ ] Alternative airports include door-to-door cost (flight + transfer)
- [ ] Every price has a verification date
- [ ] Transfer costs cite official operator URLs (CP for trains, Rede Expressos for buses)
- [ ] No OTA links (Expedia, Kiwi, eDreams) appear as primary booking links
- [ ] No personal data in search queries
