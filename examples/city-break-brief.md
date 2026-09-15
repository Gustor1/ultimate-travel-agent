# Example Brief: Tokyo & Kyoto Autumn City Break

## 1. Filled-in Travel Brief
- **Destination(s)**: Tokyo (3 nights) & Kyoto (3 nights), Japan
- **Dates or Duration**: October 18 - October 24 (6 nights / 7 days)
- **Origin**: Paris (CDG)
- **Travelers**: 2 adults (couple)
- **Budget & Currency**: €3,200 EUR total (excluding international flights)
- **Accommodation Preference**: Boutique hotels in quiet, walkable districts (e.g. Yanaka/Asakusa in Tokyo, Gion/Karasuma in Kyoto)
- **Pace Preference**: `balanced` (2 curated highlights per day + neighborhood dining)
- **Crowd Preference**: `mixed` (iconic temples visited at dawn; hidden gardens in the afternoon)
- **Transport Preference**: Public transit within cities; Shinkansen high-speed rail between Tokyo and Kyoto
- **Dietary or Accessibility Needs**: One pescatarian traveler; enjoy authentic ramen, sushi, and tea ceremonies
- **Must-Do Activities**: Shinkansen view of Mount Fuji, Fushimi Inari early morning hike, teamLab digital art
- **Things to Avoid**: Overcrowded tour buses, mid-day Takeshita Street rush
- **Other Constraints**: Arriving at Haneda Airport (HND); departing from Kansai Airport (KIX)

## 2. Agents Mobilized
- `travel-orchestrator`: Master coordinator sequencing 5 waves
- `destination-researcher`: Autumn climate (15-22°C), early foliage timing, daylight hours
- `transport-planner`: Tokyo Metro 72h pass, Tokaido Shinkansen (Nozomi/Hikari), Haruka Express to KIX
- `accommodation-researcher`: Asakusa boutique lodging (Tokyo) & traditional machiya hotel in Kyoto
- `activity-curator`: Timed teamLab Planets slot, dawn Fushimi Inari, Tenryu-ji bamboo grove anti-crowd plan
- `local-discovery-agent`: Yanaka retro coffee shops, Pontocho alley hidden obanzai eateries
- `budget-analyst`: Consolidated expenses (€2,650 estimated + €350 safety reserve = €3,000)
- `travel-preparation-agent`: Visit Japan Web digital customs registration, Pasmo/Suica IC card setup
- `itinerary-optimizer`: Day-by-day geographic clustering (East Tokyo Day 1, West Tokyo Day 2, Shinkansen Day 4)
- `quality-controller`: Verifies train connection buffers, museum reservation windows, pacing feasibility

## 3. Expected Sources
- Japan National Tourism Organization (JNTO) (Tier 1)
- JR Central / SmartEX Shinkansen Portal (Tier 2)
- Tokyo Metro & Bureau of Transportation (Tier 1)
- Kyoto City Official Travel Guide (Tier 1)
- Tokyo Metropolitan Government (Tier 1)

## 4. Structured Fictional Result
```yaml
trip_summary:
  destination: "Tokyo & Kyoto, Japan"
  duration: "7 days / 6 nights"
  party: "2 adults"
  budget_cap: "€3,200 EUR"
  total_estimated_cost: "€2,950 EUR (including 12% safety reserve)"
itinerary_highlights:
  day_1_tokyo_east:
    base: "Asakusa"
    morning: "Arrival at HND, Keikyu train to Asakusa, check-in, rest."
    afternoon: "Senso-ji Temple grounds and quiet streets of Yanaka."
    evening: "Casual soba dinner near Sumida River."
  day_2_tokyo_modern:
    morning: "teamLab Planets (pre-booked 09:30 slot to bypass queues)."
    afternoon: "Ginza architectural walk and depachika food hall exploration."
    evening: "Ramen dining in Yurakucho under-tracks."
  day_4_shinkansen_to_kyoto:
    morning: "Tokaido Shinkansen Hikari (booked mountain-side window seats for Mt Fuji view, 2h15m)."
    afternoon: "Check-in at Kyoto Karasuma, walk along Kamogawa River."
    evening: "Traditional Obanzai dinner in Pontocho alley."
  day_5_kyoto_heritage:
    morning: "Fushimi Inari Taisha (07:00 dawn walk to Upper Shrine, avoiding mid-day crowds)."
    afternoon: "Tofuku-ji garden & Sanjusangendo 1001 Kannon statues."
    evening: "Gion evening lantern walk."
```

## 5. Information Requiring Verification Before Booking
1. **Shinkansen Baggage Reservation**: Re-verify JR baggage rules if carrying suitcases exceeding 160 cm linear dimensions.
2. **teamLab Ticket Release**: Tickets release precisely on the first day of the preceding month; must be booked online immediately.
3. **Autumn Foliage Peak**: Peak koyo colors in Kyoto vary each year between mid-November and early December; late October offers early tints.
4. **Digital Customs (Visit Japan Web)**: Fill out QR codes 48h before flight departure.
