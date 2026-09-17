# Architecture Multi-Agents — `ultimate-travel-agent`

Ce document détaille l'architecture logicielle multi-agents du système `ultimate-travel-agent`, définissant la topologie d'orchestration, les responsabilités de chacun des 11 sous-agents, leurs contrats d'interface (entrées/sorties) et leurs flux de coordination.

---

## 1. Topologie Globale d'Orchestration

Le système adopte un modèle **Orchestrateur-Spécialistes avec Sas de Contrôle Qualité et d'Audit de Sécurité** (*Supervisor-Specialists with Quality Gate & Security Auditor*).

### 1.1 Schéma des Flux d'Exécution

```
                       [ Utilisateur / CLI / Web UI ]
                                     │
                             (Brief de voyage)
                                     ▼
                     ┌───────────────────────────────┐
                     │      travel-orchestrator      │
                     └───────┬───────────────▲───────┘
                             │               │
        ┌────────────────────┴───────────────┴───────────────────┐
        │                 DÉLÉGATION PARALLÈLE                   │
        ▼                             ▼                         ▼
┌────────────────────────┐   ┌──────────────────┐   ┌─────────────────────────┐
│ destination-researcher │   │transport-planner │   │accommodation-researcher │
└────────────────────────┘   └──────────────────┘   └─────────────────────────┘
        │                             │                         │
        ▼                             ▼                         ▼
┌────────────────────────┐   ┌──────────────────┐   ┌─────────────────────────┐
│    activity-curator    │   │  local-discovery │   │travel-preparation-agent │
└────────────────────────┘   └──────────────────┘   └─────────────────────────┘
        │                             │                         │
        └────────────────────┬────────┴─────────────────────────┘
                             ▼
                 ┌───────────────────────┐
                 │  itinerary-optimizer  │  (Cohérence spatio-temporelle, rythme & "anti-foule")
                 └───────────┬───────────┘
                             ▼
                 ┌───────────────────────┐
                 │     budget-analyst    │  (Chiffrage consolidé, devises & ventilation)
                 └───────────┬───────────┘
                             ▼
                 ┌───────────────────────┐
                 │   quality-controller  │  (Vérification contraintes, alertes & manques)
                 └───────────┬───────────┘
                             ▼
                 ┌───────────────────────┐
                 │   mcp-skill-auditor   │  (Audit sécurité, validation URLs, zéro fuite)
                 └───────────┬───────────┘
                             │
                             ▼ (Dossier de voyage validé)
                     [ Rapport Final Markdown ]
```

---

## 2. Définition Détaillée des 11 Sous-Agents

---

### 2.1 `travel-orchestrator` (Superviseur Général)
- **Rôle & Mission :**
  Chef d'orchestre du système. Réceptionne le brief brut de l'utilisateur, valide et normalise les paramètres, coordonne l'ordre d'exécution des agents spécialistes, résout les dépendances croisées et assemble le document final de voyage.
- **Ce qu'il reçoit (Inputs) :**
  - Prompt/formulaire utilisateur structuré : Destination(s) (pays/région/villes), dates de voyage, profil et composition des voyageurs (nombre, âges, liens), budget global ou journalier, centres d'intérêt thématiques, type d'hébergement souhaité, rythme désiré (`PACKED`, `BALANCED`, `RELAXED`), préférence d'affluence (`LOW_CROWD` / `STANDARD`).
- **Ce qu'il produit (Outputs) :**
  - Contexte global de mission (`TripMissionContext`).
  - Plan de voyage final consolidé au format Markdown structuré et complet (`TripReport`).
- **Outils & Privilèges :** Gestion du bus de messages inter-agents ; aucun appel direct à des APIs externes.

---

### 2.2 `destination-researcher` (Spécialiste Destination & Contexte)
- **Rôle & Mission :**
  Fournit la grille de lecture géographique, culturelle et contextuelle pour chaque pays, région et ville du voyage. Il rédige pour chaque ville une synthèse évocatrice ainsi qu'une anecdote historique ou culturelle marquante, formatée rigoureusement *en italique grisé*. Il identifie la période optimale de visite et les grandes règles d'accès au territoire.
- **Ce qu'il reçoit (Inputs) :**
  - Liste des villes/régions cibles, dates de voyage envisagées, centres d'intérêt dominants.
- **Ce qu'il produit (Outputs) :**
  - Fiche de destination (`DestinationProfile`) comprenant :
    - Hiérarchie géographique : Pays, Région, Ville ;
    - Descriptif culturel et anecdote sur la ville mise en forme (*italique grisé* : `*<span style="color:gray;">...</span>*`) ;
    - Période optimale de visite recommandée ;
    - Moyens d'accès principaux au territoire et spécificités géographiques.
- **Outils & Privilèges :** Accès en lecture au mock touristique local (`data/mock/destinations.json`) ou Wikivoyage en mode étendu.

---

### 2.3 `transport-planner` (Planificateur des Transports)
- **Rôle & Mission :**
  Conçoit la logistique complète de déplacement à deux échelles :
  1. **Inter-villes (macro-transit) :** Liaisons ferroviaires prioritaires ("truc de train" : Shinkansen, TGV, ICE), vols intérieurs, lignes d'autocars ou location de véhicule, temps de parcours de gare à gare et options alternatives.
  2. **Intra-urbain (micro-transit) :** Modalités de déplacement quotidien (réseau de métro, pass journaliers, marche à pied, vélos, navettes d'aéroport).
  Pour chaque trajet majeur, il fournit le lien officiel pour réserver ou acheter en ligne (sans jamais réaliser d'achat automatique).
- **Ce qu'il reçoit (Inputs) :**
  - Villes étapes ordonnées, dates, budget alloué au transport, profil des voyageurs (enfants, mobilité réduite).
- **Ce qu'il produit (Outputs) :**
  - Matrice des transferts inter-villes (`InterCityTransitPlan`) : mode de transport, gares de départ/arrivée, durée estimée, tarif moyen indicatif, lien d'achat officiel (`booking_url_official`), statut de vérification (`VERIFIED_OFFICIAL` / `ESTIMATED`).
  - Guide des mobilités locales par ville (`LocalTransitGuide`) : pass recommandés, tarifs unitaires, conseils d'usage.
- **Outils & Privilèges :** Accès au catalogue de lignes ferroviaires mock (`data/mock/transports.json`) ou connecteurs de routage OSRM.

---

### 2.4 `accommodation-researcher` (Spécialiste Hébergement)
- **Rôle & Mission :**
  Sélectionne des établissements ou types d'hébergement adaptés au profil (hôtel de charme, appartement familial, auberge conviviale, resort de luxe) et au budget. Il cible les quartiers stratégiques pour minimiser les temps de transit matin et soir.
- **Ce qu'il reçoit (Inputs) :**
  - Ville, dates de séjour, nombre de chambres/lits, budget hébergement par nuitée, typologie souhaitée.
- **Ce qu'il produit (Outputs) :**
  - Sélection de 2 à 3 options concrètes par étape (`AccommodationOption[]`) : nom indicatif, quartier recommandé, fourchette tarifaire par nuitée, atouts logistiques, lien de consultation officiel, mention explicite de réservation anticipée requise (`advance_booking_required: bool`), statut de vérification.
- **Outils & Privilèges :** Base mock d'hébergements (`data/mock/accommodations.json`) ou StayAPI/Trip.com en mode optionnel.

---

### 2.5 `activity-curator` (Curateur d'Activités & Culture)
- **Rôle & Mission :**
  Sélectionne et détaille les visites incontournables, musées, monuments et parcs naturels (landscape) en fonction des centres d'intérêt du voyageur. Pour chaque activité, il consigne l'horaire, le lieu exact, le tarif officiel indicatif, le moyen d'accès, la durée moyenne, le niveau d'affluence habituel (pour gérer la contrainte "moins de personne") et le lien officiel pour acheter le billet en ligne.
- **Ce qu'il reçoit (Inputs) :**
  - Destination, durée du séjour, intérêts thématiques (culture, nature, gastronomie, etc.), profil des voyageurs, préférence d'affluence (`LOW_CROWD` / `STANDARD`).
- **Ce qu'il produit (Outputs) :**
  - Catalogue d'activités qualifiées (`ActivityItem[]`) comprenant :
    - Nom de l'activité et descriptif synthétique ;
    - Horaires d'ouverture habituels et jours de fermeture ;
    - Lieu précis (quartier / adresse) ;
    - Tarif officiel indicatif (€/$ ou monnaie locale) ;
    - Moyen d'accès (station de métro, bus, marche) ;
    - Durée recommandée de la visite (en heures) ;
    - Statut de billetterie : `RÉSERVATION ANTICIPÉE OBLIGATOIRE` vs `WALK-IN / ACCÈS LIBRE` ;
    - Lien officiel pour acheter en ligne (`booking_url_official`) ;
    - Niveau d'affluence et créneaux creux (`crowd_level`, `off_peak_hours`) ;
    - Statut de vérification de la source (`VERIFIED_OFFICIAL` / `ESTIMATED`).
- **Outils & Privilèges :** Base mock de POIs culturels (`data/mock/activities.json`), billetteries officielles.

---

### 2.6 `local-discovery-agent` (Explorateur Local & Pépites Cachées)
- **Rôle & Mission :**
  Déniche des expériences authentiques, des points de vue panoramiques préservés de la foule ("moins de personne") et des adresses culinaires locales précises (restaurants nommés pour chaque repas : matin, midi, soir, avec leur plat signature, plutôt qu'une consigne générique). Il intègre les idées issues des plateformes de découverte (RedNote, Douyin, TikTok, blogs) après application systématique d'un filtre de réalisme.
- **Ce qu'il reçoit (Inputs) :**
  - Quartiers traversés, profil voyageur (recherche de calme ou d'immersion), régimes alimentaires, créneaux de repas.
- **Ce qu'il produit (Outputs) :**
  - Recommandations de restaurants nommés par repas (`DiningPlan`) : nom exact de l'établissement, spécialité culinaire, fourchette tarifaire indicative, quartier.
  - Sélection de spots "hors des sentiers battus" (Off-the-beaten-path) étiquetés avec avertissement de vérification terrain et mention du niveau d'affluence réduit.
- **Outils & Privilèges :** Données mock d'adresses vérifiées (`data/mock/restaurants.json`).

---

### 2.7 `budget-analyst` (Analyste Financier & Devises)
- **Rôle & Mission :**
  Quantifie financièrement chaque composante du projet. Il segmente le budget en 5 postes clés (Hébergement, Transports, Restauration, Activités, Imprévus), surveille le respect du plafond utilisateur, convertit en devise locale et calcule la moyenne de dépense journalière par personne.
- **Ce qu'il reçoit (Inputs) :**
  - Propositions tarifaires de `transport-planner`, `accommodation-researcher`, `activity-curator` et `local-discovery-agent`.
  - Budget global ou journalier cible spécifié par l'utilisateur.
- **Ce qu'il produit (Outputs) :**
  - Tableau récapitulatif du budget prévisionnel (`BudgetBreakdown`) :
    - Ventilation poste par poste (Hébergement, Transports, Repas, Activités, Imprévus) ;
    - Dépenses fixes (transports interurbains, hébergements) vs variables (repas, entrées) ;
    - Coût total estimé et coût journalier moyen par voyageur ;
    - Marge de réserve de sécurité (recommandation : 10 à 15% du budget total pour aléas) ;
    - Alertes de dépassement éventuel avec recommandations d'ajustement.
- **Outils & Privilèges :** Moteur de calcul arithmétique déterministe, table de taux de change de référence.

---

### 2.8 `travel-preparation-agent` (Spécialiste Formalités, Santé & Logistique)
- **Rôle & Mission :**
  Établit le dossier pré-voyage complet :
  - Exigences de visa (visas touristiques, exemptions, e-visas, validité résiduelle du passeport de 3 ou 6 mois) ;
  - Santé et vaccins obligatoires/recommandés ;
  - Assurance voyage requise et rapatriement ;
  - Devises locales, fonctionnement des cartes bancaires, règles de pourboires ;
  - Téléphonie mobile (cartes SIM physiques, forfaits eSIM) ;
  - Fiche de sécurité d'urgence : hôpital de référence, coordonnées consulaires/ambassades, numéros d'urgence locaux et phrases de survie dans la langue locale ;
  - Normes culturelles, étiquette et erreurs de touristes à éviter.
- **Ce qu'il reçoit (Inputs) :**
  - Nationalité du voyageur, pays de destination, dates du séjour, profil médical particulier.
- **Ce qu'il produit (Outputs) :**
  - Dossier `PreTripBriefing` complet intégrant la checklist chronologique (J-30, J-7, J-1), l'annuaire d'urgence et le guide de coutumes locales.
- **Outils & Privilèges :** Données mock administratives (`data/mock/travel_rules.json`) ou liens vers France Diplomatie / OMS.

---

### 2.9 `itinerary-optimizer` (Optimiseur d'Itinéraire & Contraintes)
- **Rôle & Mission :**
  Agence les activités et les repas dans l'ordre chronologique des journées en tenant compte de la géographie (regroupement par quartier pour minimiser les trajets), du rythme choisi (`PACKED`, `BALANCED`, `RELAXED`), des horaires réels d'ouverture, de la fatigue des voyageurs et de l'évitement des foules ("moins de personne"). Il formule également les plans de contingence (alternatives en cas de pluie ou de fermeture inopinée).
- **Ce qu'il reçoit (Inputs) :**
  - Activités candidates de `activity-curator`, adresses culinaires de `local-discovery-agent`, hébergements et transferts.
- **Ce qu'il produit (Outputs) :**
  - Déroulé jour par jour optimisé (`DailySchedule[]`) découpé en 4 créneaux : Matin, Midi (déjeuner), Après-midi, Soir (dîner & détente).
  - Temps de transition inter-activités calculés avec mode de déplacement recommandé (marche, métro, taxi) et coût estimé.
  - Plan de contingence journalier : alternative couverte en cas d'intempéries et plan B en cas de fermeture inopinée.
- **Outils & Privilèges :** Moteur de calcul de distance/routage OSRM ou matrice locale de distances.

---

### 2.10 `quality-controller` (Garant de Qualité, Réalisme & Transparence)
- **Rôle & Mission :**
  Sas d'évaluation et de validation critique du plan de voyage avant publication. Il vérifie la cohérence spatio-temporelle, le respect des plafonds budgétaires, la présence de restaurants nommés, la présence de l'anecdote de ville (*italique grisé*), l'application de la contrainte "moins de personne", et génère le rapport des données manquantes ou à vérifier.
- **Ce qu'il reçoit (Inputs) :**
  - L'ensemble du dossier de voyage pré-assemblé par `travel-orchestrator` et `itinerary-optimizer`.
- **Ce qu'il produit (Outputs) :**
  - Rapport de conformité (`QualityGateReport`) avec statut `APPROVED` ou liste d'incohérences bloquantes.
  - Section dédiée *"Informations à vérifier avant le départ"* répertoriant tous les éléments portant le statut `ESTIMATION_MOCK` ou `NON_VÉRIFIÉ_COMMUNAUTAIRE` ainsi que les champs manquants.
- **Outils & Privilèges :** Validateur de règles métier et de schémas JSON Pydantic (aucun outil externe).

---

### 2.11 `mcp-skill-auditor` (Garde-Fou de Sécurité & Confidentialité)
- **Rôle & Mission :**
  Inspecte tous les appels d'outils, liens externes et sorties de compétences pour garantir la sécurité absolue du système :
  - Empêche toute tentative d'exécution de commande shell non autorisée ;
  - Vérifie qu'aucune clé API, mot de passe ou donnée personnelle (nom complet, passeport) ne fuite dans les logs ou les exports ;
  - Valide que tous les liens d'achat en ligne (`booking_url_official`) pointent vers des domaines officiels légitimes (liste blanche de domaines autorisés) et non vers des sites de phishing ou de revente illégale ;
  - Bloque immédiatement toute tentative d'automatiser une réservation ou un paiement ;
  - Détecte d'éventuelles tentatives d'injection de prompt issues de descriptions de lieux ou de pages web externes.
- **Ce qu'il reçoit (Inputs) :**
  - Flux des requêtes/réponses d'outils MCP, prompts générés et rapport final.
- **Ce qu'il produit (Outputs) :**
  - Certification de sécurité (`SecurityAuditReport`) ou déclenchement d'un arrêt d'urgence (`SecurityException`).
- **Outils & Privilèges :** Analyseur d'expressions régulières, filtres de détection de secrets et de motifs d'injection, vérificateur de domaines HTTP.

---

## 3. Matrice d'Interaction et Dépendances

| Agent | Dépendances Amont | Livrables Fournis en Aval |
| :--- | :--- | :--- |
| `travel-orchestrator` | Entrée utilisateur | Répartition des briefs aux spécialistes |
| `destination-researcher` | `travel-orchestrator` | Hiérarchie Pays/Région/Ville & anecdotes grisées à l'`orchestrator` |
| `transport-planner` | `travel-orchestrator` | Plans de transports inter/intra et liens d'achat à `itinerary-optimizer` et `budget-analyst` |
| `accommodation-researcher` | `travel-orchestrator` | Hébergements et quartiers à `itinerary-optimizer` et `budget-analyst` |
| `activity-curator` | `travel-orchestrator` | POIs, billetterie officielle, liens d'achat et affluence à `itinerary-optimizer` et `budget-analyst` |
| `local-discovery-agent` | `activity-curator` | Pépites confidentielles ("moins de personne") et restaurants nommés à `itinerary-optimizer` |
| `travel-preparation-agent` | `destination-researcher` | Checklist administrative, sanitaire et annuaire d'urgence au dossier final |
| `itinerary-optimizer` | Activités, Hébergements, Transports | Planning journalier cohérent avec plans de secours au `quality-controller` |
| `budget-analyst` | Devis de tous les spécialistes | Bilan financier consolidé et devises au `quality-controller` |
| `quality-controller` | Tous les agents | Validation `APPROVED`, alertes d'affluence et rapport des données à vérifier |
| `mcp-skill-auditor` | Ensemble des messages et outils | Validation de sécurité, contrôle anti-fuite, validation des URLs de billetterie |
