# Claim-first research methods

Load for live or document-based travel research.

## Plan before searching

Create one compact row per decision need:

`decision -> atomic claim -> applicability -> preferred authority -> freshness -> coverage cell -> stop condition`

Search facts needed for a decision, not generic destination prose. Build a coverage lattice from the dimensions that matter: topic, date, area, traveler constraint, product, and source role. Predeclare minimum qualified candidates or modes per category; unavailable results count as investigated, not as evidence.

## Discovery and verification

1. Generate neutral query variants in the user's language, English, and the local language when useful. Include local names, transliterations, date, and official-domain terms.
2. Use broad discovery to populate every required cell and retain rejection evidence.
3. Resolve duplicate entities and equivalent offers before ranking.
4. Compare with a Pareto frontier where cost, time, risk, accessibility, robustness, and preference conflict. Do not hide trade-offs inside one unexplained score.
5. Verify retained or critical claims on the responsible primary source. Discovery sources remain labeled as such.
6. Stop only after minimum coverage and evidence gates pass and two independent query variants add no new qualified candidate or independent source. Never use saturation to skip a required cell.

## Contradictions and negative evidence

Split compound statements into atomic claims. When sources conflict, first confirm identical dates, traveler category, product, direction, and jurisdiction; then prefer the responsible and newer primary authority. Preserve both versions and their effective dates. If the conflict remains material, block the claim.

Use short rejection codes plus evidence, including `DUPLICATE_ENTITY`, `WRONG_DATE`, `LOCATION_MISMATCH`, `PRICE_OVER_BUDGET`, `TOTAL_PRICE_UNKNOWN`, `STALE_EVIDENCE`, `ACCESSIBILITY_FAIL`, `UNPROTECTED_TRANSFER`, and `INSUFFICIENT_EVIDENCE`.

## Efficient evidence capture

Normalize facts immediately into records; do not retain raw HTML or repeat search-result snippets in handoffs. Record the exact supported fact, not an entire page summary. Reuse an existing current claim/source ID instead of reopening or paraphrasing it. Research quantity is measured by covered claims, qualified candidates, and independent sources—not page opens or prose length.

Canonicalize URLs conservatively: lowercase the host, remove fragments/default ports and known tracking parameters, but preserve date, product, language, rate, and other semantic query parameters. Keep the original URL. Resolve entity aliases with name, address/location, responsible operator, and stable official identifiers; never merge merely similar names.
