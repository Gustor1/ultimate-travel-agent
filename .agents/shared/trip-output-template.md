# User-facing trip plan template

Use this structure for the final answer in `quick` and `standard` modes, and as the reading order of the expanded `TravelDossier v1` in `exhaustive` mode. Write in the user's language. Omit a section only when it does not apply, and say so in one line.

1. **En bref** — route and nights per base, total budget range, readiness label (`idées`, `plan à vérifier`, `prêt à réserver`), and the depth mode used.
2. **Points bloquants** — entry documents and electronic authorizations, last-service or tight connections, and any unresolved conflict. Empty is a valid result; say "aucun".
3. **À réserver, et quand** — a dated list grouped as *maintenant*, *J-30*, *J-7*, *J-1*: timed-entry tickets, shows, restaurants, rail or air fares likely to rise, and free slots that open on a release date. Each line gives the item, why it is time-sensitive, and the direct booking page.
4. **Choix à faire** — two to four decisions the user should take (for example rail versus air, one area versus another, an optional half-day excursion), each with the trade-off and a recommendation.
5. **Jour par jour** — one block per day grouped by area: morning, afternoon, evening, meal ideas near the route, travel time between blocks, and a rain or closure alternative for fragile items. Show slack instead of filling every hour.
6. **Logement** — recommended area and why, then the retained properties with total price for the stay, cancellation deadline, and transit to the day anchors.
7. **Transport** — arrival and departure, local transport and fare-capping or pass logic, airport or station transfers.
8. **Budget** — table with one line per category, each value marked `vérifié le <date>` (confirmed on the primary source), `relevé le <date>` (observed on a comparison engine, connector, or search snippet but not yet confirmed on the primary page), `estimation`, or `non coté`, plus the reserve. Convert currencies with a dated rate and show the original currency.
9. **Avant de partir** — revalidation tasks with dates, documents, connectivity, and offline maps.
10. **Sources** — the primary source and retrieval date for every critical claim. Never present a local file path as a web link.
    - **Contradictions entre sources** — for each material disagreement found (fee, opening days, walk-in policy…), list both values with their sources and dates, which one the plan follows and why, and the check that would settle it. Omit the list only when none were found, and say so.

## Rules

- Never turn an estimate into a fact: price, hours, and availability carry their status inline.
- Put a map link for every address-bearing item when the host can produce one, so the plan stays usable offline once saved.
- Keep it scannable: short lines, tables for comparisons, no repeated research prose.
