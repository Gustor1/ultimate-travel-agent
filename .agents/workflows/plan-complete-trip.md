# Workflow: Plan Complete Trip

## 1. Purpose
Executes the comprehensive, end-to-end multi-agent travel planning workflow for any traveler profile and destination.
Coordinates 11 specialized sub-agents across 5 sequential execution waves, ensuring thorough research, strict source validation, financial safety reserves, and a fully sourced final travel dossier without automatic purchasing.

## 2. Agents Involved
- **Lead Orchestrator**: `travel-orchestrator`
- **Wave 1 (Parallel Research)**: `destination-researcher`, `transport-planner`, `accommodation-researcher`, `activity-curator`, `local-discovery-agent`, `travel-preparation-agent`
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
  - Source provenance log (Tiers 1-6).
  - Pre-booking verification checklist for the user.

## 4. Step-by-Step Execution Process

### Step 1: Brief Ingestion & Gap Detection (`travel-orchestrator`)
- Parse the user's travel brief.
- Detect missing constraints (e.g. airport of origin, mobility needs, dietary requirements).
- If critical details are missing, establish reasonable documented assumptions or request clarification.

### Step 2: Wave 1 — Parallel Exploratory Research
Dispatch tasks concurrently to specialized research agents:
1. `destination-researcher`: Regional climate, seasonal crowd indicators, cultural customs.
2. `transport-planner`: Inter-city and long-distance transport comparison door-to-door.
   - **Flight search** (using `flight-search` skill): Execute the 4-pass progressive flight scan (base → multi-airport → flexible dates → combined). The flight search fixes effective travel dates and must complete **before** accommodation research begins.
   - **Ground transport** (using `transport-research` skill): Rail, bus, ferry, and car rental options.
3. `accommodation-researcher`: Neighborhood scouting and 3-5 vetted lodging candidates. **Depends on flight-search output** for confirmed arrival/departure dates.
4. `activity-curator`: Cultural, recreational, and dining experiences with rain backups.
5. `local-discovery-agent`: Community gems and authentic culinary spots (marked discovery-only).
6. `travel-preparation-agent`: Visa prerequisites, entry rules, passport validity, emergency templates.

### Step 3: Source Verification & Cross-Checking (`source-verification`)
- Cross-reference operating hours, admission fees, and transit routes against Tier 1 (official) and Tier 2 (direct operators) sources.
- Flag any unconfirmed or volatile figures.

### Step 4: Wave 2 — Budget Consolidation (`budget-analyst`)
- Aggregate estimated costs across all categories.
- Convert foreign currencies using reliable reference rates.
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

### Step 7: Wave 5 — Master Dossier Compilation (`travel-orchestrator`)
- Synthesize validated findings into the final travel dossier.
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
