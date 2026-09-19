# Advanced planning toolkit

Version 1.5 adds deterministic helpers around the declarative skills. They do not browse, book, pay, or run background jobs.

## Capabilities

1. **Traveler profile** — reusable, privacy-minimal preferences; no identity, passport, payment, or medical-document storage.
2. **Explainable scoring** — visible weights and criterion-by-criterion results.
3. **Uncertainty** — confidence, freshness, contradiction, critical blocker, and fallback reporting.
4. **Geography** — WGS84 distance, simple route ordering, overlap, walking, transit, and backtracking warnings.
5. **Progressive research** — gates `brief → destination → dates → area → options → booking`.
6. **Time constraints** — offset-aware connections, IANA time zones, and travel-date jet-lag estimates.
7. **Dynamic budget** — low/likely/high ranges, dated exchange rates, category caps, and separate reserves.
8. **Scenario comparison** — economy, balanced, and comfort tradeoffs.
9. **Decision registry** — idempotent accepted/rejected choices with reasons.
10. **Exports** — calendar (`.ics`), map (`.geojson`), text-only PDF, Markdown checklist, responsive mobile HTML, and offline JSON bundle with direct links.
11. **Revalidation** — deterministic due dates for claims, formalities, weather, and disruptions. A host scheduler must execute the checks.
12. **Profile corpus** — regression cases covering solo, couple, family, senior, mobility, dietary, business, budget, and low-crowd travel.

## Commands

```bash
ultimate-travel-agent profile-save profile.yaml profile.json
ultimate-travel-agent profile-show profile.json
ultimate-travel-agent export-dossier dossier.yaml trip.ics --format ics
ultimate-travel-agent export-dossier dossier.yaml trip.pdf --format pdf
ultimate-travel-agent export-dossier dossier.yaml trip.html --format html
ultimate-travel-agent revalidation-plan dossier.yaml --departure 2027-04-15
```

## Price watch assessment

`price-watch` classifies sourced flight or hotel observations as `target_reached`, `price_drop`, `price_rise`, `monitor`, or `stale`. It uses exact decimal prices, requires timezone-aware observations and source IDs, and never predicts future prices.

```console
ultimate-travel-agent price-watch price-history.yaml
```

The input contains one `watch` plus its `observations`. Configure a target price, percentage-change threshold, currency, and maximum observation age. A stale result must be refreshed before any booking decision.

All dossier exports validate `TravelDossier v1` first. Existing v1 files remain valid; the new fields are optional.
