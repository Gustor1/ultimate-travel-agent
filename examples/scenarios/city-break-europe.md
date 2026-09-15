# Scenario: City Break Europe (Barcelona, 4 Days)

## 1. User Brief
- **Destination**: Barcelona, Spain (Catalonia)
- **Duration**: 4 days / 3 nights (Thursday to Sunday in mid-May)
- **Origin**: Lyon, France (Direct TGV rail)
- **Travelers**: 2 adults (couple)
- **Budget & Currency**: €1,400 EUR total (excluding TGV train tickets)
- **Pace Preference**: `balanced` (2 main architectural highlights per day + neighborhood tapas walks)
- **Crowd Preference**: `mixed` (must see Sagrada Familia, but desire quiet evening neighborhoods like Gràcia and Poblenou)
- **Interests**: Modernisme architecture (Gaudí, Domènech i Montaner), Mediterranean seafood, coastal walks
- **Things to Avoid**: Late-night tourist crowds on Las Ramblas; overpriced paella traps near Barceloneta
- **Dietary**: No restrictions; enjoy local cava and tapas

## 2. Skills Mobilized
- `travel-orchestrator`: Sequences the 5-wave planning cycle
- `travel-web-research`: Investigates May weather (18-24°C), daylight (14h30m), public holidays
- `transport-research`: Compares Renfe-SNCF TGV direct from Lyon Part-Dieu to Barcelona Sants vs flying
- `accommodation-research`: Vets quiet boutique hotels in Eixample Dret and Gràcia
- `activity-curator`: Curates Sagrada Familia, Casa Batlló, Sant Pau Art Nouveau Site, and Park Güell
- `local-discovery`: Identifies authentic vermuterías in Gràcia and bodegas in Sant Antoni
- `budget-and-booking-checker`: Allocates expenses and sets booking alarms for Sagrada Familia
- `travel-safety`: Evaluates pickpocket risk hotspots (Metro L3, Gothic Quarter) and safety advice
- `itinerary-optimizer`: Clusters Eixample/Gràcia on Day 2 and Gothic/Born/Poblenou on Day 3
- `quality-controller`: Audits transit buffers and opening days (e.g. Park Güell slot timing)

## 3. Sub-Agents to Launch
- Wave 1: `destination-researcher`, `transport-planner`, `accommodation-researcher`, `activity-curator`, `local-discovery-agent`, `travel-preparation-agent`
- Wave 2: `budget-analyst`
- Wave 3: `itinerary-optimizer`
- Wave 4: `quality-controller`, `source-verification`
- Wave 5: `travel-orchestrator`

## 4. Expected Sources to Consult
- Turisme de Barcelona (Official Tourism Bureau) — Tier 1 (`https://www.barcelonaturisme.com`)
- Basílica de la Sagrada Família (Official Box Office) — Tier 1 (`https://sagradafamilia.org`)
- Renfe / SNCF Connect (Rail operators) — Tier 2
- TMB Transports Metropolitans de Barcelona — Tier 1 (`https://www.tmb.cat`)
- Guía Repsol Gastronomía España — Tier 4

## 5. Data Requiring Verification Before Booking
1. **Sagrada Familia Tower Access**: Tower elevators close during high winds; check weather policy.
2. **Park Güell Monumental Zone**: Strict timed entry every 30 minutes; tickets sell out days in advance.
3. **Barcelona City Tourist Tax**: Mandatory surcharges apply per person per night in licensed hotels.
4. **TGV Luggage Dimension Limits**: High-speed trains allow 3 items per passenger up to 25 kg.

## 6. Identified Risks & Mitigations
- **Pickpocketing**: High risk around major sights; carry cross-body bags with zipper clips.
- **Mid-day Heat**: May can have warm sunny days; schedule outdoor parks in early morning.
- **Dining Hours**: Traditional kitchens open at 13:30 for lunch and 20:30 for dinner; adapt schedule.

## 7. Expected Deliverable Format
Full sourced markdown dossier with day-by-day itinerary table, transport schedule, accommodation options, itemized budget (€1,210 estimated + €190 reserve = €1,400), and pre-booking verification links.
