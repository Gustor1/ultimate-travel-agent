# Interface Web Locale — `ultimate-travel-agent`

L'interface web locale d'**Ultimate Travel Agent** permet de configurer, tester, valider et visualiser des dossiers de voyage complets sans passer obligatoirement par la ligne de commande.

Elle respecte scrupuleusement la philosophie du projet :
- **100% Local-First** : tourne en local sur votre machine (`http://127.0.0.1:8000`).
- **Zéro fuite de données** : aucune donnée personnelle n'est collectée, stockée sur un cloud ou transmise à des tiers.
- **Zéro clé API obligatoire** : fonctionne immédiatement à partir de données et modèles locaux vérifiables.
- **Zéro achat automatique** : fournit des liens officiels directs vers les billetteries des transporteurs et monuments sans jamais déclencher de paiement ou de réservation automatisée.
- **Stack ultra-légère** : propulsée par Python, FastAPI, Uvicorn et du HTML5 / CSS3 / JavaScript pur (sans Node.js, sans React, sans base de données externe).

---

## 1. Démarrage Rapide

### Option A : Via la CLI
```bash
python -m ultimate_travel_agent.cli serve --port 8000
```

### Option B : Via le module Web
```bash
python -m ultimate_travel_agent.web --port 8000
```

Ouvrez ensuite votre navigateur sur :
```text
http://127.0.0.1:8000
```

---

## 2. Fonctionnalités de l'Interface

L'interface est structurée en 8 vues accessibles par onglets :

### 1. 📊 Vue d'Ensemble & Validation
- **Statistiques clés** : Durée (jours/nuits), nombre de voyageurs, activités recensées, budget prévisionnel consolidé.
- **Rapport de cohérence** : Détection instantanée des anomalies (dates incohérentes, nuits sans hébergement, identifiants orphelins).
- **Audit de preuve** : Répartition transparente des données en **Données Confirmées**, **Estimations & Découvertes**, et **Données Non Vérifiées**.

### 2. 🗺️ Étapes & Itinéraire Jour par Jour
- **Étapes du voyage** : Escales géographiques successives avec dates d'arrivée/départ et niveau de vérification.
- **Planning chronologique** : Déroulement heure par heure, temps de visite, temps de transport et temps de repas dédié.
- **Fiches activités V1.1** : Fiche détaillée par activité avec anecdote locale, quartier, créneau horaire optimal, stratégie anti-foule, accessibilité PMR, alternative mauvais temps et alternative en cas de fermeture inopinée.

### 3. 🚆 Comparateur d'Itinéraires Inter-Villes
- **Options multi-modales** : Comparaison entre train, vol, bus, voiture, ferry ou transports publics.
- **Indicateurs comparatifs** : Temps porte-à-porte, nombre de correspondances, coût estimé, indice de confort (1 à 5 étoiles) et empreinte carbone (kg CO2).
- **Moteur de recommandation multi-profils** : Recommandations ciblées selon 7 critères :
  - `cheapest` : Moins cher
  - `fastest` : Plus rapide
  - `fewest_transfers` : Moins de correspondances
  - `most_comfortable` : Plus grand confort
  - `most_eco_friendly` : Empreinte carbone minimale
  - `relaxed` : Adapté à un rythme détendu (faible correspondance, confort élevé)
  - `packed` : Optimisé pour maximiser le temps sur place

### 4. 💰 Budget & Réservations
- **Consolidation financière déterministe** : Dépenses directes + réserve de sécurité paramétrable (défaut 12% pour city-trip, 15% pour road-trip).
- **Ventilation catégorielle** : Transport, Hébergement, Activités, Repas, Imprévus.
- **Checklist de réservations manuelles** : Liste exhaustive des billets et nuitées à réserver manuellement avec liens officiels directs.

### 5. 🤖 Pipeline Multi-Agents (9 Étapes)
Visualisation en direct du travail déterministe des agents spécialisés :
1. *Destination research* (`destination-researcher`)
2. *Transport planning* (`transport-planner`)
3. *Accommodation research* (`accommodation-researcher`)
4. *Activity curation* (`activity-curator`)
5. *Local discovery* (`local-discovery-agent`)
6. *Travel preparation* (`travel-preparation-agent`)
7. *Budget analysis* (`budget-analyst`)
8. *Itinerary optimization* (`itinerary-optimizer`)
9. *Quality control* (`quality-controller` & `mcp-skill-auditor`)

Pour chaque étape, affichage complet du statut (`COMPLETE`, `PARTIAL`, `BLOCKED`), résumé narratif, hypothèses retenues, informations manquantes et risques signalés.

### 6. 🛡️ Plans B & Trousse de Préparation
- **Checklist avant départ** : Passeports, assurance rapatriement, opposition bancaire, cartes hors-ligne, adaptation vestimentaire.
- **Documents à vérifier** : Formalités consulaires (ESTA, ETA, visa, CEAM) accompagnées de la mention explicite *« Requires official source verification. »*.
- **Plan B météo** : Solutions d'abris et replis culturels intérieurs identifiés jour par jour.
- **Plan B fermeture** : Mesures de secours en cas de grève ou fermeture inopinée d'un monument.
- **Fiche d'urgence générique** : Rappels des protocoles d'alerte sans fabrication de numéros ou d'hôpitaux fictifs.

### 7. ✏️ Configurer un Nouveau Voyage
Formulaire de génération locale permettant de renseigner :
- Destination et pays
- Dates de début et de fin
- Nombre et profil des voyageurs (`solo`, `couple`, `family_with_children`, `group_friends`, etc.)
- Plafond budgétaire indicatif et devise
- Style d'hébergement (`hotel`, `apartment`, `guesthouse`, `hostel`)
- Rythme souhaité (`packed`, `balanced`, `relaxed`)
- Préférence d'affluence (`low-crowd`, `mixed`, `popular`)
- Contraintes diététiques ou d'accessibilité

### 8. 📄 Export Markdown
- Synthèse d'un clic de l'intégralité du dossier au format Markdown prêt pour impression, archivage ou partage.
- Bouton de copie instantanée dans le presse-papier.

---

## 3. Endpoints de l'API REST Locale

L'application FastAPI expose également une API JSON documentée sur `/docs` (Swagger UI) :

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Vérification de santé et rappel du mode hors-ligne |
| `GET` | `/api/trips` | Liste des voyages d'exemple disponibles |
| `GET` | `/api/examples/{name}` | Récupère le JSON d'un exemple (`city-trip` ou `road-trip`) |
| `POST` | `/api/trips/create` | Génère un dossier local complet à partir des paramètres |
| `POST` | `/api/trips/validate` | Analyse la cohérence, les alertes et les niveaux de preuve |
| `POST` | `/api/trips/budget` | Calcule le budget poste par poste avec réserve de sécurité |
| `POST` | `/api/trips/plan` | Exécute les 5 vagues et extrait les 9 étapes multi-agents |
| `POST` | `/api/trips/contingency` | Génère les plans B, checklists et la fiche d'urgence |
| `POST` | `/api/trips/routes/evaluate` | Évalue les options de trajet selon les 7 préférences |
| `POST` | `/api/trips/export` | Rendu complet du dossier en Markdown |
