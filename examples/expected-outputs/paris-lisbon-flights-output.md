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
      price_per_person: "€185"
      total_2pax: "€370"
      direct_url: "https://www.flytap.com/en/booking"
      verification_date: "2026-09-17"
    - airline: "Transavia"
      route: "ORY → LIS (direct)"
      price_per_person: "€145"
      total_2pax: "€290"
      direct_url: "https://www.transavia.com"
      verification_date: "2026-09-17"
    - airline: "easyJet"
      route: "CDG → LIS (direct)"
      price_per_person: "€120"
      total_2pax: "€240"
      direct_url: "https://www.easyjet.com/en"
      verification_date: "2026-09-17"
  reference_best_price: "€240 (2 pax, easyJet)"
```

## Pass 2 — Multi-Airport (Fixed Dates 10-17 Oct)

```yaml
pass_2_multi_airport:
  - airport: "OPO (Porto Francisco Sá Carneiro)"
    airline: "Ryanair"
    route: "BVA → OPO (direct)"
    flight_price_per_person: "€65"
    flight_total_2pax: "€130"
    transfer_to_lisbon:
      mode: "CP Alfa Pendular train"
      duration: "2h45"
      cost_per_person: "€25"
      cost_2pax: "€50"
      operator_url: "https://www.cp.pt/passageiros/en"
    door_to_door_total_2pax: "€180"
    saving_vs_pass1: "-€60 (-25%)"
    retained: true
    reason: "Saving ≥ 20% threshold met (25%)"
    direct_url: "https://www.ryanair.com/gb/en"
    verification_date: "2026-09-17"
  - airport: "FAO (Faro)"
    airline: "easyJet"
    route: "ORY → FAO (direct)"
    flight_price_per_person: "€75"
    flight_total_2pax: "€150"
    transfer_to_lisbon:
      mode: "Rede Expressos bus"
      duration: "3h15"
      cost_per_person: "€20"
      cost_2pax: "€40"
      operator_url: "https://www.rede-expressos.pt"
    door_to_door_total_2pax: "€190"
    saving_vs_pass1: "-€50 (-21%)"
    retained: true
    reason: "Saving ≥ 20% threshold met (21%)"
    direct_url: "https://www.easyjet.com/en"
    verification_date: "2026-09-17"
```

## Pass 3 — Flexible Dates (Principal Airport LIS)

```yaml
pass_3_flexible_dates:
  - shift: "Aller +2j (12 oct), Retour identique (17 oct)"
    airline: "easyJet"
    price_per_person: "€95"
    total_2pax: "€190"
    saving_vs_pass1: "-€50/2pax vs best P1"
    direct_url: "https://www.easyjet.com/en"
    verification_date: "2026-09-17"
  - shift: "Aller identique (10 oct), Retour -1j (16 oct)"
    airline: "Transavia"
    price_per_person: "€110"
    total_2pax: "€220"
    saving_vs_pass1: "-€70/2pax vs TAP P1"
    direct_url: "https://www.transavia.com"
    verification_date: "2026-09-17"
  - shift: "Aller +3j (13 oct), Retour -2j (15 oct)"
    airline: "easyJet"
    price_per_person: "€80"
    total_2pax: "€160"
    saving_vs_pass1: "-€80/2pax vs best P1"
    direct_url: "https://www.easyjet.com/en"
    verification_date: "2026-09-17"
```

## Pass 4 — Combined (Flexible Dates × Alternative Airports)

```yaml
pass_4_combined:
  - airport: "OPO"
    shift: "Aller +2j (12 oct), Retour identique (17 oct)"
    airline: "Ryanair"
    flight_price_2pax: "€100"
    transfer_2pax: "€50"
    door_to_door_total_2pax: "€150"
    saving_vs_pass1: "-€90 (-38%)"
    direct_url: "https://www.ryanair.com/gb/en"
    verification_date: "2026-09-17"
  - airport: "FAO"
    shift: "Aller +2j (12 oct), Retour -1j (16 oct)"
    airline: "easyJet"
    flight_price_2pax: "€110"
    transfer_2pax: "€40"
    door_to_door_total_2pax: "€150"
    saving_vs_pass1: "-€90 (-38%)"
    direct_url: "https://www.easyjet.com/en"
    verification_date: "2026-09-17"
```

## Synthesis Table

| Rang | Aéroport | Dates effectives | Décalage | Escales | Prix vol (2p) | Transfert (2p) | Coût total P2P | Économie vs P1 | Lien direct | Date vérif. |
|------|----------|------------------|----------|---------|---------------|----------------|-----------------|----------------|-------------|-------------|
| REF  | LIS (CDG→LIS) | 10-17 oct | ±0 | direct | €240 | — | €240 | — | [easyJet](https://www.easyjet.com/en) | 2026-09-17 |
| 1    | OPO (BVA→OPO) | 12-17 oct | Aller +2j | direct | €100 | €50 (CP train) | €150 | -€90 (-38%) | [Ryanair](https://www.ryanair.com/gb/en) | 2026-09-17 |
| 2    | FAO (ORY→FAO) | 12-16 oct | Aller +2j, Retour -1j | direct | €110 | €40 (bus) | €150 | -€90 (-38%) | [easyJet](https://www.easyjet.com/en) | 2026-09-17 |
| 3    | LIS (CDG→LIS) | 13-15 oct | Aller +3j, Retour -2j | direct | €160 | — | €160 | -€80 (-33%) | [easyJet](https://www.easyjet.com/en) | 2026-09-17 |
| 4    | OPO (BVA→OPO) | 10-17 oct | ±0 | direct | €130 | €50 (CP train) | €180 | -€60 (-25%) | [Ryanair](https://www.ryanair.com/gb/en) | 2026-09-17 |
| 5    | FAO (ORY→FAO) | 10-17 oct | ±0 | direct | €150 | €40 (bus) | €190 | -€50 (-21%) | [easyJet](https://www.easyjet.com/en) | 2026-09-17 |
| 6    | LIS (CDG→LIS) | 12-17 oct | Aller +2j | direct | €190 | — | €190 | -€50 (-21%) | [easyJet](https://www.easyjet.com/en) | 2026-09-17 |

## Source Log

```yaml
source_log:
  - name: "TAP Air Portugal Official Booking"
    tier: 2
    url: "https://www.flytap.com"
    verification_date: "2026-09-17"
  - name: "easyJet Official Booking"
    tier: 2
    url: "https://www.easyjet.com"
    verification_date: "2026-09-17"
  - name: "Ryanair Official Booking"
    tier: 2
    url: "https://www.ryanair.com"
    verification_date: "2026-09-17"
  - name: "Transavia Official Booking"
    tier: 2
    url: "https://www.transavia.com"
    verification_date: "2026-09-17"
  - name: "CP Comboios de Portugal (Porto-Lisbon train)"
    tier: 2
    url: "https://www.cp.pt"
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
  - "Baggage fees for low-cost carriers not included in base price; checked bag surcharge may apply."
  - "Transfer times include 30min buffer for connection at alternative airports."
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
```
