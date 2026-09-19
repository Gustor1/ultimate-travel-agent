# Workflow: Find Accommodation

## 1. Purpose
Identifies strategic neighborhoods and curates a vetted shortlist of accommodations matching traveler budget, style, group size, and mobility requirements.
Prioritizes safety, transit connectivity, quietness, and transparent cancellation terms without automated booking.

## 2. Agents Involved
- `accommodation-researcher` (Lead)
- `source-verification`
- `accommodation-research` (Skill)

## 3. Input / Output Contracts
- **Input**: City/region, travel dates, party size, bed/room configuration, budget tier, preferred vibe, accessibility needs.
- **Output**: Neighborhood assessment report and curated shortlist of 3-5 verified lodging properties with direct reservation links.

## 4. Step-by-Step Execution Process
1. **Neighborhood & Transit Gate**: Assess nighttime safety, noise, activity access, then verify nearby stops. Rank metro, tram, commuter rail, bus, and other modes in that order, using walking thresholds and step-free requirements from the traveler profile.
2. **Candidate Lodging Screening**: Filter properties matching group size, air conditioning, elevator access, and budget constraints.
3. **Multi-Site Price Discovery**: Compare identical stay parameters on Google Hotels, Booking.com, and at least one of Agoda or Trip.com; log unavailable or skipped providers.
4. **Cross-Check Reviews & Amenities**: Corroborate guest feedback across multiple sources, filtering out sponsored or fake reviews. Check soundproofing and cleanliness ratings.
5. **Official Verification**: Recheck identical rooms, dates, taxes, mandatory fees, breakfast, availability, and payment terms on the property website.
6. **Cancellation & Final-Price Audit**: Normalize total stay cost and refundable deadlines. Prefer direct when equal or cheaper; otherwise expose the exact third-party difference and policy tradeoff.

## 5. Deliverables
- Neighborhood Guide & Recommendation
- Shortlist of 3-5 Vetted Lodgings
- Amenity & Policy Comparison Table
- Transit Access Table with named stops, modes, lines, walking time, and accessibility
- Provider Coverage Report and Final-Price Breakdown
- Direct Official Reservation Links
