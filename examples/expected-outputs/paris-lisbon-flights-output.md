# Expected Output: Paris → Lisbon Flight Search (4-Pass)

## Pass 1 — Base (Reference)

```yaml
pass_1_base:
  airport: "LIS (Lisbon Humberto Delgado)"
  search_dates:
    departure: "2026-10-10"
    return: "2026-10-17"
  options:
    - airline: "easyJet (Meilleur résultat Passe 1 conforme au brief)"
      route: "CDG → LIS (direct)"
      baggage_policy: "1 bagage cabine 10kg/pers inclus + 1 valise en soute 15kg partagée (+€30)"
      cost_breakdown:
        flight_base_2pax: "€240 (2x €120)"
        checked_bag_fee: "€30 (1 valise soute 15kg)"
        flight_total_with_luggage: "€270"
        origin_access_cost: "€47 (RER B Châtelet → CDG A/R 2p)"
        ground_transfer_destination: "€0"
        overnight_stay: "€0"
        door_to_door_total: "€317"
      is_baseline_reference: true
      direct_url: "https://www.easyjet.com/en/buy/flights"
      booking_instructions: "Sélectionner Paris (CDG) → Lisbonne (LIS), 10 au 17 octobre 2026, 2 adultes, ajouter 1 bagage en soute 15kg."
      verification_date: "2026-09-17"
    - airline: "Transavia"
      route: "ORY → LIS (direct)"
      baggage_policy: "Petit sac inclus + 1 valise en soute 20kg (+€28)"
      cost_breakdown:
        flight_base_2pax: "€290 (2x €145)"
        checked_bag_fee: "€28 (1 valise soute 20kg)"
        flight_total_with_luggage: "€318"
        origin_access_cost: "€41 (Métro 14 Châtelet → Orly A/R 2p)"
        ground_transfer_destination: "€0"
        overnight_stay: "€0"
        door_to_door_total: "€359"
      direct_url: "https://www.transavia.com/en-EU/book-a-flight/flights/search/"
      booking_instructions: "Sélectionner Paris Orly (ORY) → Lisbonne (LIS), 10 au 17 octobre 2026."
      verification_date: "2026-09-17"
    - airline: "TAP Air Portugal"
      route: "CDG → LIS (direct)"
      baggage_policy: "1 bagage cabine 10kg inclus + 1 valise en soute 23kg (+€30)"
      cost_breakdown:
        flight_base_2pax: "€370 (2x €185)"
        checked_bag_fee: "€30 (1 valise soute 23kg)"
        flight_total_with_luggage: "€400"
        origin_access_cost: "€47 (RER B A/R 2p)"
        ground_transfer_destination: "€0"
        overnight_stay: "€0"
        door_to_door_total: "€447"
      direct_url: "https://www.flytap.com/en/booking/flights"
      booking_instructions: "Sélectionner Paris (CDG) → Lisbonne (LIS), 10 au 17 octobre 2026, 2 adultes."
      verification_date: "2026-09-17"
  reference_baseline:
    airline: "easyJet"
    door_to_door_total: "€317"
    rule: "Le meilleur résultat conforme au brief en Passe 1 constitue l'unique baseline REF."
```

## Pass 2 — Multi-Airport (Fixed Dates 10-17 Oct)

```yaml
pass_2_multi_airport:
  - airport: "OPO (Porto Francisco Sá Carneiro via Paris-Beauvais)"
    airline: "Ryanair"
    route: "BVA → OPO (direct)"
    baggage_policy: "Petit sac inclus + 1 valise en soute 20kg (+€35)"
    transfer_to_lisbon:
      mode: "CP Alfa Pendular train (Campanhã → Santa Apolónia)"
      duration: "2h45"
      cost_2pax: "€50"
      operator_url: "https://www.cp.pt/passageiros/en"
      last_departure: "20h32 (vol atterrit à 17h15, battement de 3h17 suffisant)"
    cost_breakdown:
      flight_base_2pax: "€130 (2x €65)"
      checked_bag_fee: "€35 (1 valise soute 20kg)"
      origin_access_cost: "€68 (Navette Paris Porte Maillot → BVA A/R 2p: 4x €16.90)"
      ground_transfer_destination: "€50 (Train CP promo A/R 2p)"
      overnight_stay: "€0 (correspondance le jour même confirmée)"
      total_door_to_door: "€283"
    door_to_door_total_2pax: "€283"
    saving_vs_pass1: "-€34 vs REF easyJet €317 (-11%)"
    retained: false
    reason: "Économie de €34 (11%) inférieure au seuil requis de ≥ 20% ou ≥ €50. Le coût d'accès à Beauvais (€68 navette) et la soute (€35) annulent le gain du vol low-cost pour +4h de trajet."
    direct_url: "https://www.ryanair.com/gb/en/trip/flights/select"
    booking_instructions: "Sélectionner Paris Beauvais (BVA) → Porto (OPO), 10 au 17 octobre 2026, ajouter 1 bagage en soute 20kg."
    verification_date: "2026-09-17"
  - airport: "FAO (Faro via Paris-Orly)"
    airline: "easyJet"
    route: "ORY → FAO (direct)"
    baggage_policy: "Petit sac sous siège inclus + 1 valise en soute 15kg (+€30)"
    flight_price_per_person: "€75"
    transfer_to_lisbon:
      mode: "Autocar Rede Expressos (Faro Terminal → Lisboa Sete Rios)"
      duration: "3h15"
      cost_2pax: "€40"
      operator_url: "https://www.rede-expressos.pt"
      last_departure: "20h00 (vol atterrit à 16h40, battement de 3h20 suffisant)"
    cost_breakdown:
      flight_base_2pax: "€150 (2x €75)"
      checked_bag_fee: "€30 (1 valise soute 15kg)"
      origin_access_cost: "€41 (Métro 14 Châtelet → Orly A/R 2p)"
      ground_transfer_destination: "€40 (Autocar A/R 2p)"
      overnight_stay: "€0 (correspondance le jour même confirmée)"
      total_door_to_door: "€261"
    door_to_door_total_2pax: "€261"
    saving_vs_pass1: "-€56 vs REF easyJet €317 (-18%)"
    retained: true
    reason: "Économie nette de €56 (≥ €50 requis) avec correspondance terrestre directe le jour même."
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner Paris Orly (ORY) → Faro (FAO), 10 au 17 octobre 2026, ajouter 1 valise soute 15kg."
    verification_date: "2026-09-17"
```

## Pass 3 — Flexible Dates (Principal Airport LIS)

```yaml
pass_3_flexible_dates:
  - shift: "Aller +2j (12 oct), Retour identique (17 oct)"
    airline: "easyJet"
    route: "CDG → LIS (direct)"
    baggage_policy: "1 valise en soute 15kg incluse (+€30)"
    cost_breakdown:
      flight_base_2pax: "€150 (2x €75)"
      checked_bag_fee: "€30 (1 valise soute)"
      origin_access_cost: "€47 (RER B A/R 2p)"
      ground_transfer_destination: "€0"
      overnight_stay: "€0"
      total_door_to_door: "€227"
    door_to_door_total_2pax: "€227"
    saving_vs_pass1: "-€90 vs REF easyJet €317 (-28%)"
    retained: true
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner Paris CDG → LIS, 12 au 17 octobre 2026, ajouter 1 valise soute."
    verification_date: "2026-09-17"
  - shift: "Aller identique (10 oct), Retour -1j (16 oct)"
    airline: "Transavia"
    route: "ORY → LIS (direct)"
    baggage_policy: "1 valise en soute 20kg incluse (+€28)"
    cost_breakdown:
      flight_base_2pax: "€220 (2x €110)"
      checked_bag_fee: "€28 (1 valise soute)"
      origin_access_cost: "€41 (Métro 14 A/R 2p)"
      ground_transfer_destination: "€0"
      overnight_stay: "€0"
      total_door_to_door: "€289"
    door_to_door_total_2pax: "€289"
    saving_vs_pass1: "-€28 vs REF easyJet €317 (-9%)"
    retained: false
    reason: "Économie de €28 inférieure au seuil de €50."
    direct_url: "https://www.transavia.com/en-EU/book-a-flight/flights/search/"
    booking_instructions: "Sélectionner Paris Orly (ORY) → LIS, 10 au 16 octobre 2026."
    verification_date: "2026-09-17"
  - shift: "Aller +3j (13 oct), Retour -2j (15 oct)"
    airline: "easyJet"
    route: "CDG → LIS (direct)"
    baggage_policy: "1 valise en soute 15kg incluse (+€30)"
    cost_breakdown:
      flight_base_2pax: "€130 (2x €65)"
      checked_bag_fee: "€30 (1 valise soute)"
      origin_access_cost: "€47 (RER B A/R 2p)"
      ground_transfer_destination: "€0"
      overnight_stay: "€0"
      total_door_to_door: "€207"
    door_to_door_total_2pax: "€207"
    saving_vs_pass1: "-€110 vs REF easyJet €317 (-35%)"
    retained: true
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner Paris CDG → LIS, 13 au 15 octobre 2026."
    verification_date: "2026-09-17"
```

## Pass 4 — Combined (Flexible Dates × Alternative Airports)

```yaml
pass_4_combined:
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
      total_door_to_door: "€211"
    door_to_door_total_2pax: "€211"
    saving_vs_pass1: "-€106 vs REF easyJet €317 (-33%)"
    retained: true
    direct_url: "https://www.easyjet.com/en/buy/flights"
    booking_instructions: "Sélectionner ORY → FAO, 12 au 16 octobre 2026, ajouter 1 valise soute."
    verification_date: "2026-09-17"
  - airport: "OPO (Porto via Paris-Beauvais)"
    shift: "Aller +2j (12 oct), Retour identique (17 oct)"
    airline: "Ryanair"
    baggage_policy: "1 valise en soute 20kg incluse (+€35)"
    cost_breakdown:
      flight_base_2pax: "€80 (2x €40)"
      checked_bag_fee: "€35 (1 valise soute)"
      origin_access_cost: "€68 (Navette BVA A/R 2p)"
      ground_transfer_destination: "€50 (Train CP promo A/R 2p)"
      overnight_stay: "€0"
      total_door_to_door: "€233"
    door_to_door_total_2pax: "€233"
    saving_vs_pass1: "-€84 vs REF easyJet €317 (-26%)"
    retained: true
    reason: "Économie de €84 (26%) qui compense cette fois l'accès à Beauvais grâce au tarif midweek à €40."
    direct_url: "https://www.ryanair.com/gb/en/trip/flights/select"
    booking_instructions: "Sélectionner BVA → OPO, 12 au 17 octobre 2026, ajouter 1 valise soute."
    verification_date: "2026-09-17"
```

## Synthesis Table

| Rang | Aéroport | Dates effectives | Décalage | Escales | Bagages | Prix vol (2p) | Accès origine (2p) | Transfert dest. (2p) | Coût total P2P | Économie vs P1 REF | Lien direct & Instructions | Date vérif. |
|------|----------|------------------|----------|---------|---------|---------------|-------------------|----------------------|----------------|---------------------|-----------------------------|-------------|
| REF  | LIS (CDG→LIS) | 10-17 oct | ±0 | direct | Soute incluse | €270 | €47 (RER B) | — | €317 | — | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 1    | LIS (CDG→LIS) | 13-15 oct | Aller +3j, Retour -2j | direct | Soute incluse | €160 | €47 (RER B) | — | €207 | -€110 (-35%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 2    | FAO (ORY→FAO) | 12-16 oct | Aller +2j, Retour -1j | direct | Soute incluse | €130 | €41 (Métro 14) | €40 (Autocar) | €211 | -€106 (-33%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 3    | LIS (CDG→LIS) | 12-17 oct | Aller +2j | direct | Soute incluse | €180 | €47 (RER B) | — | €227 | -€90 (-28%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |
| 4    | OPO (BVA→OPO) | 12-17 oct | Aller +2j | direct | Soute incluse | €115 | €68 (Navette BVA) | €50 (CP train) | €233 | -€84 (-26%) | [Ryanair](https://www.ryanair.com/gb/en/trip/flights/select) | 2026-09-17 |
| 5    | FAO (ORY→FAO) | 10-17 oct | ±0 | direct | Soute incluse | €180 | €41 (Métro 14) | €40 (Autocar) | €261 | -€56 (-18%) | [easyJet](https://www.easyjet.com/en/buy/flights) | 2026-09-17 |

## Source Log

```yaml
source_log:
  - name: "easyJet Official Flight Booking Engine"
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
  - name: "Aéroport Paris-Beauvais Navette Officielle"
    tier: 2
    url: "https://www.aeroportparisbeauvais.com/acces-et-parking/navette-aeroport-paris-porte-maillot"
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
  - "L'option Passe 1 de référence (REF) retenue est la meilleure offre directe easyJet conforme au brief (€317 tout compris avec soute et RER B)."
  - "Accès à l'aéroport d'origine inclus pour toutes les options afin de comparer à équipement égal (RER B €47 pour CDG, Métro 14 €41 pour Orly, navette €68 pour Beauvais)."
  - "Frais de soute demandés par le brief intégrés pour chaque option (+€30 easyJet, +€35 Ryanair, +€28 Transavia)."
  - "Valorisation forfaitaire du temps de transfert (transfer_time_value) : 0 € par défaut, mais la durée additionnelle (+4h via Beauvais/Porto, +3h15 via Faro) est mentionnée."
```

## Verification Required

```yaml
verification_required:
  - "Confirmer le tarif en direct sur les sites officiels des compagnies aériennes avant toute décision."
  - "Réserver la navette Paris-Beauvais et le train CP en ligne à l'avance pour garantir les tarifs promo."
```

## Risks

```yaml
risks:
  - "L'accès à Beauvais (BVA) coûte €68 A/R pour 2 personnes et ajoute 1h15 de trajet, annulant la rentabilité de l'option Porto en Passe 2."
  - "Correspondances à Faro : veiller à atterrir avant 19h00 pour garantir l'autocar de 20h00 vers Lisbonne."
```
