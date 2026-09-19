# Workflow: Compare Transport Options

## 1. Purpose
Researches, compares, and evaluates all viable multi-modal transit options between journey origin and destination points, or between intermediate cities.
Compares door-to-door transit time, financial cost, transfer complexity, luggage convenience, and environmental footprint.

## 2. Agents Involved
- `transport-planner` (Lead)
- `source-verification`
- `transport-research` (Skill)
- `flight-search` (Skill)

## 3. Input / Output Contracts
- **Input**: Origin and destination locations, departure/return dates, passenger count, luggage volume, travel pace/comfort preferences, whether dates are strictly fixed.
- **Output**: Multi-modal transit comparison matrix with door-to-door estimates, official booking links, and booking window guidelines. For air travel, includes the 4-pass flight search synthesis table.

## 4. Step-by-Step Execution Process
1. **Flight Search (4-Pass)**: Generate the deterministic search matrix, then execute `flight-search` across base airport, fixed-date alternative gateways, the full flexible-date grid, and the full bounded combined matrix. Skip passes 3-4 if dates are strictly fixed. Do not continue while coverage contains pending cells; unavailable/skipped cells require reasons.
2. **Identify Ground Transport Modes**: Identify available rail, bus, ferry, driving, and shared transit corridors between origin and destination using `transport-research` skill.
3. **Door-to-Door Calculation**: Add local transfer times, airport/station check-in buffers, security processing, and luggage retrieval to pure transit times.
4. **Cost & Booking Window Analysis**: Check baseline fare tiers, baggage fee policies, and advance purchase windows for best rates.
5. **Environmental & Comfort Scoring**: Compare carbon emissions and seating/work comfort (e.g. high-speed rail vs short-haul air).
6. **Operator Verification**: Provide direct links to official carriers (e.g. SNCF, Eurostar, Deutsche Bahn, national airlines) without intermediary markups.

## 5. Deliverables
- Multi-Modal Comparison Matrix (including 4-pass flight synthesis)
- Flight Search Coverage Report (expected/searched/unavailable/skipped/pending by pass)
- Door-to-Door Journey Breakdown
- Official Booking Channel Directory
- Advance Booking Timeline
