---
name: flight-search
description: Searches for flight options using a structured 4-pass methodology (base, multi-airport, flexible dates, combined) to find optimal door-to-door air travel with verified direct booking links.
conditions: Use when travel planning requires flight-search capabilities or air travel comparison.
---

# flight-search

## 1. Role & Identity
Air travel search specialist executing a systematic 4-pass scan to identify optimal flight options, comparing base fares against alternative airports, flexible dates, and combined permutations, always computing total door-to-door cost including ground transfers, luggage policies, and potential overnight stays.

## 2. Expected Inputs
- **Origin & Destination**: City/airport of departure and arrival.
- **Dates & Trip Type**:
  - `round_trip` (default): Departure date and return date (exact or flexible).
  - `one_way` (aller simple): Departure date only. Passes 3 and 4 test date shifts exclusively on the departure date.
  - `multi_city` (multi-villes): List of ordered route segments. Each segment is evaluated as an independent 4-pass search before chronological consolidation.
- **Flexibility**: Whether dates are strictly fixed (`dates_fixed: true`) or flexible ($\pm 1, \pm 2, \pm 3$ days).
- **Party Composition**: Number of adult/child travelers and cabin class preference.
- **Luggage Policy Requirements**: Cabin bag only (under-seat or trolley) vs checked luggage (number of bags and weight).
- **Budget & Constraints**: Maximum budget (if any), preferred departure airports, traveler nationality (for transit visa prerequisites).

## 3. Expected Outputs
- 4-pass progressive flight search results with clear separation between passes.
- Comprehensive synthesis table ranked by ascending total door-to-door cost, including dedicated `Bagages` column.
- Direct booking links (Tier 1-2) using deep booking URLs with pre-filled parameters or explicit user search instructions.
- Mandatory line-by-line door-to-door cost breakdown (`cost_breakdown`) leaving zero unexplained amounts.
- Pass 1 reference price always visible as baseline `REF`.
- Identification of night transfer constraints and transit accommodation costs when same-day ground connection is impossible.

## 4. Necessary Tools & Capabilities
- filesystem_read
- web_search (optional)
- browser (optional)
- local_calculation

## 5. Fallback Behavior Without Web Search or Browser
State clearly that live research cannot be completed.
Use only user-provided or local information.
List the exact information requiring verification.
Never invent live prices, availability, opening hours, visa rules or booking status.
Mark all prices as "indicatif, à confirmer" with explicit verification dates.

## 6. Sourcing Policy
All references must strictly adhere to the 6-tier sourcing hierarchy:
- **Tier 1**: Official government portals, tourism ministries, embassies, municipal administrations.
- **Tier 2**: Official direct operators (rail networks, airlines, ferry lines, museum box offices).
- **Tier 3**: Recognized tourism institutions (regional tourism boards, national park services, UNESCO).
- **Tier 4**: Recognized editorial sources (Michelin Guide, Lonely Planet, established travel journalists).
- **Tier 5**: Community reviews (TripAdvisor, Google Maps reviews, travel forums) for qualitative feedback only.
- **Tier 6**: Social media (TikTok, Instagram, RedNote, personal blogs) strictly tagged as `social_discovery_only`.

### Flight-Specific Source Rules & Deep Link Mandate
- **Airline direct websites** (e.g., Air France, TAP Air Portugal, easyJet, Ryanair) are **Tier 2** and must always serve as the primary booking link.
- **Meta-search aggregators** (Skyscanner, Google Flights, Kayak) may be cited in `source_log` as **Tier 4** discovery aids only, but must never replace the direct airline booking link.
- **OTAs** (Expedia, eDreams, Kiwi, Opodo, Lastminute) are **Tier 5** and are strictly forbidden as primary booking links.
- **Deep URLs Mandatory (No Root Homepages)**:
  - Every flight link must point to a deep booking or flight selection page (e.g., `https://www.flytap.com/en/booking/flights`, `https://www.easyjet.com/en/buy/flights`, `https://www.ryanair.com/gb/en/trip/flights/select`). Generic root domain homepages (e.g., `ryanair.com`, `easyjet.com/en`, `airfrance.fr`) are strictly forbidden.
  - If an airline's booking engine does not allow pre-filling search parameters directly via URL query strings, provide the deepest available booking portal path and supply the explicit user search instruction:
    `"Action requise sur le site : sélectionner <Origine> → <Destination>, Dates <YYYY-MM-DD> au <YYYY-MM-DD>, <N> passagers, classe <Classe>."`

## 7. Safety Policy
- **Never make purchases.**
- **Never make reservations.**
- **Never enter personal or payment data.**
- **Never share travel documents.**
- **Never bypass login, paywalls, robots rules or site restrictions.**
- **Never present social-media content as verified logistical information.**

## 8. Methodology: 4-Pass Progressive Search

### Pass 1 — Base (Reference Price)
Search the **principal airport** of the destination city on the **exact dates** requested by the user.
- This result establishes the **reference baseline price** against which all subsequent options are benchmarked.
- Record: airline, flight numbers, flight duration, stops, baggage allowance, total price, deep direct URL, verification date.

### Pass 2 — Multi-Airport (Fixed Dates)
Keeping the exact travel dates from Pass 1, investigate alternative arrival gateways:
- Other airports serving the same metropolitan area (e.g., London: LHR, LGW, STN, LTN, SEN).
- Airports of adjacent cities connected by direct high-speed rail or express bus (e.g., Porto or Faro for Lisbon; Girona or Reus for Barcelona; Bologna or Florence for Rome).
- **Combinatorial Bound**: Evaluate a **maximum of 5 alternative airports**.

#### Total Door-to-Door Cost Calculation
For each alternative airport, compute the exact door-to-door cost using the following formula:
```
door_to_door_cost = flight_price + ground_transfer_cost + overnight_stay_cost + transfer_time_penalty
```
Where:
- `flight_price`: Total flight cost for all travelers including mandatory taxes and fees.
- `ground_transfer_cost`: Total cost of round-trip ground transport (rail, express bus, shuttle) connecting the alternative airport to the final destination city center for all travelers (citing Tier 2 operators like CP, SNCF, Renfe, Rede Expressos).
- `overnight_stay_cost`: Cost of a transit overnight stay (standard rate: 60 € to 90 € / room) if flight arrival occurs too late to catch the last onward ground connection on the same day.
- `transfer_time_penalty` (or `transfer_time_value`): Optional economic valuation of extra travel fatigue and lost vacation time. Defined as a flat rate of **15 € per hour of additional ground transit time** compared to the Pass 1 baseline journey, documented explicitly in `assumptions`. If time penalty is not requested by the user, this term is set to 0 €, but the extra travel time must remain clearly visible in hours.

#### Mandatory Arithmetic & Line-by-Line Decomposition
Every door-to-door total MUST display its complete line-by-line itemization (`cost_breakdown`):
- Flight total (e.g. 2 travelers × 75 € = 150 €)
- Ground transfer total (e.g. 2 travelers × 20 € = 40 €)
- Transit overnight accommodation if applicable (e.g. 0 € if same-day transfer confirmed)
- Additional luggage / airport shuttle fees
**Zero unexplained or opaque amounts**: The mathematical sum of the individual line items must equal the declared door-to-door total.

#### Retention Threshold
Retain an alternative airport option **only if** it yields a net saving $\ge 20\%$ OR $\ge 50\,€$ compared to the best Pass 1 reference baseline.

### Pass 3 — Flexible Dates (Principal Airport)
**Skip this pass entirely if the user specified `dates_fixed: true` or non-negotiable dates.**
Using exclusively the principal airport from Pass 1:
- For round-trip journeys: test date shifts of -3, -2, -1, +1, +2, +3 days on departure AND return **independently**.
- For one-way journeys: test shifts of -3, -2, -1, +1, +2, +3 days on the departure date only.
- Document the exact date shift (e.g., "Aller +2j, Retour identique") and price delta vs Pass 1.

### Pass 4 — Combined (Flexible Dates × Multi-Airport)
**Skip this pass entirely if the user specified `dates_fixed: true`.**
Combine date flexibility with alternative airports:
- **Combinatorial Limitation**: To avoid combinatorial explosion, test date shifts limited to **$\pm 2$ days** (rather than $\pm 3$) centered around the **top 3 most promising alternative candidates** identified across Pass 2 and Pass 3.
- The agent prioritizes high-saving combinations (e.g. low-cost midweek fare drops paired with high-speed rail connections).
- Apply the same retention threshold ($\ge 20\%$ or $\ge 50\,€$ saving on total door-to-door cost) and verify night transfer feasibility.

### Night Transfers & Same-Day Connection Rule
When evaluating alternative airports:
- Inquire and verify the scheduled departure time of the last train or bus to the final destination on the arrival evening.
- Allow an incompressible safety buffer of at least **45 minutes** between flight landing and ground transit departure (for deplaning, border control, luggage reclaim, and terminal exit).
- If flight arrival is too late for same-day connection, an overnight stay near the alternative airport or station (60 € - 90 €) **must be added** to the door-to-door cost and prominently flagged as an operational risk.

### Final Synthesis Table
Produce a comparative matrix sorted strictly by **ascending total door-to-door cost**:

| Rang | Aéroport | Dates effectives | Décalage | Escales | Bagages | Prix vol | Transfert | Coût total P2P | Économie vs P1 | Lien direct & Instructions | Date vérif. |
|------|----------|------------------|----------|---------|---------|----------|-----------|-----------------|----------------|-----------------------------|-------------|
| REF  | Principal | Dates demandées | ±0 | ... | Cabine incluse | ... | — | ... | — | [Compagnie](URL_profonde) | YYYY-MM-DD |
| 1    | Alternatif | ... | Aller +2j | ... | +€35 soute | ... | €X (train) | ... | -€X (-Y%) | [Compagnie](URL_profonde) | YYYY-MM-DD |

- The Pass 1 reference baseline **must always appear as the REF row**, regardless of cost rank.
- The `Bagages` column is mandatory: specifies whether checked luggage, trolley, or personal item only is covered.
- Passes must be executed and displayed in strict chronological sequence: 1 $\rightarrow$ 2 $\rightarrow$ 3 $\rightarrow$ 4.

## 9. Output Format
All outputs must include a structured YAML block:
```yaml
summary: ""
recommendations:
  - pass_1_base:
      airport: ""
      airline: ""
      route: ""
      baggage_policy: ""
      cost_breakdown:
        flight_per_person: ""
        flight_total: ""
        transfer_total: "€0"
        overnight_stay: "€0"
        door_to_door_total: ""
      direct_url: ""
      booking_instructions: ""
      verification_date: "YYYY-MM-DD"
  - pass_2_multi_airport: []
  - pass_3_flexible_dates: []
  - pass_4_combined: []
  - synthesis_table: []
source_log: []
assumptions: []
missing_information: []
verification_required: []
risks: []
```

## 10. Concrete Example
**User Request:**
> "Recherche des vols Paris → Lisbonne, 2 adultes, 10-17 octobre 2026, dates flexibles ±3 jours, 1 bagage cabine chacun + 1 valise en soute."

**Expected Output:**
```yaml
summary: "Recherche de vols Paris → Lisbonne en 4 passes réalisée. Passe 1 référence : CDG→LIS direct TAP à €185/pers (total €370, easyJet à €240 sans soute). Passe 2 : Porto (OPO) et Faro (FAO) identifiés avec transferts ferroviaire/routier le jour même. Passe 3 : économie de €50 en décalant l'aller au 12 octobre. Passe 4 : combinaison OPO + départ 12 octobre offrant -38% d'économie porte-à-porte."
recommendations:
  - pass_1_base:
      airport: "LIS (Lisbonne Humberto Delgado)"
      airline: "TAP Air Portugal"
      route: "CDG → LIS direct"
      baggage_policy: "1 accessoire + 1 bagage cabine 10kg inclus (soute +€30)"
      cost_breakdown:
        flight_per_person: "€185"
        flight_total_2pax: "€370"
        ground_transfer_2pax: "€0"
        overnight_stay: "€0"
        door_to_door_total: "€370"
      direct_url: "https://www.flytap.com/en/booking/flights"
      booking_instructions: "Sélectionner Paris (CDG) → Lisbonne (LIS), 10 au 17 octobre 2026, 2 adultes."
      verification_date: "2026-09-17"
  - pass_2_multi_airport:
      - airport: "OPO (Porto Francisco Sá Carneiro)"
        airline: "Ryanair"
        route: "BVA → OPO direct"
        baggage_policy: "Petit sac inclus; option Regular cabine + soute 20kg (+€35/pers)"
        transfer_to_lisbon:
          mode: "Train CP Alfa Pendular (Campanhã → Santa Apolónia)"
          duration: "2h45"
          operator_url: "https://www.cp.pt/passageiros/en"
          last_departure: "20h32 (vol atterrit à 17h15, battement de 3h17 suffisant)"
        cost_breakdown:
          flight_base_2pax: "€130 (2x €65)"
          ground_transfer_2pax: "€50 (2x €25 train CP promo)"
          overnight_stay: "€0 (correspondance le jour même confirmée)"
          door_to_door_total: "€180"
        saving_vs_pass1: "-€60 vs best P1 easyJet €240 (-25%)"
        retained: true
        reason: "Économie de 25% (≥ 20% requis) avec transfert fluide le jour même"
        direct_url: "https://www.ryanair.com/gb/en/trip/flights/select"
        booking_instructions: "Sélectionner Paris Beauvais (BVA) → Porto (OPO), 10 au 17 octobre 2026."
        verification_date: "2026-09-17"
      - airport: "FAO (Faro)"
        airline: "easyJet"
        route: "ORY → FAO direct"
        baggage_policy: "Petit sac sous siège inclus"
        transfer_to_lisbon:
          mode: "Autocar Rede Expressos (Faro Terminal → Lisboa Sete Rios)"
          duration: "3h15"
          operator_url: "https://www.rede-expressos.pt"
          last_departure: "20h00 (vol atterrit à 16h40, battement suffisant)"
        cost_breakdown:
          flight_base_2pax: "€150 (2x €75)"
          ground_transfer_2pax: "€40 (2x €20 autocar)"
          overnight_stay: "€0 (correspondance le jour même confirmée)"
          door_to_door_total: "€190"
        saving_vs_pass1: "-€50 vs best P1 easyJet €240 (-21%)"
        retained: true
        reason: "Économie de 21% (≥ 20% requis, soit 50 €)"
        direct_url: "https://www.easyjet.com/en/buy/flights"
        booking_instructions: "Sélectionner Paris Orly (ORY) → Faro (FAO), 10 au 17 octobre 2026."
        verification_date: "2026-09-17"
  - pass_3_flexible_dates:
      - shift: "Aller +2j (12 oct), Retour identique (17 oct)"
        airline: "easyJet"
        baggage_policy: "Petit sac inclus"
        cost_breakdown:
          flight_total_2pax: "€190 (2x €95)"
          transfer_total: "€0"
          overnight_stay: "€0"
          door_to_door_total: "€190"
        saving_vs_pass1: "-€50 vs best P1 (€190 vs €240)"
        direct_url: "https://www.easyjet.com/en/buy/flights"
        booking_instructions: "Sélectionner Paris CDG → LIS, 12 au 17 octobre 2026."
        verification_date: "2026-09-17"
  - pass_4_combined:
      - airport: "OPO (Porto)"
        shift: "Aller +2j (12 oct), Retour identique (17 oct)"
        airline: "Ryanair"
        cost_breakdown:
          flight_total_2pax: "€100 (2x €50)"
          ground_transfer_2pax: "€50 (2x €25 train CP)"
          overnight_stay: "€0"
          door_to_door_total: "€150"
        saving_vs_pass1: "-€90 vs best P1 (-38%)"
        retained: true
        direct_url: "https://www.ryanair.com/gb/en/trip/flights/select"
        booking_instructions: "Sélectionner BVA → OPO, 12 au 17 octobre 2026."
        verification_date: "2026-09-17"
  - synthesis_table: "Tableau comparatif trié par coût porte-à-porte croissant"
source_log:
  - name: "TAP Air Portugal Official Booking Engine"
    tier: 2
    url: "https://www.flytap.com/en/booking/flights"
    verification_date: "2026-09-17"
  - name: "easyJet Official Flight Search"
    tier: 2
    url: "https://www.easyjet.com/en/buy/flights"
    verification_date: "2026-09-17"
  - name: "Ryanair Official Trip Flight Selector"
    tier: 2
    url: "https://www.ryanair.com/gb/en/trip/flights/select"
    verification_date: "2026-09-17"
  - name: "CP Comboios de Portugal"
    tier: 2
    url: "https://www.cp.pt/passageiros/en"
    verification_date: "2026-09-17"
  - name: "Rede Expressos Portugal"
    tier: 2
    url: "https://www.rede-expressos.pt"
    verification_date: "2026-09-17"
assumptions:
  - "Prix indicatifs constatés à la date de vérification; les tarifs des compagnies low-cost sont hautement volatils."
  - "Valorisation du temps de transfert (transfer_time_value) fixée par défaut à 0 € dans le calcul financier, mais le surplus de durée (+2h45 pour Porto, +3h15 pour Faro) est systématiquement reporté."
  - "Correspondances le jour même vérifiées : vol Porto atterrit à 17h15, laissant 3h17 avant le train de 20h32."
missing_information:
  - "Préférence de gare/aéroport de départ en Île-de-France (BVA nécessite une navette dédiée à €16.90/pers depuis Porte Maillot)."
  - "Poids exact et dimension des valises en soute souhaitées."
verification_required:
  - "Vérifier le tarif en direct sur les sites officiels des compagnies aériennes avant toute décision."
  - "Réserver les billets Promo Trains CP dès l'ouverture de la fenêtre de réservation (60 jours avant)."
risks:
  - "Beauvais (BVA) est situé à 85 km de Paris : prévoir 1h15 de navette et 34 € A/R par personne."
  - "Une arrivée tardive à Faro après 19h30 imposerait une nuit d'hôtel de transit (€70) car le dernier autocar part à 20h00."
```

## Direct Link Requirements & Flight Source Rules
- Every flight option must include a **deep direct URL to the airline's official booking engine** (Tier 2). Generic root domain homepages are strictly prohibited.
- If pre-filled query parameters are unsupported by the carrier, provide the deep search page URL and specify step-by-step user input instructions.
- Ground transfer fares must cite the official operator URL (Tier 2, e.g. `cp.pt` or `rede-expressos.pt`).
- Every price must carry an explicit `verification_date` in `YYYY-MM-DD` format.
