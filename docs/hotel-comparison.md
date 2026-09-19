# Transit-aware hotel comparison

Hotel research now follows four passes:

1. neighborhood and public-transport validation;
2. like-for-like discovery on Google Hotels, Booking.com, and Agoda or Trip.com;
3. matching-room verification on the official property website;
4. final-price and cancellation comparison.

## Transit priority

Nearby stops are ranked `metro → tram → commuter rail → bus → ferry/shuttle/other`. The default walking limit is 12 minutes and can be changed per traveler. Every stop records its name, lines, walking time, step-free status, source, and verification date.

A bus can remain a useful fallback, but it does not silently replace the metro/tram check. A property is not described as well connected when no verified stop fits the walking or accessibility limit.

## Comparable final price

Quotes are compared only when dates, occupancy, room count, room key, currency, breakfast requirement, and cancellation requirement match. The final total includes:

```text
nightly rate × nights × rooms
+ taxes + city tax + resort fee + cleaning fee
+ service fee + breakfast cost + other mandatory fees
```

Google Hotels is discovery-only. Booking.com, Agoda, and Trip.com require property-specific URLs. The official property channel is preferred when its comparable total is equal or cheaper.

## Commands

```bash
ultimate-travel-agent hotel-search-plan request.yaml hotel-plan.json
ultimate-travel-agent hotel-search-coverage hotel-plan.json --booking-ready
ultimate-travel-agent hotel-compare comparison.yaml
```

These commands generate and validate research. Live rates and availability still require browser/API access; the system never books or enters payment details.
