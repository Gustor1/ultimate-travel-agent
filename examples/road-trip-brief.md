# Example Brief: Scottish Highlands & Isle of Skye Road Trip

## 1. Filled-in Travel Brief
- **Destination(s)**: Scottish Highlands & Isle of Skye, Scotland (UK)
- **Dates or Duration**: June 8 - June 16 (8 nights / 9 days)
- **Origin**: Edinburgh Airport (EDI)
- **Travelers**: 2 adults (friends/adventurers)
- **Budget & Currency**: £2,200 GBP total (excluding flights)
- **Accommodation Preference**: Cozy Bed & Breakfasts, historic inns, and independent guest cottages
- **Pace Preference**: `balanced` (driving capped at 3.5 hours per day; scenic stops and short hikes)
- **Crowd Preference**: `low-crowd` (early morning walks, remote peninsulas like Trotternish and Applecross)
- **Transport Preference**: Compact automatic rental car (easier navigation on single-track Highland roads)
- **Dietary or Accessibility Needs**: No restrictions; keen on local seafood (Cullen skink, langoustines) and distillery tours
- **Must-Do Activities**: Glencoe scenic pass, Old Man of Storr hike at sunrise, Talisker distillery tour, Eilean Donan photo
- **Things to Avoid**: Rushing through Glenfinnan viaduct crowds, excessive single-day driving distances
- **Other Constraints**: Both drivers have valid international driving licenses; need left-hand side driving confidence

## 2. Agents Mobilized
- `travel-orchestrator`: Coordinates driving loop (Edinburgh -> Stirling -> Glencoe -> Skye -> Inverness -> Cairngorms -> Edinburgh)
- `destination-researcher`: Highland June weather (12-18°C, long 17h daylight, midge prevention strategies)
- `transport-planner`: Rental car insurance coverage, single-track passing place etiquette, fuel stops
- `accommodation-researcher`: Pre-booked Portree/Broadford B&Bs and Glencoe historic inn
- `activity-curator`: Morning hikes at Quiraing and Storr, Skye seafood stops, Highland folk museum
- `local-discovery-agent`: Stein Inn (oldest pub on Skye), Applecross walled garden cafe
- `budget-analyst`: Rental car, petrol, accommodation, dining, and admission breakdown (£1,880 + £320 buffer)
- `travel-preparation-agent`: UK ETA / visa rules, international driving permit check, waterproof hiking gear checklist
- `itinerary-optimizer`: Circular driving loop preventing backtracking; scenic rest breaks every 90 minutes
- `quality-controller`: Audits daily drive times against real single-track road conditions and ferry timetables

## 3. Expected Sources
- VisitScotland (National Tourism Organisation) (Tier 1)
- Traffic Scotland (Road conditions & roadworks) (Tier 1)
- Met Office UK (Mountain weather forecasts) (Tier 1)
- Historic Environment Scotland (Tier 1)
- Caledonian MacBrayne (CalMac) Ferries (Tier 2)

## 4. Structured Fictional Result
```yaml
trip_summary:
  destination: "Scottish Highlands & Isle of Skye"
  duration: "9 days / 8 nights"
  party: "2 adults"
  budget_cap: "£2,200 GBP"
  total_estimated_cost: "£2,110 GBP (including 15% safety reserve)"
itinerary_highlights:
  day_1: "Edinburgh to Glencoe via Stirling Castle (2h45m drive). Overnight in Glencoe historic inn."
  day_2: "Glencoe morning photography, Glen Etive, drive to Mallaig, ferry to Armadale (Skye). Overnight in Broadford."
  day_3: "Isle of Skye: Fairy Pools morning walk, Talisker Bay, Neist Point sunset. Overnight in Portree."
  day_4: "Trotternish Ridge: Old Man of Storr (07:30 sunrise hike), Kilt Rock, Quiraing loop. Overnight in Portree."
  day_6: "Skye to Inverness via Eilean Donan Castle and Loch Ness scenic drive. Overnight in Inverness."
  day_8: "Cairngorms National Park: Rothiemurchus pine forest walk, return rental at Edinburgh Airport."
```

## 5. Information Requiring Verification Before Booking
1. **CalMac Mallaig-Armadale Ferry**: Vehicle space on the ferry must be reserved weeks in advance; alternatively, use Skye Bridge for zero-fee crossing.
2. **Skye Lodging Availability**: Isle of Skye accommodation books out months ahead for June; secure refundable rooms early.
3. **Single-Track Road Ettiquette**: Review UK Highway Code on passing places and yielding to climbing vehicles.
4. **Midges Defense**: June can see Highland biting midges; prepare Smidge repellent and head nets for windless evenings.
