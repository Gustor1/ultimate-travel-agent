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
```

---

## 4. Gestion des Erreurs et Repli Automatique (*Graceful Fallback*)

En mode programmatique ou via les outils MCP :
- Si un outil est appelé avec `mode="offline"` ou `mode="mock"`, la réponse est garantie instantanée sans réseau.
- Si un outil est appelé avec `mode="live"` alors que la clé correspondante est absente, le système retourne une erreur explicite `ProviderConfigurationError` indiquant la variable manquante et suggérant le repli vers le mode offline.
- En aucun cas une indisponibilité externe ou un quota épuisé ne doit interrompre brutalement le fonctionnement de base du planificateur local.
