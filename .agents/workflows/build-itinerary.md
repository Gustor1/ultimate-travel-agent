# Workflow: Build & Optimize Daily Itinerary

## 1. Purpose
Synthesizes researched destinations, transit segments, lodgings, and activities into a coherent, hour-by-hour, day-by-day travel itinerary.
Enforces geographic clustering to eliminate backtracking, balances daily walking loads, and provides flexible meal and rest buffers.

## 2. Agents Involved
- `itinerary-optimizer` (Lead)
- `activity-curator`
- `transport-planner`
- `itinerary-builder` (Skill)

## 3. Input / Output Contracts
- **Input**: Approved activities, lodging location, inter-city arrival/departure times, pace preference (`packed`, `balanced`, `relaxed`).
- **Output**: Chronological daily itinerary table with morning/afternoon/evening segments, transfer times, meal windows, and buffer zones.

## 4. Step-by-Step Execution Process
1. **Geographic Clustering**: Group selected activities into geographic zones (e.g. East District on Day 1, North District on Day 2) to minimize transit.
2. **Pacing & Energy Balancing**: Alternate high-energy walking tours with seated experiences, relaxed lunches, or leisure breaks.
3. **Temporal Sequencing**: Align activities with confirmed opening hours, optimal light for photography, and pre-booked timed entry slots.
4. **Buffer Insertion**: Add 20-30 minute cushions between activities to absorb minor delays and spontaneous exploration.
5. **Contingency Integration**: Embed pre-determined rain alternatives directly into the daily schedule.

## 5. Deliverables
- Day-by-Day Chronological Schedule
- Daily Transit & Walking Map Breakdown
- Daily Meal & Rest Recommendations
- Contingency Swap Guide
