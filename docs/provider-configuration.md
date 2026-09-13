# Guide de Configuration des Fournisseurs d'Intégration — `ultimate-travel-agent`

Ce document détaille le paramétrage des fournisseurs de données de voyage intégrés dans le **Provider Hub** de la version `v1.2`.

---

## 1. Principes Fondamentaux

1. **Fonctionnement Hors-Ligne par Défaut (`TRAVEL_AGENT_MODE=offline`)** :
   - Zéro compte externe requis.
   - Zéro clé API requise.
   - Tous les modules basculent de manière transparente et déterministe sur des simulateurs locaux typés.
2. **Sanctuarisation Zéro Achat / Zéro Réservation** :
   - Aucun connecteur ne réalise de transaction financière, de prélèvement bancaire ou de création de réservation automatisée.
   - Les liens fournis sont des adresses directes vers les portails officiels des prestataires (`official_booking_url`).
3. **Minimisation des Données** :
   - Aucune coordonnée personnelle, identité ou numéro de pièce d'identité n'est manipulé ou transmis aux prestataires.

---

## 2. Les 3 Modes d'Exécution

Le système et ses connecteurs supportent 3 modes d'exécution :

| Mode | Variable `TRAVEL_AGENT_MODE` | Comportement | Clés API requises |
| :--- | :--- | :--- | :--- |
| **`offline`** | `offline` (défaut) | Données locales déterministes, zéro appel réseau sortant. | Aucune |
| **`mock`** | `mock` | Données de simulation enrichies reproduisant les formats exacts des fournisseurs cibles. | Aucune |
| **`live`** | `live` | Requêtes directes vers les APIs partenaires. Si la clé est absente, lève `ProviderConfigurationError`. | Oui (selon le provider) |

---

## 3. Variables d'Environnement et Fichier `.env`

Pour activer optionnellement un fournisseur en mode direct :
1. Copiez le gabarit `.env.example` vers `.env` à la racine :
   ```bash
   cp .env.example .env
   ```
2. Renseignez uniquement les identifiants souhaités.
3. Ne commitez jamais votre fichier `.env`. Le fichier `.gitignore` bloque toute variante (`.env`, `.env.*`, `*.env`).

### Récapitulatif des Variables

```text
# Mode général
TRAVEL_AGENT_MODE=offline
LOG_LEVEL=INFO

# Recherche de vols
AMADEUS_CLIENT_ID=
AMADEUS_CLIENT_SECRET=
AVIATION_EDGE_API_KEY=

# Réseau ferroviaire & transports terrestres
SNCF_API_KEY=
NAVITIA_API_KEY=

# Hébergements & Avis
STAYAPI_API_KEY=
TRIPADVISOR_API_KEY=
BOOKING_API_KEY=

# Activités & Visites
GETYOURGUIDE_API_KEY=
VIATOR_API_KEY=
OPENTRIPMAP_API_KEY=

# Cartes, Distances et Itinéraires
GOOGLE_MAPS_API_KEY=
ORS_API_KEY=
OSRM_BACKEND_URL=http://localhost:5000

# Météo
OPENWEATHER_API_KEY=
OPEN_METEO_URL=https://api.open-meteo.com/v1/forecast

# Serveur MCP
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8765

# Fournisseurs Publics Sans Clé (Phase 10 — Keyless Public Data)
TRAVEL_MCP_ENABLE_KEYLESS_LIVE_PROVIDERS=false
TRAVEL_MCP_ENABLE_OPEN_METEO=true
TRAVEL_MCP_ENABLE_ECB=true
TRAVEL_MCP_ENABLE_WIKIVOYAGE=true
TRAVEL_MCP_ENABLE_NOMINATIM=false
TRAVEL_MCP_ENABLE_OSRM=false
TRAVEL_MCP_HTTP_USER_AGENT=UltimateTravelAgent/1.0 (https://github.com/Gustor1/ultimate-travel-agent)
TRAVEL_HTTP_TIMEOUT=5.0
```

---

## 4. Fournisseurs Publics Sans Clé (Phase 10)

La Phase 10 intègre des sources ouvertes ne nécessitant aucune clé API ni compte développeur :

| Fournisseur | Catégorie | Statut par défaut | Règle de débit | Cache local | Attribution obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo** | Météo & Géocodage | **Activé** si keyless live activé | 5 req/s max | 30 min | "Weather data by Open-Meteo.com under CC BY 4.0" |
| **BCE / ECB** | Taux de change | **Activé** si keyless live activé | 2 req/s max | 12h | "Source: European Central Bank (ECB) euro reference exchange rates" |
| **Wikivoyage** | Guides éditoriaux | **Activé** si keyless live activé | 3 req/s max | 24h | "Text from Wikivoyage under CC BY-SA 4.0" |
| **Nominatim** | Géocodage OSM | **Désactivé** (mode limité) | **1 req/s absolu** | 7 jours | "Data © OpenStreetMap contributors, ODbL 1.0" |
| **OSRM Démo** | Routage routier | **Désactivé** (mode expérimental) | 1 req/s max | 2h | "Routing © Project OSRM / OpenStreetMap contributors" |

### Précautions d'Usage
1. **Désactivation par défaut de Nominatim et OSRM** : Ces services publics reposent sur des infrastructures mutualisées sans SLA. Dans un serveur MCP distant public, ils doivent rester désactivés (`false`) pour éviter tout bannissement d'IP ou instabilité.
2. **Attribution légale** : Toute réponse issue de ces providers renvoie obligatoirement le champ `attribution` et `source_url`.
3. **Météo et Données communautaires** : L'agent qualité (`quality-controller`) interdit de qualifier de "garantie" une prévision météorologique ou un contenu communautaire Wikivoyage.

---

## 5. Gestion des Erreurs et Repli Automatique (*Graceful Fallback*)

En mode programmatique ou via les outils MCP :
- Si un outil est appelé avec `mode="offline"` ou `mode="mock"`, la réponse est garantie instantanée sans réseau.
- Si un outil est appelé avec `mode="live"` alors que la clé ou le service n'est pas activé, le système retourne une erreur explicite `ProviderConfigurationError` indiquant la variable d'activation requise et suggérant le repli vers le mode offline.
- En cas d'erreur 429 (débit dépassé) ou 5xx réseau, le client HTTP renvoie les données expirées en cache (`cache_status: stale`) ou bascule sur le simulateur typé local.
- En aucun cas une indisponibilité externe ou un quota épuisé ne doit interrompre brutalement le fonctionnement de base du planificateur local.

