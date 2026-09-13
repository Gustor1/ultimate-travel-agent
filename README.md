# Ultimate Travel Agent 🌍✈️

> **A generic, privacy-first, local-first multi-agent travel planning system generating verified, realistic, day-by-day itineraries with budget estimation and zero required external accounts.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Architecture: Local-First](https://img.shields.io/badge/Architecture-Local--First-green.svg)](docs/offline-mode.md)

---

## Qu'est-ce que Ultimate Travel Agent ? (En bref)

**Ultimate Travel Agent** est un système open source conçu pour aider n'importe qui à planifier un voyage complet et réaliste, sans risquer ses données personnelles et sans dépendre d'abonnements cloud ou de clés d'API payantes.

Contrairement aux chatbots conventionnels qui hallucinent des horaires, inventent des prix ou poussent vers des liens sponsorisés, ce système :
1. **Modélise fidèlement la réalité** : Regroupement géographique des visites, temps de trajet porte-à-porte, pauses déjeuner respectées, alternatives en cas de pluie ou de fermeture.
2. **Fonctionne 100% hors-ligne par défaut** : Zéro compte requis, zéro fuite de données, reproductibilité totale.
3. **Sécurise vos démarches** : **Ne réserve et ne paye jamais automatiquement**. Il fournit des liens officiels directs vers les billetteries réelles des monuments et compagnies de transport.
4. **Offre 3 interfaces** : Une interface web locale intuitive (FastAPI), une CLI puissante et un serveur MCP compatible Claude Desktop / Cursor.

---

## Concepts Clés & Différenciation

Pour bien comprendre l'architecture du projet :

- **Skills** : Des instructions et directives réutilisables (`SKILL.md`) installables dans tout projet IA compatible Antigravity (planification, vérification de sources, validation budgétaire, sécurité, orchestration, audit MCP).
- **Sous-agents** : Les rôles d'IA spécialisés internes coordonnés en vagues DAG pour accomplir la synthèse du voyage de bout en bout.
- **MCP local** : Le serveur Model Context Protocol exécuté sur la machine locale via le transport `stdio`.
- **MCP distant** : Le serveur HTTP Streamable déployé en ligne (Cloud Run, Railway, Render, Fly.io, Docker), connectable à distance depuis n'importe quel IDE ou agent compatible MCP.
- **Provider** : Une connexion optionnelle côté serveur vers une source de données externe (vols, trains, hôtels, avis, activités, cartes, météo, devises), toujours protégée par un repli déterministe hors-ligne.

---

## Mode Hors-Ligne & Garantie de Non-Paiement

> ⚠️ **Avertissement produit réglementaire :**  
> ```text
> Offline local planning mode:
> No live availability, price, opening-hour or booking verification.
> ```

- **Zéro transaction financière** : Le système n'a aucun accès bancaire et ne déclenche aucun paiement direct.
- **Zéro inventaire en direct** : Les disponibilités réelles de sièges ou de chambres d'hôtel doivent être vérifiées sur les portails officiels avant départ.
- **Zéro fabrication d'urgence** : Les numéros d'urgence et coordonnées diplomatiques portent la mention légale *« Requires official source verification. »*.

---

## Le Rôle des 11 Sous-Agents Spécialisés

Pour garantir une rigueur absolue et éviter l'amplification d'erreurs, le système coordonne 11 agents ordonnancés en 5 vagues rigides, couvrant 9 étapes métier transparentes :

```text
Wave 1 (Parallel Exploration)
  ├── 1. destination-researcher       Geographic context & quiet travel periods
  ├── 2. transport-planner            Door-to-door transit & official booking links
  ├── 3. accommodation-researcher     Strategic neighborhood curation (quiet areas)
  ├── 4. activity-curator             26-dimension activity modeling & crowd avoidance
  ├── 5. local-discovery-agent        Authentic culinary gems (flagged for manual verification)
  └── 6. travel-preparation-agent     Passports, health, visas, and pre-departure checklists

Wave 2 (Budget Consolidation)
  └── 7. budget-analyst               Itemized multi-currency budget & safety buffer (+10-15%)

Wave 3 (Itinerary Optimization)
  └── 8. itinerary-optimizer          Day-by-day scheduling with geographic clustering & weather backup

Wave 4 (Quality & Safety Gate)
  ├── 9. quality-controller           Coherence checks, pacing fatigue alerts & proof audit
  └── mcp-skill-auditor               URL allowlist inspection & prompt injection defense

Wave 5 (Synthesis)
  └── travel-orchestrator             Final trip dossier compilation & Markdown export
```

---

## Installation Rapide

### Prérequis
- Python 3.10 ou supérieur
- Git

```bash
git clone https://github.com/Gustor1/ultimate-travel-agent.git
cd ultimate-travel-agent

# Création et activation de l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate

# Installation du package avec dépendances Web et MCP
pip install -e ".[dev,mcp,web]"
```

### Lancer la suite de tests
```bash
pytest
```

---

## Les 3 Façons d'Utiliser le Système

### 1. Interface Web Locale (Recommandé) 🌐

Lancez l'application locale légère avec FastAPI et ouvrez votre navigateur sur `http://127.0.0.1:8000` :

```bash
python -m ultimate_travel_agent.cli serve --port 8000
# ou directement :
python -m ultimate_travel_agent.web --port 8000
```

Dans l'interface, vous pouvez :
- Charger les exemples de référence en 1 clic (City-trip Barcelone ou Road-trip Islande).
- Renseigner vos critères (destination, dates, nombre de voyageurs, style d'hébergement, rythme, affluence).
- Visualiser les étapes, le planning jour par jour et les fiches activités enrichies.
- Comparer des options d'itinéraires inter-villes selon 7 préférences (`cheapest`, `fastest`, `eco`, etc.).
- Inspecter la ventilation budgétaire et les alertes de surcoût.
- Suivre les 9 étapes du pipeline multi-agents avec leurs hypothèses et niveaux de preuve.
- Consulter les plans B (intempéries, fermetures) et la fiche d'urgence générique.
- Exporter ou copier le dossier en Markdown.

Voir la documentation dédiée : [docs/web-interface.md](docs/web-interface.md).

---

### 2. Ligne de Commande (CLI) 💻

```bash
# Valider la cohérence et l'intégrité d'un voyage JSON
python -m ultimate_travel_agent.cli validate examples/city-trip/trip.json

# Calculer le budget prévisionnel consolidé avec marge de sécurité
python -m ultimate_travel_agent.cli budget examples/city-trip/trip.json

# Exécuter l'orchestration multi-agents en 5 vagues
python -m ultimate_travel_agent.cli plan examples/city-trip/trip.json

# Exporter le dossier complet de voyage en Markdown
python -m ultimate_travel_agent.cli export examples/city-trip/trip.json --output reports/barcelone.md

# Lancer la démo scriptée complète
python examples/demo_run.py
```

---

### 3. Serveur MCP Local (Model Context Protocol) 🔌

Le système inclut un serveur MCP standard stdio (version **1.2.0**) exposant **21 outils en lecture seule** pour Claude Desktop, Cursor ou tout client MCP :

```bash
python -m ultimate_travel_agent.mcp.server
```

Configuration Claude Desktop (`mcp-config.json`) :
```json
{
  "mcpServers": {
    "ultimate-travel-agent": {
      "command": "python",
      "args": ["-m", "ultimate_travel_agent.mcp.server"]
    }
  }
}
```

**21 Outils disponibles :**
- **Planification & Vérification (V1.0 / V1.1) :** `list_trips`, `get_trip`, `validate_trip`, `get_itinerary`, `validate_itinerary`, `calculate_budget`, `list_booking_requirements`, `export_trip_summary`, `get_inter_city_routes`, `get_contingency_dossier`.
- **Hub d'Intégrations & Consultation Voyage (V1.2) :** `list_integration_providers`, `get_provider_status`, `search_flight_options`, `search_train_options`, `search_accommodation_options`, `search_hotel_reviews`, `search_activity_options`, `get_route_options`, `get_weather_outlook`, `convert_currency`, `search_travel_sources`.

---

## Exemples Référents Inclus

### 🏙️ Exemple City-Trip : Barcelone Culturelle (3 Jours)
- Fichier : [`examples/city-trip/trip.json`](examples/city-trip/trip.json)
- Style : Découverte culturelle et gastronomique pour 2 personnes.
- Spécificités : Billet horodaté Sagrada Família matinal (09h00), Park Güell en fin d'après-midi, hébergement boutique calme à Gràcia, trajets en TGV Paris-Barcelone, alternatives en cas de pluie.

### 🚗 Exemple Road-Trip : Sud de l'Islande (5 Jours)
- Fichier : [`examples/road-trip/trip.json`](examples/road-trip/trip.json)
- Style : Itinérance nature & paysages en véhicule 4x4 (chutes de Skógafoss, plage de Reynisfjara, lagon de Jökulsárlón).
- Spécificités : Distinction du coût véhicule vs passagers, réserve de sécurité à 15% pour variations de carburant/météo, consignes de sécurité sur les vagues traîtresses et l'état des routes (`road.is`).

---

## Hub d'Intégrations Voyage V1.2 (Provider Hub)

Le projet propose une architecture modulaire unifiée dans `src/ultimate_travel_agent/integrations/` organisée autour d'un `ProviderRegistry` et de modèles typés (Pydantic v2).

### 1. Modes de Fonctionnement

Le système supporte 3 modes d'exécution distincts :
- **`offline`** : Données locales déterministes, temps d'accès instantané, zéro appel réseau, parfait pour les tests et la planification déconnectée.
- **`mock`** : Fixtures enrichies et simulations réalistes avec délais plausibles, couverture de cas limites et formats identiques aux APIs réelles.
- **`live`** : Interrogation d'APIs tierces réelles en lecture seule. **Activé uniquement si les identifiants nécessaires sont configurés.** En cas d'erreur réseau ou d'absence de clé, le système applique un repli gracieux automatique (*graceful fallback*) vers le mock sans interruption.

### 2. Procédure d'Installation : Sans Clé vs Avec Clés Optionnelles

- **Installation standard sans clé (100% fonctionnelle, zéro configuration) :**
  ```bash
  pip install -e ".[dev,mcp,web]"
  ```
  Toutes les fonctionnalités (CLI, Web FastAPI, MCP Server 21 outils, tests unitaires) fonctionnent immédiatement sans aucune clé d'API.

- **Configuration optionnelle avec clés réelles :**
  Copiez le gabarit sécurisé d'environnement :
  ```bash
  cp .env.example .env
  ```
  Puis renseignez uniquement les clés que vous souhaitez activer (par exemple `AMADEUS_CLIENT_ID` et `AMADEUS_CLIENT_SECRET`). Les clés non renseignées conservent leur mode mock / offline par défaut.

### 3. Garanties de Confidentialité & Absence d'Achat Automatique

- 🚫 **Zéro Achat / Zéro Réservation Automatique :** Le système n'a aucun accès aux cartes bancaires, aucun token de paiement et aucune fonction d'écriture transactionnelle. Il ne clique pas, ne remplit pas de formulaires de paiement et ne réserve rien. Il fournit systématiquement des liens officiels directs vers les billetteries des opérateurs.
- 🛡️ **Zéro Partage de PII (Données Personnelles) :** Aucun nom, prénom, courriel, passeport ou donnée privée de voyageur n'est envoyé aux adaptateurs externes. Les requêtes sont anonymisées et portent uniquement sur des critères généraux (ville de départ, destination, dates, nombre d'adultes).
- 🔒 **Secrets Protégés :** Le fichier `.env.example` ne contient aucun secret par défaut, et `.gitignore` exclut tous les masques `.env*` pour éviter toute fuite accidentelle vers un dépôt public.

### 4. Tableau Récapitulatif des Fournisseurs

| Fournisseur | Domaine / Usage | Clé API requise | Mode supporté | Statut actuel |
| :--- | :--- | :--- | :--- | :--- |
| **MockFlightProvider** | Vols (itinéraires, tarifs indicatifs, bagages) | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **AmadeusFlightProvider** | Vols réels (GDS Amadeus for Developers) | `AMADEUS_CLIENT_ID` / `SECRET` | `live`, `mock` | 🟡 Préparé (Stub prêt, validation requise) |
| **AviationEdgeFlightProvider** | Horaires & statuts de vol | `AVIATION_EDGE_API_KEY` | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **Google Flights** | Comparaison de vols | N/A (Aucune API publique) | Aucun | ❌ **Rejeté** (Scraping interdit & instable) |
| **MockTrainProvider** | Trains (temps de trajet porte-à-porte, TGV/TER) | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **SNCFTrainProvider** | Trains France / TGV InOui / TER | `SNCF_API_KEY` | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **NavitiaTrainProvider** | Réseaux de transports publics européens | `NAVITIA_API_KEY` | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **MockAccommodationProvider** | Hôtels (quartiers calmes, boutique-hôtels) | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **AmadeusHotelProvider** | Inventaire hôtelier et tarifs indicatifs | `AMADEUS_CLIENT_ID` / `SECRET` | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **BookingProvider** | Consultation hébergements | Partenariat Affiliate | `live`, `mock` | 🟡 Préparé (Stub consultation uniquement) |
| **MockReviewProvider** | Avis et sentiment voyageurs agrégés | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **StayAPIReviewProvider** | Sentiments et notes d'hôtels vérifiés | `STAYAPI_KEY` | `live`, `mock` | 🟡 Préparé (Strictement lecture/avis) |
| **TripadvisorReviewProvider** | Notations et avis de réputation | `TRIPADVISOR_API_KEY` | `live`, `mock` | 🟡 Préparé (Strictement lecture/avis) |
| **MockActivityProvider** | Activités (26 dimensions, créneaux, replis pluie) | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **GetYourGuideActivityProvider** | Visites et excursions culturelles | Partenariat GYG | `live`, `mock` | 🟡 Préparé (Stub consultation uniquement) |
| **ViatorActivityProvider** | Activités et circuits | Partenariat Viator | `live`, `mock` | 🟡 Préparé (Stub consultation uniquement) |
| **OpenTripMapActivityProvider** | POIs culturels et monuments ouverts | Clé gratuite OpenTripMap | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **MockMapsProvider** | Distances, temps de trajet, matrices d'étapes | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **OSRMProvider** | Routage routier open source (OpenStreetMap) | Aucune (Serveur public/auto-hébergé) | `live`, `mock` | 🟡 Préparé (Prêt pour auto-hébergement) |
| **OpenRouteServiceProvider** | Isochrones et routage multi-modal | `OPENROUTESERVICE_API_KEY` | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **NominatimProvider** | Géocodage d'adresses OpenStreetMap | Aucune (Respect de l'User-Agent) | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **GoogleMapsRoutesProvider** | Matrices de distance Google Maps | `GOOGLE_MAPS_API_KEY` | `live`, `mock` | 🟡 Préparé (Stub consultation uniquement) |
| **MockWeatherProvider** | Météo, indices climatiques, déclencheur plan B | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **OpenMeteoProvider** | Prévisions météo sans clé (Open Data) | Aucune | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **OpenWeatherMapProvider** | Prévisions et alertes météo | `OPENWEATHERMAP_API_KEY` | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **MockCurrencyProvider** | Devises, conversion avec date de référence | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **ECBCurrencyProvider** | Taux officiels Banque Centrale Européenne | Aucune (Flux XML public) | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **MockGuideProvider** | Contexte local, anecdotes, sécurité | Aucune | `offline`, `mock` | ✅ Intégré & Actif par défaut |
| **WikivoyageProvider** | Données de voyage libres et participatives | Aucune (API MediaWiki) | `live`, `mock` | 🟡 Préparé (Stub prêt) |
| **SocialDiscoveryProvider** | Pépites émergentes (TikTok/IG) — Non vérifiées | Aucune | `offline`, `mock` | ✅ Intégré & Tagué `social_discovery_only` |

---

## Niveaux de Vérification des Données

Chaque donnée porte un niveau de preuve transparent :
- 🟢 `official_verified` : Certifié auprès d'un portail gouvernemental, consulaire ou de la billetterie officielle directe.
- 🔵 `cross_checked` : Confirmé par au moins deux guides ou sources réputées indépendantes.
- 🔷 `community_recommended` : Recommandé par consensus de communautés de voyageurs expérimentés.
- 🟣 `social_discovery_only` : Issu des réseaux sociaux (TikTok, Instagram) — nécessite une vérification manuelle des horaires et prix réels.
- 🟡 `unverified` : Estimation préliminaire non vérifiée.
- 🔴 `outdated` : Donnée antérieure à une modification de grille tarifaire ou d'horaires.

Voir [docs/data-verification.md](docs/data-verification.md) pour les règles d'audit.

---

## Use Ultimate Travel Agent in another project

Ultimate Travel Agent can be seamlessly plugged into any external AI agent workspace (Antigravity, Claude Code, Cursor, Windsurf):

### 1. Install Travel Skills
Copy the 6 travel planning, safety, budgeting, and verification skills into your target project:
```bash
# Using CLI
ultimate-travel-agent install-skills --target ../my-project

# Or using the portable python script (zero dependencies)
python packages/travel-skills/install.py --target ../my-project
```

### 2. Configure Local MCP Server (Stdio)
Add to your client configuration (e.g. `~/.antigravity/mcp_config.json`):
```json
{
  "mcpServers": {
    "ultimate-travel-agent-local": {
      "command": "python",
      "args": ["-m", "ultimate_travel_agent.mcp.server"]
    }
  }
}
```

### 3. Configure Remote MCP Server (HTTPS Streamable HTTP)
Connect to your remote deployed instance (Railway, Render, Fly.io, Cloud Run):
```json
{
  "mcpServers": {
    "ultimate-travel-agent-remote": {
      "url": "https://YOUR-TRAVEL-MCP-DOMAIN/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TRAVEL_MCP_API_KEY"
      }
    }
  }
}
```

### 4. Example Travel Query
Ask your AI assistant:
> "Plan a 4-day trip to Barcelona. Query `search_flight_options` from Paris, find lodging in quiet neighborhoods with `search_accommodation_options`, and calculate total expenditure with `calculate_budget` using a 12% buffer."

### 5. Data Limitations in Offline/Mock Modes
- All results in `offline` or `mock` mode are simulated or heuristic approximations.
- Fares and hotel prices must be re-checked manually on the official portal links provided.
- Zero automated bookings or financial transactions will ever be executed.

### 6. Activating Live Providers
To activate real-time API integrations on your deployed server:
1. Set server environment variables (e.g. `AMADEUS_CLIENT_ID`, `SNCF_API_KEY`, `OPENROUTESERVICE_API_KEY`).
2. Select active providers: `TRAVEL_PROVIDER_FLIGHTS=amadeus`, `TRAVEL_PROVIDER_WEATHER=open_meteo`.
3. Query tools with `mode="live"`. If required credentials are missing, the server safely fails closed with `ProviderConfigurationError`.

---

## Documentation Complète

### Phase 9 — Remote MCP & Distribution Pack
- [Audit de Transition Phase 9 (Remote MCP & Skills)](docs/phase-9-remote-mcp-audit.md)
- [Guide de Connexion Trans-Projets](docs/connect-from-any-project.md)
- [Pack de Skills Réutilisables](docs/reusable-skills.md)
- [Sécurité du MCP Distant](docs/remote-mcp-security.md)
- [Guide d'Authentification MCP](docs/authentication.md)
- [Architecture de Limitation de Débit](docs/rate-limiting.md)
- [Guide de Déploiement des Fournisseurs](docs/provider-deployment-guide.md)
- [Matrice de Statut des Fournisseurs](docs/provider-status.md)
- [Manifestes de Déploiement Cloud (Railway, Render, Cloud Run, Fly)](deployment/README.md)
- [Package Travel Skills](packages/travel-skills/README.md)

### Architecture & Base Locale
- [Architecture Technique & Hub d'Intégrations](docs/architecture.md)
- [Audit des Intégrations Réelles V1.2](docs/v1.2-live-integrations-audit.md)
- [Configuration des Fournisseurs & Clés](docs/provider-configuration.md)
- [Politique de Données en Direct & Fallback](docs/live-data-policy.md)
- [Comparatif des Fournisseurs de Voyage](docs/provider-comparison.md)
- [Confidentialité, Flux de Données & Zéro-PII](docs/privacy-and-data-flow.md)
- [Guide de Demande d'Identifiants](docs/credentials-request.md)
- [Audit Produit V1.1](docs/v1.1-product-audit.md)
- [Interface Web Locale](docs/web-interface.md)
- [Mode Hors-Ligne & Garanties](docs/offline-mode.md)
- [Modèle de Preuve & Niveaux de Vérification](docs/data-verification.md)
- [Flux Multi-Agents en 5 Vagues](docs/travel-workflow.md)
- [Limitations Connues](docs/known-limitations.md)
- [Prochaines Étapes](docs/next-steps.md)
- [Suivi d'Avancement](docs/progress.md)
- [Registre des Décisions d'Architecture (ADR)](docs/decisions.md)

---

## Licence

Ce projet est distribué sous la [Licence MIT](LICENSE). Vous êtes libre de l'utiliser, le modifier et le distribuer.
