---
name: flight-search
description: Searches for flight options using a structured 4-pass methodology (base, multi-airport, flexible dates, combined) to find optimal door-to-door air travel with verified direct booking links.
conditions: Use when travel planning requires flight-search capabilities or air travel comparison.
---

# flight-search

## 1. Role & Identity
Air travel search specialist executing a systematic 4-pass scan to identify optimal flight options, comparing base fares against alternative airports, flexible dates, and combined permutations, always computing total door-to-door cost including ground access to departure airports, ground transfers at destination, luggage policies, and potential overnight stays.

## 2. Expected Inputs
- **Origin & Destination**: City/airport of departure and arrival.
- **Dates & Trip Type**:
  - `round_trip` (default): Departure date and return date (exact or flexible).
  - `one_way` (aller simple): Departure date only. Passes 3 and 4 test date shifts exclusively on the departure date.
  - `multi_city` (multi-villes): List of ordered route segments. Each segment is evaluated as an independent 4-pass search before chronological consolidation.
- **Flexibility**: Whether dates are strictly fixed (`dates_fixed: true`) or flexible ($\pm 1, \pm 2, \pm 3$ days).
- **Party Composition**: Number of adult/child travelers and cabin class preference.
- **Luggage Policy Requirements**: Cabin bag only (under-seat or trolley) vs checked luggage (number of bags and weight). When checked bags are required by the brief, checked baggage fees **must be included in the evaluated cost**.
- **Budget & Constraints**: Maximum budget (if any), traveler origin location in departure city (to compute origin access cost), traveler nationality (for transit visa prerequisites).

## 3. Expected Outputs
- 4-pass progressive flight search results with clear separation between passes.
- Comprehensive synthesis table ranked by ascending total door-to-door cost, including dedicated `Bagages` column.
- Direct booking links (Tier 1-2) using deep booking URLs with pre-filled parameters or explicit user search instructions.
- Mandatory line-by-line door-to-door cost breakdown (`cost_breakdown`) itemizing flight, departure airport access, destination transfer, and transit overnight stay (leaving zero unexplained amounts).
- Single best Pass 1 reference baseline price always visible as baseline `REF`.
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

### Distant Horizons (> 11 months / > 330 days) & Unopened Airline Inventories
- Commercial airline flight schedules and ticketing inventories are typically opened only 330 to 360 days in advance.
- When travel dates exceed this horizon (> ~11 mois / > 330 jours) or when real-time live prices cannot be confirmed directly:
  - The skill **must output a realistic price range** (e.g. `850-950 €` or `€850-€950`), rather than an illusory exact price with two decimals (e.g. `872.45 €`).
  - The pricing status must be systematically and explicitly tagged: `"estimation, inventaire non ouvert"`.
  - Fictitious exact pricing for unopened inventories is strictly forbidden.

## 6. Sourcing Policy
All references must strictly adhere to the 6-tier sourcing hierarchy:
- **Tier 1**: Official government portals, tourism ministries, embassies, municipal administrations.
- **Tier 2**: Official direct operators (rail networks, airlines, ferry lines, airport express shuttles).
- **Tier 3**: Recognized tourism institutions (regional tourism boards, national park services, UNESCO).
- **Tier 4**: Recognized editorial sources (Michelin Guide, Lonely Planet, established travel journalists).
- **Tier 5**: Community reviews (TripAdvisor, Google Maps reviews, travel forums) for qualitative feedback only.
- **Tier 6**: Social media (TikTok, Instagram, RedNote, personal blogs) strictly tagged as `social_discovery_only`.

### Flight-Specific Source Rules & Deep Link Mandate
- **Airline direct websites** (e.g., Air France, TAP Air Portugal, easyJet, Ryanair) are **Tier 2** and must always serve as the primary booking link.
- **Active Discovery via Adaptive Cross-Comparison**:
  - Before verifying on airline direct sites, use **at least one available comparison engine** in Passes 1, 2, and 3. Google Flights, Skyscanner, and Trip.com are supported examples, not a rigid quota.
  - Query a second or third engine only when it materially improves coverage: a price discrepancy, missing route, flexible-date search, nearby-airport search, regional inventory gap, or low confidence.
  - When an engine is blocked, unavailable, or redundant, record that fact in `source_log`; do not retry mechanically or invent results.
  - Supported engines include:
    1. **Google Flights**
    2. **Skyscanner**
    3. **Trip.com**
  - **Details of Cross-Comparison per Pass**:
    - **Pass 1 (Base)**: Run an exact-date search on one engine. Add another engine if the route or price needs corroboration, then preselect the top 3-5 offers.
    - **Pass 2 (Multi-Airport)**: Use a nearby-airport or broad-regional search. Cross-check only retained candidates whose coverage or price is uncertain.
    - **Pass 3 (Flexible Dates)**: Use an available date grid or price calendar. Add another engine when the identified minimum is not sufficiently supported.
  - **Strict Verification & Direct Booking Boundary**:
    - The cross-comparison is used **exclusively for rapid discovery, screening, and price spread detection**.
    - Every preselected candidate flight, true door-to-door cost, baggage fee, and live schedule must then be verified directly on the official airline website (Tier 2).
    - **Single Booking Link Rule**: The official airline direct portal remains the **SOLE booking link** displayed to the traveler. Trip.com, Skyscanner, and Google Flights are comparison tools only and are **NEVER** displayed as flight booking links.
    - **Preserved Exception**: Trip.com remains the primary practical booking channel for Chinese rail ticketing in `transport-research`.
  - **Taxonomy & Classification Note**:
    - Google Flights, Skyscanner, and Trip.com are classified as **comparison engines** ("moteurs de comparaison") during the discovery phase, distinct from editorial Tier 4 guides (Michelin, Lonely Planet).
    - **Trip.com Dual Status**: Trip.com functions strictly as a comparison tool for flights (never as a booking link), whereas it serves as the authorized primary practical booking channel for Chinese rail ticketing in `transport-research`.
  - **OTA Ban Intact**: The prohibition of OTAs as flight booking links remains absolute (Expedia, eDreams, Kiwi, Opodo, Lastminute forbidden; Trip.com strictly confined to discovery/comparison, never as a flight booking link).
  - **Adaptive Source Logging**: Every engine actually consulted must appear individually in `source_log` with verification date (`YYYY-MM-DD`). Record unavailable or deliberately skipped engines and the reason. At least one comparison engine and one direct-airline verification are required for a booking-ready retained option.
- **Deep URLs Mandatory on EVERY Retained Option**:
  - Every retained flight option (`retained: true` or Pass 1 `REF`) across Passes 1, 2, 3, and 4 **must provide a deep booking link** to the airline's flight selection portal (e.g., `https://www.flytap.com/en/booking/flights`, `https://www.easyjet.com/en/buy/flights`, `https://www.ryanair.com/gb/en/trip/flights/select`). Generic root domain homepages (e.g., `ryanair.com`, `easyjet.com/en`, `airfrance.fr`) are strictly forbidden.
  - **Mandatory Step-by-Step Instructions**: On every retained option, provide explicit user search instructions:
    `"Action requise sur le site : sélectionner <Origine> → <Destination>, Dates <YYYY-MM-DD> au <YYYY-MM-DD>, <N> passagers, classe <Classe>."`

## 7. Safety Policy
- **Never make purchases.**
- **Never make reservations.**
- **Never enter personal or payment data.**
- **Never share travel documents.**
- **Never bypass login, paywalls, robots rules or site restrictions.**
- **Never present social-media content as verified logistical information.**

## 8. Methodology: 4-Pass Progressive Search

### Pass 1 — Base (Single Best Reference Price)
Search flights to the **principal airport** of the destination city on the **exact dates** requested by the user, incorporating origin access from the traveler's city center (e.g. RER B to CDG or Metro 14 to Orly) and luggage requirements.
- **Adaptive Cross-Comparison**: Query at least one available comparison engine on the exact dates requested. Add another engine only when needed to resolve a price discrepancy, coverage gap, or confidence issue. Document all engines used or unavailable.
- **Direct Carrier Verification**: Verify the preselected candidates directly on official airline portals (Tier 2) to confirm final base fare, baggage fees, and conditions.
- When multiple airlines are found (e.g., TAP at €400, Transavia at €318, easyJet at €270 with checked bag), **the single best Pass 1 result** (the cheapest option strictly conforming to the brief's baggage and timing requirements) serves as the **unique reference baseline (REF)** for all subsequent comparisons.
- Record: airline, flight numbers, flight duration, stops, baggage allowance, total price, deep direct URL, verification date, and comparison engine price deltas.

### Pass 2 — Multi-Airport (Fixed Dates)
Keeping the exact travel dates from Pass 1, investigate alternative arrival gateways:
- **Adaptive Cross-Comparison Step**: Use an available nearby-airport or broad-regional search to discover alternative departure and arrival hubs. Cross-check only material candidates whose price or coverage is uncertain.
- **Direct Carrier Verification**: Verify candidate flights, exact schedules, and live bag fees directly on official airline portals (Tier 2). Document engines used, skipped, or unavailable in `source_log`.
- Other airports serving the same metropolitan area (e.g., London: LHR, LGW, STN, LTN, SEN).
- Airports of adjacent cities connected by direct high-speed rail or express bus (e.g., Porto or Faro for Lisbon; Girona or Reus for Barcelona; Bologna or Florence for Rome).
- Alternative departure airports in the traveler's origin region (e.g., Paris Beauvais BVA instead of CDG/Orly).
- **Combinatorial Bound**: Evaluate a **maximum of 5 alternative airports**.

#### Complete Door-to-Door Cost Formula
For every alternative airport option, compute the comprehensive door-to-door cost:
```
door_to_door_cost = flight_price + origin_access_cost + ground_transfer_cost + overnight_stay_cost + transfer_time_penalty
```
Where:
- `flight_price`: Total flight cost for all travelers, **including checked baggage fees if demanded by the brief**, mandatory taxes, and fees.
- `origin_access_cost`: Total ground transit cost from the traveler's city center to the departure airport for all travelers. Use one-way access for `one_way`; use outbound and return access for `round_trip`. **To ensure a fair comparison, compute origin access for baseline and alternatives on the same trip basis.**
- `ground_transfer_cost`: Total round-trip ground transport (rail, express bus, shuttle) connecting the alternative arrival airport to the final destination city center for all travelers (citing Tier 2 operators like CP, SNCF, Renfe, Rede Expressos).
- `overnight_stay_cost`: Cost of a transit overnight stay (standard rate: 60 € to 90 € / room) if flight arrival occurs too late to catch the last onward ground connection on the same day.
- `transfer_time_penalty` (or `transfer_time_value`): Economic valuation of extra travel fatigue and lost vacation time. Defined as a flat rate of **15 € per hour of additional ground transit time** compared to the Pass 1 baseline journey, documented explicitly in `assumptions`.
  - **Default Application Rule**: This penalty is **applied by default** whenever the cumulative door-to-door transit time exceeds the Pass 1 baseline by **more than 4 hours** (> 4h). If the additional transit time is $\le 4\text{ h}$, `transfer_time_penalty` is 0 € by default.
  - **Traveler Opt-Out**: The traveler can explicitly disable this penalty by setting `transfer_time_penalty: false` in the brief, in which case the penalty is 0 € regardless of duration, but the extra travel time must remain clearly visible in hours.

#### Mandatory Arithmetic & Line-by-Line Decomposition
Every door-to-door total MUST display its complete line-by-line itemization (`cost_breakdown`):
- Flight total with luggage (e.g. 2 travelers × €65 base + 1 checked bag €35 = €165)
- Origin airport access total (e.g. 2 travelers × €33.80 A/R navette BVA = €68)
- Ground transfer total at destination (e.g. 2 travelers × €25 train CP = €50)
- Transit overnight accommodation if applicable (e.g. €0 if same-day transfer confirmed)
- Additional fees
**Zero unexplained or opaque amounts**: The mathematical sum of the individual line items must equal the declared door-to-door total.

#### Retention Threshold
Retain an alternative airport option **only if** it yields a net saving $\ge 20\%$ OR $\ge 50\,€$ compared to the single best Pass 1 reference baseline (`REF`). If an alternative departure airport adds substantial shuttle costs and extra hours without meeting this saving threshold, it must be **explicitly rejected (`retained: false`)** with documented reasons.
- **Mandatory Deep Link on Retained Options**: Every retained alternative option (`retained: true`) must include a deep direct booking link (`direct_url`) and step-by-step user search instructions (`booking_instructions`).

### Pass 3 — Flexible Dates (Principal Airport)
**Skip this pass entirely if the user specified `dates_fixed: true` or non-negotiable dates.**
Using exclusively the principal airport from Pass 1:
- **Adaptive Cross-Comparison Step**: Use an available flexible-date grid or price calendar in the $\pm 3$ days window. Add another engine only when a fare dip, missing route, or price discrepancy needs corroboration.
- **Direct Carrier Verification**: Verify prices, seats, and baggage policies directly on the airline website (Tier 2). Record every engine consulted, skipped, or unavailable in `source_log`.
- For round-trip journeys: test date shifts of -3, -2, -1, +1, +2, +3 days on departure AND return **independently**.
- For one-way journeys: test shifts of -3, -2, -1, +1, +2, +3 days on the departure date only.
- Document the exact date shift (e.g., "Aller +2j, Retour identique") and price delta vs the single best Pass 1 baseline.
- **Mandatory Deep Link on Retained Options**: Every retained date-shift option (`retained: true`) must include a deep direct booking link (`direct_url`) and step-by-step user search instructions (`booking_instructions`).

### Pass 4 — Combined (Flexible Dates × Multi-Airport)
**Skip this pass entirely if the user specified `dates_fixed: true`.**
Combine date flexibility with alternative airports:
- **Combinatorial Limitation**: Limit date shifts to **$\pm 2$ days** (rather than $\pm 3$) centered around the **top 3 most promising alternative candidates** identified across Pass 2 and Pass 3.
- The agent prioritizes high-saving combinations (e.g. low-cost midweek fare drops paired with high-speed rail connections).
- Apply the complete door-to-door formula (including origin access, checked luggage, and transfer time penalty if > 4h) and the retention threshold ($\ge 20\%$ or $\ge 50\,€$ saving vs Pass 1 REF).
- **Mandatory Deep Link on Retained Options**: Every retained combined option (`retained: true`) must include a deep direct booking link (`direct_url`) and step-by-step user search instructions (`booking_instructions`).

### Night Transfers & Same-Day Connection Rule
When evaluating alternative airports:
- Inquire and verify the scheduled departure time of the last train or bus to the final destination on the arrival evening.
- Allow an incompressible safety buffer of at least **45 minutes** between flight landing and ground transit departure (for deplaning, border control, luggage reclaim, and terminal exit).
- If flight arrival is too late for same-day connection, an overnight stay near the alternative airport or station (60 € - 90 €) **must be added** to the door-to-door cost and prominently flagged as an operational risk.

### Final Synthesis Table
Produce a comparative matrix sorted strictly by **ascending total door-to-door cost**:

| Rang | Aéroport | Dates effectives | Décalage | Escales | Bagages | Prix vol | Accès origine | Transfert dest. | Coût total P2P | Économie vs P1 | Lien direct & Instructions | Date vérif. |
|------|----------|------------------|----------|---------|---------|----------|---------------|-----------------|-----------------|----------------|-----------------------------|-------------|
| REF  | Principal | Dates demandées | ±0 | ... | Soute incluse | ... | €X (RER) | — | ... | — | [Compagnie](URL_profonde) | YYYY-MM-DD |
| 1    | Alternatif | ... | Aller +2j | ... | Soute incluse | ... | €Y (navette) | €Z (train) | ... | -€X (-Y%) | [Compagnie](URL_profonde) | YYYY-MM-DD |

- The Pass 1 single best reference baseline **must always appear as the REF row**, regardless of cost rank.
- The `Bagages` column is mandatory: specifies whether checked luggage, trolley, or personal item only is covered. All compared fares must satisfy the brief's baggage requirements.
- Passes must be executed and displayed in strict chronological sequence: 1 $\rightarrow$ 2 $\rightarrow$ 3 $\rightarrow$ 4.

## 9. Output Format
All outputs must conform to `TravelDossier v1` (`docs/travel-dossier-v1.md`). The specialized flight structure belongs in `recommendations`; every critical price or schedule also needs a claim and source reference:
```yaml
summary: ""
recommendations:
  - pass_1_base:
      airport: ""
      airline: ""
      route: ""
      baggage_policy: ""
      cost_breakdown:
        flight_base: ""
        checked_bag_fee: ""
        flight_total_with_luggage: ""
        origin_access_cost: ""
        ground_transfer_destination: "€0"
        overnight_stay: "€0"
        transfer_time_penalty: "€0"
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
The fixture below is illustrative only. It is not evidence of current fares, schedules, inventory, or availability.
```yaml
summary: "Recherche de vols Paris → Lisbonne en 4 passes réalisée pour 2 adultes avec 1 valise en soute. Référence Passe 1 (REF) : easyJet CDG→LIS direct à €270 (€240 vol + €30 soute) + €47 RER = €317 porte-à-porte. Passe 2 : Porto via Beauvais revient à €283 tout compris (€165 vol+soute + €68 navette BVA + €50 train CP) soit seulement €34 d'économie (11%) pour +4h de trajet, donc REJETÉE sous le seuil de 20%/€50; Faro via Orly retenue à €261 (-€56). Passe 3 : easyJet CDG décalé au 12 octobre à €227 (-€90). Passe 4 : Faro décalé au 12 octobre offrant le meilleur tarif combiné à €211 (-€106, -33%)."
recommendations:
  - pass_1_base:
      airport: "LIS (Lisbonne Humberto Delgado)"
      airline: "easyJet (Meilleur résultat Passe 1 conforme au brief)"
      route: "CDG → LIS direct"
      baggage_policy: "1 bagage cabine par personne inclus + 1 valise en soute 15kg (+€30)"
      cost_breakdown:
        flight_base_2pax: "€240 (2x €120)"
        checked_bag_2pax: "€30 (1 valise partagée)"
        flight_total_with_luggage: "€270"
        origin_access_cost: "€47 (RER B Paris Châtelet → CDG A/R 2p)"
        ground_transfer_destination: "€0"
        overnight_stay: "€0"
        transfer_time_penalty: "€0"
        door_to_door_total: "€317"
      is_baseline_reference: true
      direct_url: "https://www.easyjet.com/en/buy/flights"
      booking_instructions: "Sélectionner Paris (CDG) → Lisbonne (LIS), 10 au 17 octobre 2026, 2 adultes, ajouter 1 bagage en soute 15kg."
      verification_date: "2026-09-17"
  - pass_2_multi_airport:
      - airport: "OPO (Porto Francisco Sá Carneiro via Paris-Beauvais)"
        airline: "Ryanair"
        route: "BVA → OPO direct"
        baggage_policy: "Petit sac inclus + 1 valise en soute 20kg (+€35)"
        transfer_to_lisbon:
          mode: "Train CP Alfa Pendular (Campanhã → Santa Apolónia)"
          duration: "2h45"
          operator_url: "https://www.cp.pt/passageiros/en"
          last_departure: "20h32 (vol atterrit à 17h15, battement de 3h17 suffisant)"
        cost_breakdown:
          flight_base_2pax: "€130 (2x €65)"
          checked_bag_fee: "€35 (1 valise soute 20kg)"
          origin_access_cost: "€68 (Navette officielle Paris Porte Maillot → BVA A/R 2p: 4x €16.90)"
          ground_transfer_destination: "€50 (Train CP promo A/R 2p)"
          overnight_stay: "€0 (correspondance le jour même confirmée)"
          transfer_time_penalty: "€0 (additional time does not exceed the >4h threshold)"
          door_to_door_total: "€283"
        saving_vs_pass1: "-€34 vs REF easyJet €317 (-11%)"
        retained: false
        reason: "Économie de €34 (11%) inférieure au seuil minimal requis de ≥ 20% ou ≥ €50, avec pénalité de +4h de transport terrestre cumulé (BVA navette + CP train)."
        direct_url: "https://www.ryanair.com/gb/en/trip/flights/select"
        booking_instructions: "Sélectionner Paris Beauvais (BVA) → Porto (OPO), 10 au 17 octobre 2026, ajouter 1 bagage en soute 20kg."
        verification_date: "2026-09-17"
      - airport: "FAO (Faro via Paris-Orly)"
        airline: "easyJet"
        route: "ORY → FAO direct"
        baggage_policy: "Petit sac inclus + 1 valise en soute 15kg (+€30)"
        transfer_to_lisbon:
          mode: "Autocar Rede Expressos (Faro Terminal → Lisboa Sete Rios)"
          duration: "3h15"
          operator_url: "https://www.rede-expressos.pt"
          last_departure: "20h00 (vol atterrit à 16h40, battement suffisant)"
        cost_breakdown:
          flight_base_2pax: "€150 (2x €75)"
          checked_bag_fee: "€30 (1 valise soute 15kg)"
          origin_access_cost: "€41 (Métro ligne 14 Châtelet → Orly A/R 2p)"
          ground_transfer_destination: "€40 (Autocar A/R 2p)"
          overnight_stay: "€0 (correspondance le jour même confirmée)"
          transfer_time_penalty: "€0"
          door_to_door_total: "€261"
        saving_vs_pass1: "-€56 vs REF easyJet €317 (-18%)"
        retained: true
        reason: "Économie nette de €56 (≥ €50 requis) avec correspondance terrestre directe le jour même."
        direct_url: "https://www.easyjet.com/en/buy/flights"
        booking_instructions: "Sélectionner Paris Orly (ORY) → Faro (FAO), 10 au 17 octobre 2026, ajouter 1 valise soute 15kg."
        verification_date: "2026-09-17"
  - pass_3_flexible_dates:
      - shift: "Aller +2j (12 oct), Retour identique (17 oct)"
        airline: "easyJet"
        route: "CDG → LIS direct"
        baggage_policy: "1 valise en soute 15kg incluse (+€30)"
        cost_breakdown:
          flight_base_2pax: "€150 (2x €75)"
          checked_bag_fee: "€30 (1 valise soute)"
          origin_access_cost: "€47 (RER B A/R 2p)"
          ground_transfer_destination: "€0"
          overnight_stay: "€0"
          transfer_time_penalty: "€0"
          door_to_door_total: "€227"
        saving_vs_pass1: "-€90 vs REF easyJet €317 (-28%)"
        retained: true
        direct_url: "https://www.easyjet.com/en/buy/flights"
        booking_instructions: "Sélectionner Paris CDG → LIS, 12 au 17 octobre 2026, ajouter 1 valise soute."
        verification_date: "2026-09-17"
  - pass_4_combined:
      - airport: "FAO (Faro via Paris-Orly)"
        shift: "Aller +2j (12 oct), Retour -1j (16 oct)"
        airline: "easyJet"
        baggage_policy: "1 valise en soute 15kg incluse (+€30)"
        cost_breakdown:
          flight_base_2pax: "€100 (2x €50)"
          checked_bag_fee: "€30 (1 valise soute)"
          origin_access_cost: "€41 (Métro 14 A/R 2p)"
          ground_transfer_destination: "€40 (Autocar A/R 2p)"
          overnight_stay: "€0"
          transfer_time_penalty: "€0"
          door_to_door_total: "€211"
        saving_vs_pass1: "-€106 vs REF easyJet €317 (-33%)"
        retained: true
        direct_url: "https://www.easyjet.com/en/buy/flights"
        booking_instructions: "Sélectionner ORY → FAO, 12 au 16 octobre 2026, ajouter 1 valise soute."
        verification_date: "2026-09-17"
  - synthesis_table: "Tableau comparatif trié par coût porte-à-porte croissant avec ligne REF unique"
source_log:
  - name: "Google Flights (Moteur de comparaison / découverte & grille tarifaire)"
    source_type: "comparison_engine"
    authority: "secondary"
    url: "https://www.google.com/travel/flights"
    verification_date: "2026-09-17"
  - name: "Skyscanner (Moteur de comparaison / calendrier & aéroports)"
    source_type: "comparison_engine"
    authority: "secondary"
    url: "https://www.skyscanner.net"
    verification_date: "2026-09-17"
  - name: "Trip.com (Moteur de comparaison de vols / recherche large)"
    source_type: "comparison_engine"
    authority: "secondary"
    url: "https://www.trip.com/flights"
    verification_date: "2026-09-17"
  - name: "easyJet Official Flight Booking Engine"
    tier: 2
    url: "https://www.easyjet.com/en/buy/flights"
    verification_date: "2026-09-17"
  - name: "Ryanair Official Trip Flight Selector"
    tier: 2
    url: "https://www.ryanair.com/gb/en/trip/flights/select"
    verification_date: "2026-09-17"
  - name: "Aéroport Paris-Beauvais Navette Officielle"
    tier: 2
    url: "https://www.aeroportparisbeauvais.com/acces-et-parking/navette-aeroport-paris-porte-maillot"
    verification_date: "2026-09-17"
  - name: "CP Comboios de Portugal (Liaison Porto-Lisbonne)"
    tier: 2
    url: "https://www.cp.pt/passageiros/en"
    verification_date: "2026-09-17"
  - name: "Rede Expressos Portugal (Liaison Faro-Lisbonne)"
    tier: 2
    url: "https://www.rede-expressos.pt"
    verification_date: "2026-09-17"
assumptions:
  - "Comparatif croisé systématique réalisé sur 3 moteurs (Google Flights, Skyscanner, Trip.com) pour les passes 1, 2 et 3. Écart constaté en Passe 1 : easyJet affiché à €240 sur Google Flights/Skyscanner vs €244 sur Trip.com ; tarif vérifié et confirmé à €240 + €30 soute sur le site officiel easyJet."
  - "L'option Passe 1 de référence (REF) retenue est la meilleure offre directe easyJet conforme au brief (€317 tout compris avec soute et RER B)."
  - "Accès à l'aéroport d'origine inclus pour toutes les options afin de comparer à équipement égal (RER B €47 pour CDG, Métro 14 €41 pour Orly, navette €68 pour Beauvais)."
  - "Les frais de soute requis par le brief sont rigoureusement intégrés dans le coût des billets de chaque option."
  - "Pénalité de temps de transfert (transfer_time_penalty à 15 €/h) : s'applique par défaut si le temps additionnel dépasse 4h vs Pass 1. Pour Porto (+4h de trajet terrestre cumulé BVA+CP), le surcoût de temps et l'accès à Beauvais (€68) rendent l'option non rentable en Passe 2."
missing_information:
  - "Adresse exacte de départ en Île-de-France (pour affiner le temps de trajet vers Porte Maillot vs Châtelet)."
verification_required:
  - "Confirmer le prix final des billets et des options bagages directement sur les sites des transporteurs."
  - "Réserver la navette Beauvais et le train CP en ligne à l'avance pour bénéficier des tarifs préférentiels."
risks:
  - "L'option Beauvais impose 1h15 de navette et un éloignement de 85 km, rendant l'économie insuffisante en Passe 2."
  - "Correspondances à Faro : veiller à atterrir avant 19h00 pour garantir l'autocar de 20h00 vers Lisbonne."
```

## Direct Link Requirements & Flight Source Rules
- Every flight option must include a **deep direct URL to the airline's official booking engine** (Tier 2). Generic root domain homepages are strictly prohibited.
- **Deep link & Search Instructions Mandatory on ALL Retained Options**: Every retained option across Passes 1, 2, 3, and 4 must provide both the deep booking link (`direct_url`) and explicit step-by-step query instructions (`booking_instructions`) for the user.
- **Adaptive Cross-Comparison**: Use at least one available comparison engine across Passes 1, 2, and 3, and add further engines only for material coverage or confidence gaps. Record consulted, skipped, and unavailable engines in `source_log`.
- **Direct Carrier Booking Only**: Booking links are exclusively direct carrier websites (Tier 2). Google Flights, Skyscanner, and Trip.com are comparison tools only and must NEVER appear as flight booking links. (Trip.com is retained as a booking channel solely for Chinese rail in transport-research).
- **Unopened Inventories (> 11 months / > 330 days)**: Must output realistic price ranges (e.g. `850-950 €`), tagged `"estimation, inventaire non ouvert"`. Fictitious exact decimals are prohibited.
- Ground transfer fares must cite the official operator URL (Tier 2, e.g. `cp.pt`, `rede-expressos.pt`, `aeroportparisbeauvais.com`).
- Every price must carry an explicit `verification_date` in `YYYY-MM-DD` format.
