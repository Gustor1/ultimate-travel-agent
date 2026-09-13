---
name: travel-planning
description: Best practices and structured protocols for assembling end-to-end travel itineraries across city-trips, road-trips, and nature expeditions.
---

# Travel Planning Skill

## Overview
This skill guides the creation of realistic, well-paced, and comprehensive travel plans without relying on automated booking.

## Core Rules

1. **Door-to-Door Realism**:
   - Always factor in check-in, security checks, and transfer buffers:
     - High-speed trains: 30-45 minutes buffer before departure.
     - Domestic/European flights: 90-120 minutes buffer.
     - International long-haul flights: 180 minutes buffer.
   - Include last-mile transit between train stations/airports and accommodations.

2. **Pacing and Geographic Clustering**:
   - Group visits within the same district or walking corridor.
   - Cap major sights at 2 to 3 per day for balanced trips, 1 per day for relaxed trips.
   - Maintain dedicated lunchtime (at least 60-75 minutes) and evening wind-down intervals.

3. **Weather & Rainy-Day Contingency**:
   - Every outdoor attraction (parcs, hikes, architectural walks) must have an identified indoor alternative (`indoor_contingency` or `indoor_backup`).

4. **Crowd Avoidance ("Moins de personne")**:
   - Target opening hours (08:30 - 09:30) or late afternoon slots (after 16:30) for high-density landmarks.
   - Favor quiet residential and pedestrianized neighborhoods for accommodations.

5. **Provider Hub Integration & Zero-Booking Protocol**:
   - Query flights and trains for multi-option door-to-door comparisons without triggering any reservation requests.
   - Separate lodging reviews (`StayAPIReviewProvider` / `TripadvisorReviewProvider`) from live room inventory and pricing.
   - Ground budget calculations in published exchange rates (`ECBCurrencyProvider`) and always distinguish estimated from confirmed live prices.
   - Zero automated booking: All tickets, lodging, and excursions must be confirmed directly by the traveler on the provider's official portal.
