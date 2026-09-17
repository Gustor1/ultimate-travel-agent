# Analyse des Serveurs MCP et APIs Candidates — `ultimate-travel-agent`

Ce document analyse les serveurs Model Context Protocol (MCP) et les APIs candidates identifiés dans la note brute du projet ("mcp serveur trip", "google flight ou autre équivalent", "truc de train", Bright Data, StayAPI, Composio TripAdvisor), ainsi que les alternatives ouvertes nécessaires à une implémentation robuste, sécurisée et modulaire.

---

## 1. Cadre d'Évaluation de Sécurité et de Conformité MCP

Conformément aux principes directeurs du projet :
- **Aucun composant MCP externe n'est considéré comme sûr par défaut.**
- **Principe de moindre privilège :** Les outils MCP ne doivent avoir accès qu'aux fonctions strictement nécessaires (lecture seule privilégiée, aucun accès disque racine, aucune exécution de commandes shell non contrôlées).
- **Zéro clé sensible dans Git :** Gestion stricte des variables d'environnement via `.env` non versionné et templates `.env.example`.
- **Zéro paiement/réservation autonome :** Toute action de type "checkout", "create_booking" ou "charge_card" est formellement bloquée.
- **Transparence et vérification :** Tout appel MCP ou API doit qualifier la fraîcheur et la fiabilité des données retournées (officielle, agrégée, prévisionnelle).

---

## 2. Analyse Détaillée des Candidats

### 2.1 Serveur MCP Tout-en-Un "Trip" (`mcp-server-trip`)
- **Mention dans la note :** *"mcp serveur trip ( tout que ca soit train hotel vol etc)"*
- **Description technique :** Idée d'un serveur MCP unique et monolithique regroupant l'ensemble des verticales de voyage (vols, trains, hôtels, activités, météo).
- **Utilité pour le projet :**
  - Point de contact unique pour l'orchestrateur.
- **Permissions requises :**
  - Très larges (accès réseau multiple, gestion de multiples clés d'API, requêtes hétérogènes).
- **Clé API & Coût :**
  - Variable selon les sous-services connectés.
- **Risques identifiés :**
  - *Monolithe fragile :* Si un fournisseur change ses schémas, l'ensemble du serveur échoue.
  - *Surface d'attaque élargie :* Violation du principe de responsabilité unique (SRP).
  - *Saturation de contexte :* Les définitions d'outils combinées encombrent inutilement la fenêtre de contexte du LLM.
- **Statut :** **`rejected` en tant que monolithe ; `core` en tant qu'architecture modulaire décomposée.**
- **Justification :** Nous rejetons un serveur MCP fourre-tout monolithique au profit d'outils modulaires spécialisés ou d'un serveur MCP local mock unifié mais compartimenté en modules étanches.

---

### 2.2 Google Flights & Alternatives de Recherche Aérienne
- **Mention dans la note :** *"google flight ou autre équivalent"*
- **Description technique :** Comparateurs et moteurs de recherche de liaisons aériennes, calendriers tarifaires et historiques de prix. Google Flights ne dispose pas d'API publique REST gratuite officielle (l'accès se fait via des APIs tierces comme SerpApi Google Flights Engine, Fast-Flights, ou les APIs Amadeus / Skyscanner).
- **Utilité pour le projet :**
  - Estimation des tarifs médians et durée des liaisons aériennes pour les longs trajets et voyages multi-villes.
  - Identification des aéroports de départ/arrivée optimaux et des escales.
- **Permissions requises :**
  - Requêtes HTTP sortantes vers l'agrégateur (ex: `api.amadeus.com` ou `serpapi.com`).
  - Stockage sécurisé de tokens OAuth2 / clés secrètes.
- **Clé API & Coût :**
  - **Amadeus Self-Service :** Clé requise (`AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET`). Quota gratuit en environnement de test (Sandbox), facturation à l'appel en production.
  - **SerpApi (Google Flights scraper) :** Clé requise, freemium (100 requêtes/mois gratuites, payant au-delà).
  - **Skyscanner API (via RapidAPI) :** Clé requise, modèle freemium/payant.
- **Risques identifiés :**
  - *Fluctuation tarifaire permanente :* Les prix de billets d'avion changent à la minute selon le yield management. Risque d'incohérence entre l'itinéraire généré et le prix réel constaté par le voyageur.
  - *Risque de dépendance commerciale :* Quotas stricts pouvant paralyser l'agent en cas d'utilisation intensive.
- **Statut :** **`optional` (Prévu en Phase 4 / V2).**
- **Justification :** Non indispensable pour la V1 qui se base sur des liaisons aériennes types et des fourchettes tarifaires mockées. En Phase 4, intégration via le connecteur Amadeus Sandbox ou lien direct Google Flights sans scraping intrusif.

---

### 2.3 APIs & Outils Ferroviaires ("truc de train")
- **Mention dans la note :** *"truc de train"* (SNCF Connect, Deutsche Bahn Hafas, Navitia, Trainline)
- **Description technique :** APIs et connecteurs de données ferroviaires nationales et transfrontalières pour obtenir les horaires, numéros de train, gares de correspondance et tarifs indicatifs.
- **Utilité pour le projet :**
  - Cœur de la logistique multi-villes et road-trips éco-responsables (liaisons TGV, Intercités, Shinkansen, ICE, Frecciarossa).
  - Calcul précis des temps de parcours de gare à gare.
- **Permissions requises :**
  - Requêtes HTTP vers les APIs ouvertes (ex: Navitia open data, DB Hafas / Transport.rest) ou passerelle locale.
- **Clé API & Coût :**
  - **Navitia / SNCF Open Data :** Gratuit avec token d'inscription.
  - **DB Hafas (API ouverte non officielle / transport.rest) :** Gratuit, open-source, sans clé API.
  - **Trainline Partner API :** Fermé aux particuliers, réservé aux partenaires commerciaux.
- **Risques identifiés :**
  - *Fragilité des wrappers non officiels :* Risque de rupture en cas de refonte des plateformes nationales.
  - *Couverture géographique fragmentée :* Aucun connecteur ferroviaire mondial unique n'existe ; nécessite un adaptateur par région (Europe, Japon JR, etc.).
- **Statut :** **`optional` (Phase 4 / V2) ; Mock prioritaire en V1.**
- **Justification :** Le catalogue mock local en V1 intègre les grands axes ferroviaires classiques (ex: Tokyo-Kyoto en Shinkansen, Paris-Barcelone en TGV). L'intégration Navitia / DB Hafas viendra enrichir la V2.

---

### 2.4 Bright Data MCP Server (`brightdata/brightdata-mcp`)
- **Source :** `https://github.com/brightdata/brightdata-mcp`
- **Description technique :** Serveur MCP développé par Bright Data permettant à un LLM d'effectuer du web scraping automatisé, d'interroger des moteurs de recherche (SERP API), d'extraire des données de pages Web protégées contre les robots et d'utiliser des proxys résidentiels rotatifs.
- **Utilité pour le projet :**
  - Scraping de pages touristiques officielles non dotées d'APIs publiques (ex: horaires de musées provinciaux, tarifs de bus locaux).
  - Extraction d'articles de blogs de voyage et d'adresses spécifiques.
- **Permissions requises :**
  - Accès réseau sortant complet (HTTP/HTTPS sur l'ensemble du Web).
  - Variables d'environnement pour stocker le token de zone Bright Data.
- **Clé API & Coût :**
  - **Clé API requise :** Oui (`BRIGHTDATA_API_KEY`, `ZONE_NAME`).
  - **Coût :** **Payant au volume / à la consommation (Pay-as-you-go).** Les proxys résidentiels et le Web Unlocker peuvent devenir extrêmement onéreux en cas de boucle de requêtes incontrôlée de l'agent.
- **Risques identifiés :**
  - *Risque financier :* Facturation imprévisible si l'agent effectue des centaines de crawls en boucle.
  - *Risque de sécurité / Injection de prompt :* Le scraping direct de contenu HTML non sanitisé provenant du web public peut injecter des instructions malveillantes (*indirect prompt injection*) dans le contexte du LLM.
  - *Risque légal :* Respect des conditions d'utilisation (Terms of Service) des sites tiers scrapés.
- **Statut :** **`experimental` (Éventuellement en Phase 4 sous garde-fous stricts).**
- **Justification :** Inutile pour la V1 qui fonctionne en local/mock. Ne sera activable que sous réserve d'un plafond de dépenses strict (*hard spend limit*) et d'un parseur de désinfection HTML rigoureux.

---

### 2.5 StayAPI Trip.com API (`stayapi.com/apis/tripcom`)
- **Source :** `https://stayapi.com/apis/tripcom`
- **Description technique :** API REST commerciale agissant comme passerelle (wrapper) pour interroger les disponibilités et les tarifs d'hôtels référencés sur la plateforme Trip.com.
- **Utilité pour le projet :**
  - Récupération des disponibilités hôtelières réelles par ville/quartier.
  - Comparaison des types de chambres et des grilles tarifaires par nuitée.
- **Permissions requises :**
  - Accès réseau sortant restreint au domaine `api.stayapi.com`.
  - Variable d'environnement contenant la clé API de souscription.
- **Clé API & Coût :**
  - **Clé API requise :** Oui (`STAYAPI_KEY`).
  - **Coût :** **Freemium / Payant.** Niveau gratuit très restreint (quelques dizaines d'appels par mois), puis abonnement mensuel ou coût par requête.
- **Risques identifiés :**
  - *Dépendance à un intermédiaire tiers :* StayAPI n'est pas une entité officielle de Trip.com ; risque d'interruption unilatérale de service.
  - *Monoculture de catalogue :* Ne reflète que l'inventaire Trip.com, délaissant les hébergements indépendants et gîtes locaux.
- **Statut :** **`research-needed` / `optional` (V4).**
- **Justification :** Ne doit en aucun cas être une dépendance bloquante. La V1 utilise un jeu de données mock d'hébergements locaux. En production future, des alternatives multi-fournisseurs devront être étudiées.

---

### 2.6 Composio TripAdvisor Toolkit (`composio.dev/toolkits/tripadvisor/framework/ai-sdk`)
- **Source :** `https://composio.dev/toolkits/tripadvisor/framework/ai-sdk`
- **Description technique :** Intégration managée par Composio encapsulant l'API TripAdvisor sous forme d'outils compatibles avec les frameworks d'agents et le protocole MCP.
- **Utilité pour le projet :**
  - Recherche de restaurants et d'attractions par ville avec notes, classements et volume d'avis.
  - Extraction de résumés de commentaires de voyageurs pour qualifier l'ambiance et la qualité.
- **Permissions requises :**
  - Accès réseau vers les serveurs relais de Composio ou TripAdvisor.
  - Clé API Composio et/ou clé officielle TripAdvisor Partner.
- **Clé API & Coût :**
  - **Clé API requise :** Oui (`COMPOSIO_API_KEY`).
  - **Coût :** **Freemium.** Quota gratuit mensuel limité par Composio, payant au-delà. L'API directe TripAdvisor officielle nécessite en outre un statut de partenaire d'entreprise.
- **Risques identifiés :**
  - *Intermédiation opaque :* Passer par Composio ajoute une couche d'abstraction et de latence réseau supplémentaire.
  - *Biais d'évaluation :* Risque de faux avis ou de mise en avant d'établissements sponsorisés.
- **Statut :** **`optional` (V4).**
- **Justification :** Utile pour enrichir les recommandations culinaires et d'activités avec des avis consolidés, mais non critique pour l'architecture centrale.

---

### 2.7 Serveur MCP Local Mock (`mcp-local-travel-mock`) — Composant Interne
- **Source :** Développement interne au projet `ultimate-travel-agent`.
- **Description technique :** Serveur MCP exécuté en local (sur transport stdio ou socket IPC), fournissant des données de voyage fictives mais ultra-réalistes (destinations, musées, horaires, prix officiels, hébergements, météo type, affluence) issues de fichiers JSON locaux validés.
- **Utilité pour le projet :**
  - Permet le fonctionnement autonome immédiat du projet sans aucune clé API ni connexion Internet.
  - Sert de banc d'essai pour tester les agents de manière 100% déterministe et reproductible.
- **Permissions requises :**
  - Lecture seule sur le répertoire local `data/mock/`.
  - Aucune permission réseau externe.
  - Aucune permission d'écriture système.
- **Clé API & Coût :** **Zéro clé API, 100% gratuit et open-source.**
- **Risques identifiés :**
  - *Données statiques :* Ne reflète pas les fermetures exceptionnelles en temps réel du jour J (nécessite une date de référence mockée).
- **Statut :** **`core` (Indispensable V1).**
- **Justification :** Cœur battant de la version 1.0. Garantit qu'aucun utilisateur n'est bloqué par un paywall ou une configuration complexe.

---

### 2.8 Open-Meteo API / MCP Connector
- **Source :** `https://open-meteo.com/` (Open source weather API)
- **Description technique :** Service météo mondial haute précision s'appuyant sur les modèles météorologiques nationaux (DWD, NOAA, Météo-France, ECMWF).
- **Utilité pour le projet :**
  - Fournir des prévisions de pluie, vent, ensoleillement et températures pour adapter les plannings journaliers et alimenter les plans de contingence.
- **Permissions requises :**
  - Requête HTTP GET sortante vers `api.open-meteo.com`.
- **Clé API & Coût :** **Gratuit pour usage non commercial, zéro clé API requise.**
- **Risques identifiés :**
  - Risque quasi nul. Respecter une politique de cache local pour éviter le spam de requêtes.
- **Statut :** **`optional` (Prévu dès la phase d'extension V3/V4).**
- **Justification :** Idéal pour apporter de la donnée réelle sans barrière à l'entrée ni gestion de secrets.

---

### 2.9 OpenStreetMap / OSRM Routing MCP
- **Source :** Projet OpenStreetMap / OSRM (Open Source Routing Machine).
- **Description technique :** Moteur de calcul de distance, temps de trajet à pied, à vélo ou en voiture basé sur les données libres d'OpenStreetMap.
- **Utilité pour le projet :**
  - Calculer des temps de transit réalistes entre le musée du matin et le restaurant du midi, évitant les plannings irréalisables.
- **Permissions requises :**
  - Requête HTTP vers instance publique OSRM ou conteneur Docker local.
- **Clé API & Coût :** **Gratuit, open source, zéro clé requise.**
- **Risques identifiés :**
  - Quotas d'usage sur les serveurs de démonstration publics ; nécessite un cache ou un déploiement local pour les gros volumes.
- **Statut :** **`core` pour les calculs de géodistances.**
- **Justification :** Remplace avantageusement les solutions payantes comme Google Distance Matrix sans dépendance propriétaire.

---

## 3. Tableau Récapitulatif des Statuts MCP / API

| Nom du Composant | Catégorie | Permissions | Clé API | Coût | Statut | Priorité d'Implémentation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`mcp-local-travel-mock`** | Données locales | Lecture seule locale | Aucune | Gratuit | **`core`** | **Phase 1 & Phase 3 (V1)** |
| **OSRM / OpenStreetMap** | Routage / Géo | Réseau sortant OSRM | Aucune | Gratuit | **`core`** | **Phase 3 (V1)** |
| **Open-Meteo** | Météo | Réseau sortant GET | Aucune | Gratuit | **`optional`** | **Phase 4 (V2)** |
| **Google Flights / Amadeus** | Vols | Réseau sortant API | Requise (Amadeus) | Freemium / Payant | **`optional`** | **Phase 4 (V2)** |
| **Train APIs ("truc de train")** | Ferroviaire | Réseau sortant API | Aucune (DB/Navitia) | Gratuit | **`optional`** | **Phase 4 (V2)** |
| **TripAdvisor (Composio)** | Avis & POI | Réseau externe relais | Requise | Freemium | **`optional`** | **Phase 4 (V2)** |
| **StayAPI (Trip.com)** | Hébergement | Réseau externe StayAPI| Requise | Payant | **`research-needed`** | **Phase 4 (V2)** |
| **Bright Data MCP** | Web Scraping / SERP | Réseau complet sortant | Requise | Pay-as-you-go | **`experimental`** | **Phase 4 (Sous condition)** |
| **`mcp-server-trip` (Monolithe)** | Tout-en-un | Accès non cloisonné | Multiples | Incontrôlé | **`rejected`** | **Rejeté (Anti-pattern)** |
| **Automated Booking / Payment** | Achat / Paiement | Cartes, écritures | Sensibles | Variable | **`rejected`** | **Formellement exclu (Hors périmètre)** |
