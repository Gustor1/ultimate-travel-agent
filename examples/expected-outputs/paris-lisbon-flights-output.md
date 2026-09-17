# Expected Output: Paris → Lisbon Flight Search (4-Pass)

## Pass 1 — Base (Reference)

```yaml
pass_1_base:
  airport: "LIS (Lisbon Humberto Delgado)"
  search_dates:
    departure: "2026-10-10"
    return: "2026-10-17"
  options:
    - airline: "TAP Air Portugal"
      route: "CDG → LIS (direct)"
      baggage_policy: "1 bagage cabine 10kg inclus (soute +€30)"
      cost_breakdown:
        flight_per_person: "€185"
        flight_total_2pax: "€370"
        ground_transfer: "€0"
        overnight_stay: "€0"
        door_to_door_total: "€370"
      direct_url: "https://www.flytap.com/en/booking/flights"
      booking_instructions: "Sélectionner Paris (CDG) → Lisbonne (LIS), 10 au 17 octobre 2026, 2 adultes."
      verification_date: "2026-09-17"
    - airline: "Transavia"
      route: "ORY → LIS (direct)"
      baggage_policy: "Petit sac inclus (cabine +€15, soute +€28)"
      cost_breakdown:
        flight_per_person: "€145"
        flight_total_2pax: "€290"
        ground_transfer: "€0"
        overnight_stay: "€0"
        door_to_door_total: "€290"
      direct_url: "https://www.transavia.com/en-EU/book-a-flight/flights/search/"
      booking_instructions: "Sélectionner Paris Orly (ORY) → Lisbonne (LIS), 10 au 17 octobre 2026."
      verification_date: "2026-09-17"
    - airline: "easyJet"
      route: "CDG → LIS (direct)"
      baggage_policy: "Petit sac inclus sous siège (grand cabine +€20)"
      cost_breakdown:
        flight_per_person: "€120"
        flight_total_2pax: "€240"
        ground_transfer: "€0"
        overnight_stay: "€0"
        door_to_door_total: "€240"
      direct_url: "https://www.easyjet.com/en/buy/flights"
      booking_instructions: "Sélectionner Paris Charles de Gaulle (CDG) → Lisbonne (LIS), 10 au 17 octobre 2026."
      verification_date: "2026-09-17"
  reference_best_price: "€240 (2 pax, easyJet direct CDG→LIS)"
```

## Pass 2 — Multi-Airport (Fixed Dates 10-17 Oct)

```yaml
pass_2_multi_airport:
  - airport: "OPO (Porto Francisco Sá Carneiro)"
    airline: "Ryanair"
    route: "BVA → OPO (direct)"
    baggage_policy: "Petit sac sous siège inclus (option Regular cabine + soute 20kg +€35/pers)"
    flight_price_per_person: "€65"
    flight_total_2pax: "€130"
    transfer_to_lisbon:
      mode: "CP Alfa Pendular train (Campanhã → Santa Apolónia)"
      duration: "2h45"
      cost_per_person: "€25"
      cost_2pax: "€50"
      operator_url: "https://www.cp.pt/passageiros/en"
      last_departure: "20h32 (vol atterrit à 17h15, battement de 3h17 suffisant)"
    cost_breakdown:
      flight_total: "€130 (2x €65)"
      ground_transfer_total: "€50 (2x €25 train CP)"
      overnight_stay: "€0 (correspondance le jour même confirmée)"
      total_door_to_door: "€180"
    door_to_door_total_2pax: "€180"
    saving_vs_pass1: "-€60 vs best P1 easyJet €240 (-25%)"
    retained: true
    reason: "Économie de 25% (≥ 20% requis) avec transfert fluide le jour même"
    direct_url: "https://www.ryanair.com/gb/en/trip/flights/select"
    booking_instructions: "Sélectionner Paris Beauvais (BVA) → Porto (OPO), 10 au 17 octobre 2026."
    verification_date: "2026-09-17"
  - airport: "FAO (Faro)"
    airline: "easyJet"
    route: "ORY → FAO (direct)"
    baggage_policy: "Petit sac sous siège inclus"
    flight_price_per_person: "€75"
    flight_total_2pax: "€150"
    transfer_to_lisbon:
      mode: "Rede Expressos autocar (Faro Terminal → Lisboa Sete Rios)"
      duration: "3h15"
      cost_per_person: "€20"
      cost_2pax: "€40"
      operator_url: "https://www.rede-expressos.pt"
      last_departure: "20h00 (vol atterrit à 16h40, battement de 3h20 suffisant)"
    cost_breakdown:
      flight_total: "€150 (2x €75)"
      ground_transfer_total: "€40 (2x €20 bus)"
      overnight_stay: "€0 (correspondance le jour même confirmée)"
      total_door_to_door: "€190"
    door_to_door_total_2pax: "€190"
    saving_vs_pass1: "-€50 vs best P1 easyJet €240 (-21%)"
    retained: true
    reason: "Économie de 21% (≥ 20% requis, soit 50 €)"
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner Paris Orly (ORY) → Faro (FAO), 10 au 17 octobre 2026."
    verification_date: "2026-09-17"
```

## Pass 3 — Flexible Dates (Principal Airport LIS)

```yaml
pass_3_flexible_dates:
  - shift: "Aller +2j (12 oct), Retour identique (17 oct)"
    airline: "easyJet"
    route: "CDG → LIS (direct)"
    baggage_policy: "Petit sac inclus"
    flight_price_per_person: "€95"
    cost_breakdown:
      flight_total: "€190 (2x €95)"
      ground_transfer_total: "€0"
      overnight_stay: "€0"
      total_door_to_door: "€190"
    door_to_door_total_2pax: "€190"
    saving_vs_pass1: "-€50 vs best P1 (€190 vs €240)"
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner Paris CDG → LIS, 12 au 17 octobre 2026."
    verification_date: "2026-09-17"
  - shift: "Aller identique (10 oct), Retour -1j (16 oct)"
    airline: "Transavia"
    route: "ORY → LIS (direct)"
    baggage_policy: "Petit sac inclus"
    flight_price_per_person: "€110"
    cost_breakdown:
      flight_total: "€220 (2x €110)"
      ground_transfer_total: "€0"
      overnight_stay: "€0"
      total_door_to_door: "€220"
    door_to_door_total_2pax: "€220"
    saving_vs_pass1: "-€20 vs best P1 (€220 vs €240)"
    direct_url: "https://www.transavia.com/en-EU/book-a-flight/flights/search/"
    booking_instructions: "Sélectionner Paris Orly (ORY) → LIS, 10 au 16 octobre 2026."
    verification_date: "2026-09-17"
  - shift: "Aller +3j (13 oct), Retour -2j (15 oct)"
    airline: "easyJet"
    route: "CDG → LIS (direct)"
    baggage_policy: "Petit sac inclus"
    flight_price_per_person: "€80"
    cost_breakdown:
      flight_total: "€160 (2x €80)"
      ground_transfer_total: "€0"
      overnight_stay: "€0"
      total_door_to_door: "€160"
    door_to_door_total_2pax: "€160"
    saving_vs_pass1: "-€80 vs best P1 (€160 vs €240, -33%)"
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner Paris CDG → LIS, 13 au 15 octobre 2026."
    verification_date: "2026-09-17"
```

## Pass 4 — Combined (Flexible Dates × Alternative Airports)

```yaml
pass_4_combined:
  - airport: "OPO (Porto)"
    shift: "Aller +2j (12 oct), Retour identique (17 oct)"
    airline: "Ryanair"
    baggage_policy: "Petit sac inclus (+€35 soute)"
    flight_price_2pax: "€100 (2x €50)"
    cost_breakdown:
      flight_total: "€100 (2x €50)"
      ground_transfer_total: "€50 (2x €25 train CP)"
      overnight_stay: "€0"
      total_door_to_door: "€150"
    door_to_door_total_2pax: "€150"
    saving_vs_pass1: "-€90 vs best P1 (-38%)"
    retained: true
    direct_url: "https://www.ryanair.com/gb/en/trip/flights/select"
    booking_instructions: "Sélectionner BVA → OPO, 12 au 17 octobre 2026."
    verification_date: "2026-09-17"
  - airport: "FAO (Faro)"
    shift: "Aller +2j (12 oct), Retour -1j (16 oct)"
    airline: "easyJet"
    baggage_policy: "Petit sac inclus"
    flight_price_2pax: "€110 (2x €55)"
    cost_breakdown:
      flight_total: "€110 (2x €55)"
      ground_transfer_total: "€40 (2x €20 autocar)"
      overnight_stay: "€0"
      total_door_to_door: "€150"
    door_to_door_total_2pax: "€150"
    saving_vs_pass1: "-€90 vs best P1 (-38%)"
    retained: true
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner ORY → FAO, 12 au 16 octobre 2026."
    verification_date: "2026-09-17"
```

## Synthesis Table

| Rang | Aéroport | Dates effectives | Décalage | Escales | Bagages | Prix vol (2p) | Transfert (2p) | Coût total P2P | Économie vs P1 | Lien direct & Instructions | Date vérif. |
|------|----------|------------------|----------|---------|---------|---------------|----------------|-----------------|----------------|-----------------------------|-------------|
| REF  | LIS (CDG→LIS) | 10-17 oct | ±0 | direct | Cabine incluse | €240 | — | €240 | — | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 1    | OPO (BVA→OPO) | 12-17 oct | Aller +2j | direct | Sac seul (+€35 soute) | €100 | €50 (CP train) | €150 | -€90 (-38%) | [Ryanair](https://www.ryanair.com/gb/en/trip/flights/select) | 2026-09-17 |
| 2    | FAO (ORY→FAO) | 12-16 oct | Aller +2j, Retour -1j | direct | Sac sous siège | €110 | €40 (autocar) | €150 | -€90 (-38%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 3    | LIS (CDG→LIS) | 13-15 oct | Aller +3j, Retour -2j | direct | Sac sous siège | €160 | — | €160 | -€80 (-33%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 4    | OPO (BVA→OPO) | 10-17 oct | ±0 | direct | Sac seul (+€35 soute) | €130 | €50 (CP train) | €180 | -€60 (-25%) | [Ryanair](https://www.ryanair.com/gb/en/trip/flights/select) | 2026-09-17 |
| 5    | FAO (ORY→FAO) | 10-17 oct | ±0 | direct | Sac sous siège | €150 | €40 (autocar) | €190 | -€50 (-21%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 6    | LIS (CDG→LIS) | 12-17 oct | Aller +2j | direct | Sac sous siège | €190 | — | €190 | -€50 (-21%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |

## Source Log

```yaml
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
  - name: "Transavia Official Booking Portal"
    tier: 2
    url: "https://www.transavia.com/en-EU/book-a-flight/flights/search/"
    verification_date: "2026-09-17"
  - name: "CP Comboios de Portugal (Porto-Lisbon train)"
    tier: 2
    url: "https://www.cp.pt/passageiros/en"
    verification_date: "2026-09-17"
  - name: "Rede Expressos (Faro-Lisbon bus)"
    tier: 2
    url: "https://www.rede-expressos.pt"
    verification_date: "2026-09-17"
```

## Assumptions

```yaml
assumptions:
  - "All prices are indicative, based on search at verification date."
  - "Valorisation du temps de transfert (transfer_time_value) : 0 € par défaut, les heures supplémentaires (+2h45 pour OPO, +3h15 pour FAO) sont reportées."
  - "Baggage fees for low-cost carriers not included in base price; checked bag surcharge indicated."
  - "Transfer times include 45min safety buffer for airport egress."
```

## Verification Required

```yaml
verification_required:
  - "Confirm all flight prices directly on airline websites before booking."
  - "Verify CP Alfa Pendular Porto-Lisbon schedule for selected dates."
  - "Verify Rede Expressos Faro-Lisbon schedule for selected dates."
  - "Check baggage policy changes for low-cost carriers."
```

## Risks

```yaml
risks:
  - "Low-cost carrier prices fluctuate rapidly; prices may increase within hours."
  - "Porto and Faro alternatives add 3-4 hours of ground transfer time."
  - "Railway/bus strikes could disrupt alternative airport ground transfers."
  - "BVA (Beauvais) is 85km from Paris center; factor in shuttle time and cost."
  - "Late arrival in Faro past 19h30 would prevent catching the 20h00 last bus, requiring an overnight transit stay (~€70)."
```
