# Feuille de Route du Projet (Roadmap) — `ultimate-travel-agent`

Ce document présente le plan de développement structuré en 7 phases successives, de la recherche initiale jusqu'à la publication open-source mondiale du projet `ultimate-travel-agent`.

---

## Vue d'Ensemble des Phases

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   PHASE 0    │ ──> │   PHASE 1    │ ──> │   PHASE 2    │ ──> │   PHASE 3    │
│ Recherche &  │     │ Structure du │     │ 11 Agents &  │     │  MCP Local   │
│    Audit     │     │    Dépôt     │     │ Prompts XML  │     │  (Mock Data) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                       │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
│   PHASE 6    │ <── │   PHASE 5    │ <── │   PHASE 4    │ <───────────┘
│ Publication  │     │  Interface   │     │ Intégrations │
│  Open Source │     │     Web      │     │  Externes    │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## Phase 0 : Recherche et Audit (Phase Complétée)

### Objectifs :
- Analyser la note brute initiale et consolider les exigences fonctionnelles.
- Qualifier l'ensemble des sources, des APIs (Google Flights, liaisons ferroviaires, hébergements) et des skills candidates.
- Définir l'architecture logicielle des 11 sous-agents avec leurs contrats d'entrée/sortie précis.
- Concevoir le socle minimal autonome V1 fonctionnant 100% hors-ligne sur des données locales fictives, sans réservation automatique ni manipulation de données sensibles.

### Livrables Réalisés :
- `research/raw-notes.md` : Sauvegarde brute intégrale et exacte mot pour mot.
- `research/requirements.md` : Périmètre V1/V2/Hors-périmètre, styles de voyage (*landscape, city, multi-villes*), profils et dimension "moins de personne".
- `research/source-matrix.md` : Matrice catégorisée des sources avec niveaux de confiance, protocoles de recoupement et cartographie des URLs.
- `research/candidate-skills.md` : Analyse critique des skills candidates, de la saturation de contexte et de la détection d'hallucinations.
- `research/candidate-mcps.md` : Audit des MCPs/APIs (serveur trip, Google Flights, trains, StayAPI, Composio, Bright Data, mock local, OSRM, Open-Meteo) avec statuts précis.
- `research/agent-architecture.md` : Spécification complète des 11 sous-agents, contrats de données et drapeaux de vérification.
- `research/architecture-v1.md` : Architecture technique du socle minimal V1 avec double mode d'exécution (déterministe local vs LLM).
- `research/roadmap.md` : Plan de réalisation séquentiel en 7 phases.

### Critères de Passage Validés :
- [x] Spécifications documentées et cohérentes sans ambiguïté.
- [x] Règles de sécurité formellement sanctuarisées (zéro paiement, zéro fuite, priorité aux sources officielles).

---

## Phase 1 : Structure du Dépôt et Données Fictives

### Objectifs :
- Initialiser le squelette de code Python propre avec gestionnaire de dépendances moderne (`pyproject.toml`).
- Construire le jeu de données mock complet dans `data/mock/` pour couvrir 3 scénarios types (Multi-villes Tokyo/Kyoto, City-trip Barcelone, Séjour Nature Fjords de Norvège).
- Établir les modèles Pydantic v2 stricts pour l'ensemble des flux de données inter-agents.

### Tâches Concrètes :
1. Mise en place de `pyproject.toml` (dépendances : `pydantic>=2.0`, `typer`, `rich`, `jinja2`, `pytest`).
2. Configuration de l'outillage de qualité de code : `ruff` (linter & formateur), `mypy` (typage statique strict).
3. Création des jeux de données JSON réalistes dans `data/mock/` :
   - `destinations.json` (pays, régions, villes, périodes optimales, anecdotes grisées) ;
   - `transports.json` (liaisons ferroviaires TGV/Shinkansen, métros urbains, liens de billetterie officielle) ;
   - `accommodations.json` (hôtels, appartements, auberges par quartier et budget) ;
   - `activities.json` (musées, parcs, durées, billetterie anticipée vs libre, créneaux creux "moins de personne", URLs officielles) ;
   - `restaurants.json` (adresses nommées avec spécialités et prix par repas) ;
   - `travel_rules.json` (visas, passeports, vaccins, numéros et contacts d'urgence).
4. Écriture des modèles de données Pydantic (`src/ultimate_travel_agent/models/`).

### Critères de Passage :
- 100% des fichiers JSON de mock validés automatiquement par les schémas Pydantic.
- Suite de tests de validation de données passante avec `pytest`.

---

## Phase 2 : Implémentation des 11 Sous-Agents et Prompts Modulaires

### Objectifs :
- Développer la logique métier de chacun des 11 sous-agents sous forme de classes modulaires.
- Assurer le double mode de fonctionnement : exécution algorithmique déterministe locale (sans LLM) et support des prompts modulaires XML pour LLM.
- Mettre en place le moteur d'optimisation d'itinéraire et le sas de contrôle qualité/sécurité.

### Tâches Concrètes :
1. Implémentation des classes d'agents dans `src/ultimate_travel_agent/agents/` :
   - `travel_orchestrator` : Ingestion du brief, coordination et synthèse.
   - `destination_researcher` : Contexte géographique et anecdotes en italique grisé.
   - `transport_planner` : Macro-transit (trains/vols) et micro-transit avec liens officiels.
   - `accommodation_researcher` : Sélection stratégique par quartier et budget.
   - `activity_curator` : Sélection d'activités, gestion d'affluence et billetterie.
   - `local_discovery_agent` : Bonnes tables nommées et pépites hors sentiers battus.
   - `budget_analyst` : Découpage financier, devises et marge de sécurité (10-15%).
   - `travel_preparation_agent` : Checklist visas, santé et contacts d'urgence.
   - `itinerary_optimizer` : Agencement horaire, regroupement géographique et plans météo de secours.
   - `quality_controller` : Contrôle de réalisme et recensement des informations à vérifier.
   - `mcp_skill_auditor` : Vérification de la liste blanche d'URLs, filtres anti-fuites et anti-injections.
2. Écriture des gabarits de rendu Jinja2 pour la sortie Markdown propre.
3. Tests unitaires et d'intégration avec `pytest` pour chaque agent.

### Critères de Passage :
- Génération déterministe d'un plan de voyage complet de 5 jours en moins de 2 secondes en local, avec 100% de tests unitaires passants.

---

## Phase 3 : Serveur MCP Local et Banc d'Essai Déconnecté

### Objectifs :
- Encapsuler les fournisseurs de données mock dans un serveur MCP local standardisé (transport stdio).
- Permettre à un client MCP externe (ex: Claude Desktop, Cursor, ou tout agent compatible) d'interroger les outils de voyage en mode déconnecté.

### Tâches Concrètes :
1. Développement d'un serveur MCP léger avec le SDK Python officiel `mcp`.
2. Exposition des outils MCP sécurisés en lecture seule :
   - `search_destinations(city, country)`
   - `get_intercity_transports(origin, destination)`
   - `get_activities(city, category, crowd_preference, indoor_only)`
   - `get_dining_recommendations(city, neighborhood, meal_type)`
   - `get_travel_safety_and_rules(origin_country, destination_country)`
3. Intégration du moteur OSRM local pour les temps de marche et de transport.
4. Validation de sécurité des outils par le `mcp-skill-auditor`.

### Critères de Passage :
- Le serveur MCP local est reconnu et utilisable par un client MCP standard sans aucun accès Internet.

---

## Phase 4 : Intégrations Externes Optionnelles (APIs & MCPs Distants)

### Objectifs :
- Développer des connecteurs optionnels pour interroger des données réelles en ligne.
- Assurer un repli automatique et transparent (*graceful fallback*) vers les données locales en cas d'absence de clé ou de panne réseau.

### Tâches Concrètes :
1. Connecteur **Open-Meteo** (prévisions météo réelles gratuites sans clé API).
2. Connecteur **OpenStreetMap / Nominatim** (géocodage et calcul d'itinéraires en temps réel).
3. Connecteur optionnel **Amadeus Sandbox** (consultation de vols réels).
4. Connecteur optionnel **DB Hafas / Navitia** (horaires réels de trains européens).
5. Connecteur optionnel **TripAdvisor via Composio** (enrichissement d'avis avec clé utilisateur).
6. Gestion sécurisée des clés via variables d'environnement `.env` non versionnées.

### Critères de Passage :
- L'application s'exécute avec fluidité avec ou sans les clés externes configurées, sans jamais bloquer l'utilisateur.

---

## Phase 5 : Interface Utilisateur Web et Visualisation Cartographique

### Objectifs :
- Déployer une interface graphique interactive en complément de la ligne de commande CLI.
- Intégrer une visualisation sur carte interactive des étapes et trajets journaliers.

### Tâches Concrètes :
1. Interface frontend moderne (Streamlit ou FastAPI + React/Vite).
2. Cartographie interactive des étapes avec OpenStreetMap / Leaflet.
3. Export multi-formats : Markdown propre, fichier PDF prêt à imprimer, et calendrier standard `.ics`.
4. Mode hors-ligne PWA pour consultation sur smartphone en cours de voyage.

### Critères de Passage :
- Génération d'un voyage complet et consultation cartographique en moins de 3 clics par un utilisateur profane.

---

## Phase 6 : Publication Open Source et Gouvernance Communautaire

### Objectifs :
- Publier le dépôt sous licence open-source permissive (MIT ou Apache 2.0).
- Établir une gouvernance claire et accueillir les contributions communautaires.

### Tâches Concrètes :
1. Rédaction de la documentation d'accueil : `README.md` (démo visuelle, tutoriel de démarrage en 2 minutes), `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`.
2. Configuration des GitHub Actions CI/CD : linting Ruff, typage Mypy, matrice de tests sur Linux, macOS et Windows.
3. Création de templates d'issues et de pull requests.
4. Publication du package sur PyPI et diffusion auprès des communautés (Hacker News, Reddit r/LocalLLaMA, Discord MCP).

### Critères de Passage :
- Score de couverture de tests supérieur à 85% et pipeline CI au vert sur tous les systèmes d'exploitation supportés.
