# Comparatif Technique des Fournisseurs de Données — `ultimate-travel-agent`

Ce document présente une comparaison objective des fournisseurs intégrés et candidats pour chaque catégorie de données de voyage.

---

## 1. Vols (Flights)

| Fournisseur | Modèle Économique | Clé Requise | Données Fournies | Avantages | Inconvénients / Limites |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **MockFlightProvider** | Gratuit / Local | Non | Horaires types, durée, cabine, escales, prix estimé | Zéro latence, 100% hors-ligne | Données statiques représentatives |
| **Amadeus Flight Offers** | Freemium (2000 req/m en test) | Oui (Client ID + Secret) | Offres de vols multi-compagnies, tarifs en direct, PNR | Standard GDS mondial, documentation complète | Configuration sandbox requise, quotas stricts |
| **AviationEdge** | Freemium limité | Oui | Horaires, routes, statuts en direct | Précision sur les mouvements d'aéroports | Moins axé sur la comparaison tarifaire |
| **Google Flights** | Scraping / Non officiel | N/A | Recherche grand public | Ergonomie connue | **Refusé** : Aucune API publique ouverte, violation des CGU de Google |

---

## 2. Trains et Transports Terrestres (Trains & Transit)

| Fournisseur | Modèle Économique | Clé Requise | Données Fournies | Avantages | Inconvénients / Limites |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **MockTrainProvider** | Gratuit / Local | Non | Liaisons TGV/Renfe, durée porte-à-porte, correspondances | Modélisation porte-à-porte avec marges d'embarquement | Données pré-calculées |
| **SNCF Open Data** | Gratuit (Compte dév) | Oui | Horaires et départs réseau ferré français | Données officielles précises sur la France | Limité géographiquement |
| **Navitia (Kisio)** | Freemium | Oui | Itinéraires multi-modaux (train, bus, métro) Europe | Excellente couverture intermodale | Quotas sur le tier communautaire |
| **GTFS Open Data** | Gratuit / Libre (ODbL) | Non | Fichiers d'horaires statiques téléchargeables | Fonctionnement 100% déconnecté | Nécessite un stockage local des jeux de données |

---

## 3. Hébergements et Avis (Accommodation & Reviews)

| Fournisseur | Usage Autorisé | Clé Requise | Partenariat Requis | Statut dans l'Architecture |
| :--- | :--- | :---: | :---: | :--- |
| **MockAccommodationProvider** | Quartiers calmes & prix indicatifs | Non | Non | Connecteur par défaut 100% hors-ligne |
| **Amadeus Hotel Search** | Recherche de catalogues et tarifs | Oui | Sandbox ouvert | Connecteur préparé (lecture seule) |
| **StayAPI (Trip.com)** | **Avis clients uniquement** | Oui | Non | Connecteur avis préparé (pas de résa) |
| **TripAdvisor v2 Content** | Notations et synthèses d'avis | Oui | Accord API | Connecteur avis préparé |
| **Booking.com Demand API** | Recherche et inventaire | Oui | ⚠️ Contrat commercial B2B | En attente de contrat partenaire |
| **Hotelbeds APItude** | Tarifs grossistes | Oui | ⚠️ Licence agence de voyage | En attente d'agrément |

---

## 4. Activités et Excursions (Activities)

| Fournisseur | Catégories Disponibles | Clé Requise | Plan B Météo Modélisé | Réservation Directe |
| :--- | :--- | :---: | :---: | :---: |
| **MockActivityProvider** | 9 catégories complètes (culture, gastronomie, nature, etc.) | Non | Oui (plan pluie + fermeture) | Non (lien officiel vers billetterie) |
| **GetYourGuide Partner** | Visites guidées, pass musées | Oui | Non (à déduire) | Non (lien d'affiliation) |
| **Viator Partner** | Excursions, excursions journée | Oui | Non (à déduire) | Non (lien d'affiliation) |
| **OpenTripMap** | Monuments, patrimoine, musées | Oui (gratuit) | Partiel (tags indoor) | Non |

---

## 5. Cartes, Distances et Trajets (Maps & Routing)

| Fournisseur | Auto-hébergeable | Clé Requise | Respect de la Vie Privée | Détection Fatigue |
| :--- | :---: | :---: | :---: | :---: |
| **MockMapsProvider** | Oui (inclus en Python) | Non | Maximale (zéro réseau) | Oui (> 4h de route alerté) |
| **OSRM (Open Source Routing)** | Oui (Docker local) | Non | Maximale | Oui |
| **OpenRouteService (ORS)** | Oui / Cloud gratuit | Oui | Élevée (serveurs universitaires Heidelberg) | Oui |
| **Nominatim (OSM Geocode)** | Oui / Cloud public | Non | Élevée (OpenStreetMap) | N/A (géocodage seul) |
| **Google Maps Platform** | Non (Cloud propriétaire) | Oui (CB requise) | Moyenne (traçage de requêtes) | Oui |

---

## 6. Météo et Climat (Weather)

| Fournisseur | Clé Requise | Gratuite Non-Commerciale | Distinction Climat vs Live | Déclenchement Plan B |
| :--- | :---: | :---: | :---: | :---: |
| **MockWeatherProvider** | Non | Oui | Oui (historique vs forecast) | Oui (> 40% pluie) |
| **Open-Meteo** | **Non** | **Oui (Open-source)** | Oui | Oui |
| **OpenWeatherMap** | Oui | Oui (One Call freemium) | Partiel | Oui |

---

## 7. Devises (Currency)

| Fournisseur | Clé Requise | Source | Horodatage du Taux | Support Taux Manuel |
| :--- | :---: | :--- | :---: | :---: |
| **MockCurrencyProvider** | Non | Table déterministe locale | Oui (`2026-09-01`) | Oui (`custom_rate`) |
| **ECB (Banque Centrale)** | Non | Flux public officiel BCE | Oui (journalier) | Oui |
