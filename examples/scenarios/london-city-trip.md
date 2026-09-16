# Scenario: London Cultural & Urban Exploration (4 Days)

## 1. User Brief
- **Destination**: London, United Kingdom (Bloomsbury, City, South Bank, West End)
- **Duration**: 4 days / 3 nights (October 15 - October 18)
- **Origin**: Paris Gare du Nord (Eurostar to London St Pancras International) or Heathrow (LHR)
- **Travelers**: 2 adults
- **Budget & Currency**: £1,400 GBP (~€1,640 EUR)
- **Pace Preference**: `balanced` (1 major paid monument, world-class free national museums, walking routes)
- **Interests**: British history, architectural landmarks, free galleries, historic pubs
- **Transport Requirements**: Airport / Eurostar arrival transfers, Underground, buses, clear Contactless vs Oyster advice

## 2. Skills Mobilized
`travel-orchestrator`, `transport-research`, `accommodation-research`, `activity-curator`, `local-discovery`, `budget-and-booking-checker`, `itinerary-builder`, `source-verification`, `travel-quality-control`

## 3. Required Grounding & Sourcing Invariants
- **Airport Connections**: Elizabeth line, Tube Piccadilly, or Heathrow Express with direct operator links.
- **TfL Contactless vs Oyster**: Deep comparison based on card foreign transaction fees, daily caps, and card fees (tfl.gov.uk/fares).
- **Free vs Paid Culture**: Explicitly distinguish free permanent collections (British Museum, National Gallery) from paid temporary exhibits.
- **Official Monument Ticketing**: Tower of London via Historic Royal Palaces (hrp.org.uk) rather than reseller blogs.
- **Hotels**: Direct hotel URLs with verified location and amenities.
