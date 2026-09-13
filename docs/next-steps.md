# Prochaines Étapes — `ultimate-travel-agent`

Ce document liste l'état des livrables de la version V1.2 et les pistes d'évolution future prioritaires pour une future version V1.3.

---

## 1. État Actuel : Phase 10 — Keyless Public Data Integrations Réalisée & Validée

Toutes les étapes de la Phase 10 sont achevées et testées à 100% hors-ligne :
- [x] **Audit de Faisabilité Sans Clé** : `docs/phase-10-keyless-providers-audit.md` (Open-Meteo, BCE/ECB, Wikivoyage, Nominatim, OSRM ; exclusion stricte des APIs commerciales).
- [x] **Client HTTP & Rate Limiting Défensif** : `src/ultimate_travel_agent/integrations/http_client.py` (`KeylessHttpClient`, enforcement HTTPS-only, User-Agent identifié, mutex par domaine et mutex de processus Nominatim 1 req/s, cache TTL 3 statuts `hit`/`miss`/`stale`).
- [x] **Providers Données Ouvertes Live** :
  - `OpenMeteoProvider` : météo 7 jours, géocodage, évaluation risque pluie (>= 40% ou >= 2mm) et alternatives indoor.
  - `ECBCurrencyProvider` : cours de référence officiels de la Banque Centrale Européenne et avertissement frais bancaires (+1.5% à 3.5%).
  - `WikivoyageProvider` : extraits MediaWiki, synthèse culturelle et conseils non-autoritaires sous CC BY-SA 4.0.
  - `NominatimProvider` : géocodage OSM limité à 1 req/s avec mutex strict (désactivé par défaut).
  - `OSRMProvider` : routage routier expérimental sans SLA avec alertes fatigue (> 4h de conduite, désactivé par défaut).
- [x] **Outils MCP Dédiés** : 9 nouveaux outils MCP (`geocode_destination`, `get_weather_forecast`, `get_weather_activity_advice`, `get_exchange_rates`, `convert_currency_live`, `search_wikivoyage_destination`, `get_wikivoyage_summary`, `get_limited_route_options`, `get_keyless_provider_status`).
- [x] **Sous-Agents & Skills Enrichis** : Prise en compte de la météo dans `activity-curator`, des frais bancaires dans `budget-analyst`, du statut communautaire Wikivoyage dans `destination-researcher`, et vérification des sources ouvertes dans `quality-controller`.
- [x] **Interface Web FastAPI** : Nouveaux endpoints REST, onglet interactif « Données Ouvertes Live », et footer d'attribution légale Open-Meteo / ECB / Wikivoyage / OpenStreetMap.
- [x] **Documentation & Conformité Légale** : `docs/keyless-live-providers.md`, `docs/open-data-attribution.md`, `docs/provider-rate-limits.md`, `docs/keyless-provider-limitations.md`.
- [x] **Suite de Tests Validée** : 156 tests unitaires passants à 100% hors-ligne (zéro appel réseau en CI).

---

## 2. Pistes d'Évolution Prioritaires pour une Future Version (Phase 11+)

Pour continuer d'enrichir le produit de façon progressive et sécurisée :

1. **Phase 11 — Free Tier Authenticated Providers (avec clés utilisateur gratuites)** :
   - Intégrer les APIs nécessitant un compte gratuit sans carte bancaire : OpenTripMap, OpenRouteService, Navitia / SNCF Open Data, OpenWeatherMap free tier.
   - Isolation des secrets par variables d'environnement utilisateur locales (`.env`).

2. **Génération de Fichiers de Calendrier `.ics` et Cartes Hors-Ligne `.geojson`** :
   - Exporter l'itinéraire jour par jour sous forme d'événements de calendrier universels `.ics` (avec rappels d'embarquement et créneaux coupe-file).
   - Générer un fichier `.geojson` téléchargeable importable directement dans Organic Maps / OsmAnd pour une navigation cartographique 100% hors-ligne.

3. **Génération de Dossier PDF Stylisé Imprimable** :
   - Rendu HTML-vers-PDF (ou typographie print CSS) pour imprimer un carnet de voyage physique complet en format livret de poche (fiches d'urgence, billets, plans B, horaires).
