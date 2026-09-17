# Format de Données et Schémas — `ultimate-travel-agent`

Ce document décrit les structures de données JSON / YAML utilisées pour modéliser un dossier de voyage, ses composantes et son statut de vérification.

---

## 1. Niveaux de Vérification (*VerificationLevel*)

Chaque donnée concrète (transport, hôtel, activité, règle) porte un niveau de confiance explicite :

| Valeur | Définition |
| :--- | :--- |
| `official_verified` | Donnée vérifiée directement auprès d'une source officielle gouvernementale, consulaire ou d'une billetterie agréée. |
| `cross_checked` | Donnée confirmée par au moins deux sources indépendantes réputées (guides de référence, offices de tourisme). |
| `community_recommended` | Donnée largement plébiscitée par les communautés de voyageurs (forums vérifiés, retours d'expérience documentés). |
| `social_discovery_only` | Idée découverte sur les réseaux sociaux (TikTok, RedNote, Instagram, blogs personnels) nécessitant confirmation impérative. |
| `unverified` | Estimation initiale ou donnée générée n'ayant pas encore fait l'objet d'un recoupement. |
| `outdated` | Donnée historique obsolète ou dont la validité temporelle a expiré. |

---

## 2. Entités Principales

### 2.1 Voyageur (`Traveler`)
- `id`: Identifiant unique anonymisé (ex: `traveler-1`).
- `name`: Nom ou pseudonyme.
- `profile`: `solo`, `couple`, `family_with_children`, `group_friends`, `seniors`, `digital_nomad`, `quiet_seeker`.
- `pacing_preference`: `packed`, `balanced`, `relaxed`.
- `crowd_sensitivity`: `standard`, `avoid_crowds`, `extreme_quiet`.
- `dietary_restrictions`: Liste des contraintes alimentaires éventuelles.

### 2.2 Voyage (`Trip`)
- `id`: Identifiant unique du voyage.
- `title`: Titre descriptif.
- `trip_type`: `city_trip`, `road_trip`, `multi_city`, `nature_landscape`, `slow_travel`.
- `start_date` / `end_date`: Période couverte (format ISO `YYYY-MM-DD`).
- `currency`: Devise principale (ex: `EUR`, `USD`, `JPY`).
- `travelers`: Liste des profils de voyageurs.
- `budget_cap`: Plafond budgétaire total souhaité.
- `destinations`: Liste des destinations du voyage.
- `stages`: Liste ordonnée des étapes et escales (`TripStage`).
- `transports`: Liste des trajets interurbains et urbains (`TransportSegment`), gérant les coûts par voyageur ou par véhicule/groupe.
- `accommodations`: Liste des hébergements (`Accommodation`).
- `activities`: Liste des visites et loisirs programmés (`Activity`).
- `itinerary`: Découpage journalier ordonné (`DaySchedule`).
- `checklists`: Checklist avant départ et sur place (`ChecklistItem`).
- `reservations`: Formalisation des démarches de réservation manuelle (`BookingRequirement`).

### 2.3 Étape (`TripStage`)
- `id`: Identifiant unique de l'étape.
- `destination_id`: Destination rattachée.
- `order`: Ordre de séquence (1-indexé).
- `title`: Titre descriptif de l'étape.
- `arrival_date` / `departure_date`: Dates d'arrivée et de départ.
- `nights`: Nombre de nuitées passées sur cette étape.
- `notes`: Conseils d'itinéraire ou alertes.

### 2.4 Réservation (`BookingRequirement`)
- `id`: Identifiant unique.
- `category`: `transport`, `accommodation`, `activity`, `permit`, `other`.
- `title`: Intitulé de la réservation.
- `status`: `needed`, `booked`, `not_needed`.
- `mandatory`: Booléen d'obligation légale ou logistique.
- `official_booking_url`: Lien direct vers l'opérateur officiel (zéro intermédiaire non vérifié).
- `action_required`: Consigne explicite pour le voyageur.

---

## 3. Schémas JSON

Les schémas officiels JSON Schema v7 sont versionnés dans le dossier `data/schemas/` :
- `trip.schema.json`
- `traveler.schema.json`
- `destination.schema.json`
- `stage.schema.json`
- `transport.schema.json`
- `accommodation.schema.json`
- `activity.schema.json`
- `checklist.schema.json`
- `booking.schema.json`
- `budget.schema.json`
- `agent_result.schema.json`
