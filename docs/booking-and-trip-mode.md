# Controlled Booking and In-Trip Mode

`booking-handoff` prepares a provider checkout without making a purchase. Quotes require an item-specific HTTPS URL, exact decimal total, currency, timestamp, source IDs, expiry, and cancellation summary. Confirmation must repeat the exact booking ID, amount, currency, and literal `CONFIRM`. Even after confirmation, checkout and payment remain a user action on the provider's website.

The pack never stores payment data or traveler identity documents.

`trip-mode` returns the current itinerary item, the next item, departure time including travel buffer, local-language address, offline-readiness warnings, and emergency contacts. It reports missing booking references, documents, maps, or emergency information before they become travel-day failures.

Use the existing `offline` export format before departure, then feed its sourced itinerary data to trip mode. Network loss does not change the deterministic next-action calculation.
