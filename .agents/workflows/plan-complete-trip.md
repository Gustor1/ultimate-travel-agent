# Workflow: Plan Complete Trip

## 1. Purpose
Executes the comprehensive, end-to-end multi-agent travel planning workflow for any traveler profile and destination.
Coordinates 12 specialized agents through dependency gates, ensuring sourced claims, financial safety reserves, and a `TravelDossier v1` result without automatic purchasing.

## 2. Agents Involved
- **Lead Orchestrator**: `travel-orchestrator`
- **Wave 1A (Parallel Research)**: `destination-researcher`, `transport-planner`, `activity-curator`, `travel-preparation-agent`
- **Wave 1B (After Date Gate)**: `accommodation-researcher`, `local-discovery-agent`, date-sensitive `activity-curator` refinement
- **Wave 2 (Financial Consolidation)**: `budget-analyst`
- **Wave 3 (Scheduling & Optimization)**: `itinerary-optimizer`
- **Wave 4 (Quality & Safety Gate)**: `quality-controller`, `source-verification`, `mcp-skill-auditor` (optional)
- **Wave 5 (Synthesis)**: `travel-orchestrator`

## 3. Input / Output Contracts
- **Input**:
  - Filled trip brief (see `examples/trip-brief-template.md`) with destinations, dates, budget, party composition, pacing, and preferences.
  - Runtime tool status (filesystem, web search, browser capabilities).
- **Output**:
  - Complete master travel dossier (executive summary, day-by-day itinerary table, multi-modal transport plan, accommodation shortlist, activity catalog with rain contingencies, itemized budget with 10-15% safety reserve, pre-departure administrative checklist).
  - Claim ledger linked to typed, dated, expiring source evidence.
  - Pre-booking verification checklist for the user.

## 4. Step-by-Step Execution Process

### Step 1: Brief Ingestion & Gap Detection (`travel-orchestrator`)
- Parse the user's travel brief.
- Detect missing constraints (e.g. airport of origin, mobility needs, dietary requirements).
- If critical details are missing, establish reasonable documented assumptions or request clarification.

### Step 2: Wave 1A — Parallel Exploratory Research
Dispatch independent tasks concurrently:
1. `destination-researcher`: Regional climate, seasonal crowd indicators, cultural customs.
2. `transport-planner`: Inter-city and long-distance transport comparison door-to-door.
3. `accommodation-researcher` depends on `flight-search` and `transport-planner` dates before checking live lodging availability.
   - **Flight search** (using `flight-search` skill): Generate and execute the full bounded 4-pass matrix (base → fixed-date gateways → full flexible-date grid → full dates × gateways matrix). The result proposes effective date candidates and must have zero pending search cells **before** accommodation research begins.
   - **Ground transport** (using `transport-research` skill): Rail, bus, ferry, and car rental options.
3. `activity-curator`: Broad cultural and recreational candidates not dependent on final dates.
4. `travel-preparation-agent`: Visa prerequisites, entry rules, passport validity, emergency templates.

### Step 2B: Date Gate and Wave 1B
- Select candidate effective travel dates from the transport result; do not describe them as booked or confirmed.
- Then run `accommodation-researcher`, `local-discovery-agent`, and date-sensitive activity refinement in parallel.
- If no viable date set exists, return `status: blocked` instead of continuing with fictional availability.

### Step 3: Source Verification & Cross-Checking (`source-verification`)
- Cross-reference operating hours, admission fees, and transit routes against Tier 1 (official) and Tier 2 (direct operators) sources.
- Convert factual outputs into claim IDs linked to exact source IDs.
- Assign `retrieved_at` and `expires_at`; flag stale, unconfirmed, or contradictory claims.

### Step 4: Wave 2 — Budget Consolidation (`budget-analyst`)
- Aggregate estimated costs across all categories.
- Convert foreign currencies using dated reference-rate claims.
- Add mandatory 10-15% safety contingency reserve.
- Verify total against the traveler's stated budget cap.

### Step 5: Wave 3 — Itinerary Construction (`itinerary-optimizer`)
- Assemble researched activities, transfers, meals, and rest into chronological day-by-day plans.
- Apply geographic clustering to eliminate backtracking.
- Insert realistic transit buffers between stops.
- Integrate bad-weather contingency plans for outdoor blocks.

### Step 6: Wave 4 — Quality Assurance Gate (`quality-controller`)
- Audit daily schedules for connection feasibility and pacing realism.
- Verify that every price or operating claim cites an appropriate source tier.
- Reject plans with impossible transfers, missing rest buffers, or unvetted commercial claims.
- Keep `mode: inspiration` unless every critical claim passes the booking-readiness gate.

### Step 7: Wave 5 — Master Dossier Compilation (`travel-orchestrator`)
- Synthesize validated findings into `TravelDossier v1`.
- Include explicit pre-booking action items with official booking links.
- Present clear warnings that live availability and pricing require self-booking confirmation by the user.

## 5. Deliverables
1. Executive Travel Summary
2. Day-by-Day Chronological Itinerary
3. Door-to-Door Transport Plan
4. Vetted Accommodation Shortlist
5. Curated Activities Catalog & Rain Contingency Plan
6. Itemized Budget & Currency Breakdown
7. Pre-Departure Checklist & Administrative Requirements
8. Pre-Booking Verification Action List (with official links)
