# Workflow: Compare Transport Options

## 1. Purpose
Researches, compares, and evaluates all viable multi-modal transit options between journey origin and destination points, or between intermediate cities.
Compares door-to-door transit time, financial cost, transfer complexity, luggage convenience, and environmental footprint.

## 2. Agents Involved
- `transport-planner` (Lead)
- `source-verification`
- `transport-research` (Skill)

## 3. Input / Output Contracts
- **Input**: Origin and destination locations, departure/return dates, passenger count, luggage volume, travel pace/comfort preferences.
- **Output**: Multi-modal transit comparison matrix with door-to-door estimates, official booking links, and booking window guidelines.

## 4. Step-by-Step Execution Process
1. **Identify Transport Modes**: Identify available air, rail, bus, ferry, driving, and shared transit corridors between origin and destination.
2. **Door-to-Door Calculation**: Add local transfer times, airport/station check-in buffers, security processing, and luggage retrieval to pure transit times.
3. **Cost & Booking Window Analysis**: Check baseline fare tiers, baggage fee policies, and advance purchase windows for best rates.
4. **Environmental & Comfort Scoring**: Compare carbon emissions and seating/work comfort (e.g. high-speed rail vs short-haul air).
5. **Operator Verification**: Provide direct links to official carriers (e.g. SNCF, Eurostar, Deutsche Bahn, national airlines) without intermediary markups.

## 5. Deliverables
- Multi-Modal Comparison Matrix
- Door-to-Door Journey Breakdown
- Official Booking Channel Directory
- Advance Booking Timeline
