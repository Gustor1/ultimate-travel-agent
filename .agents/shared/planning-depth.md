# Planning depth modes

Choose one mode per run before discovery and record it in the brief. The mode bounds which coverage cells are *required*; it never relaxes evidence honesty. Cells outside the mode are `skipped` with reason `DEPTH_MODE`, never silently dropped.

| Mode | Use when | Run state | Search breadth |
|---|---|---|---|
| `quick` | Inspiration, "is this a good idea?", rough shape of a trip | None; answer in the conversation | Destination context, rough route, labeled estimates only |
| `standard` (default) | A real trip of up to ~2 weeks, one or two countries | Optional; keep claims and sources inline in the final answer | Bounded discovery plus primary verification of critical claims |
| `exhaustive` | Multi-country, separate tickets, groups, high-stakes or user asks for an audit | Full `.travel-agent/runs/<run_id>/` protocol and `compact-handoff/v2` | Complete matrices from each specialist skill |

Escalate to `exhaustive` automatically for separate-ticket connections, multi-border routes, minors travelling with one parent, high altitude, or medical constraints. Tell the user which mode is active in one line and offer the other modes.

## Standard-mode bounds

- **Flights:** Pass 1 plus flexible dates limited to ±2 days on the principal airports; add gateways only when one is a credible alternative. Verify only retained fares on the airline.
- **Corridor decision:** when rail, coach, or ferry is credible for the origin–destination pair, compare it against air door-to-door in one table before choosing either.
- **Lodging:** 2–3 areas, 3 qualified properties across at least two providers or the direct site.
- **Activities:** one anchor per full day, one rain/closure alternative per fragile anchor, booking release and sell-out risk for each ticketed item.
- **Local food and photo:** one or two per base, near the planned route.
- **Safety and entry:** never reduced. Entry documents, electronic travel authorizations, and identity-document rules for the traveler's nationality are checked on official sources in every mode for international trips.
- **Arithmetic:** use the deterministic commands when installed; otherwise show the formula and inputs so the user can recheck. Convert currencies with a stated, dated rate and keep the original currency beside the converted value.

In `quick` and `standard`, report readiness in plain words (`idées`, `plan à vérifier`, `prêt à réserver`) and keep the four gates internal. `validate-run` applies only when a run directory exists.

## Tool routing

Use the best tool the host actually exposes, in this order, and record which one supplied each critical fact:

1. Connected first-party or MCP connectors that cover the need (for example lodging or attraction search, calendars, maps).
2. Official operator, venue, and government pages read directly.
3. Web search for discovery, then the responsible page for verification.
4. A browser for JavaScript-heavy pages when available.

Comparison engines that cannot be read by the host are `unavailable`, not skipped silently; use another engine or the operator site. Never retry a blocked site in a loop, bypass bot protection, or sign in on the user's behalf.

- **Connector results** (lodging, attractions, fares) are `observed`. Before retaining a lodging rate, open the connector's detail or room tool, or the property page, to confirm whether the total includes taxes and fees, the room type, and the cancellation deadline. Unknown inclusions stay explicit in the plan.
- **Unreadable live prices:** when an operator's fares cannot be read, mark them `non coté` and give the user the direct search page, prefilled with route, dates, and passengers when the site's public URL format allows it, plus a bounded estimate labeled as such.
- **Search snippets** guide where to look; they do not verify (see `evidence-policy.md`).

## Language

Write user-facing output in the user's language (default to the language of their brief). Keep official names, station names, and venue names as published, with a translation when useful.
