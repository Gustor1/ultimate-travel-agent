# Flux de Travail et Orchestration Multi-Agents — `ultimate-travel-agent`

Ce document détaille le flux d'exécution séquentiel qui transforme les critères initiaux d'un utilisateur en un dossier de voyage exhaustif, réaliste et sécurisé.

---

## 1. Vue d'Ensemble du Flux en 5 Vagues

Pour éviter les dérives et les amplifications d'erreurs fréquentes dans les boucles d'agents autonomes, l'ordonnancement est organisé en un **graphe acyclique dirigé (DAG) linéaire à 5 vagues synchrones** :

```text
Entrée Utilisateur (Destination, Dates, Profil, Budget, Rythme, Affluence)
   │
   ▼
[ Vague 1 : Exploration Parallèle ]
   ├── 1. Destination research      (Profil climatique, saisonnalité, créneaux calmes)
   ├── 2. Transport planning        (Liaisons macro/micro, temps porte-à-porte, billetteries)
   ├── 3. Accommodation research    (Quartiers calmes, hôtels authentiques, critères d'isolation)
   ├── 4. Activity curation         (Visites majeures, créneaux anti-foule, alternatives)
   ├── 5. Local discovery           (Comptoirs du terroir, adresses culinaires locales)
   └── 6. Travel preparation        (Checklist avant départ, formalités d'entrée, vaccins)
   │
   ▼ [Barrière Synchrone 1]
[ Vague 2 : Consolidation Budgétaire ]
   └── 7. Budget analysis           (Coûts passagers vs véhicule, marge de sécurité 10-15%)
   │
   ▼ [Barrière Synchrone 2]
[ Vague 3 : Ordonnancement Chronologique ]
   └── 8. Itinerary optimization    (Groupement géographique, gestion de la fatigue, plan B météo)
   │
   ▼ [Barrière Synchrone 3]
[ Vague 4 : Porte de Sécurité & Contrôle Qualité ]
   └── 9. Quality control           (Validation de cohérence, audit de preuve, audit URLs anti-phishing)
   │
   ▼ [Barrière Synchrone 4]
[ Vague 5 : Synthèse & Dossier Final ]
   └── Travel orchestrator          (Compilation du dossier Markdown, exports, fiches d'urgence)
```

---

## 2. Les 9 Étapes Métier Détaillées

### 1. Destination Research (`destination-researcher`)
- **Rôle** : Identifier le contexte géographique, la saisonnalité touristique et les périodes creuses d'affluence.
- **Hypothèses** : Horaires d'ouverture réguliers et conditions météo de saison.
- **Sortie** : Fiche destination avec anecdotes locales et conseils de créneaux paisibles.

### 2. Transport Planning (`transport-planner`)
- **Rôle** : Planifier les trajets porte-à-porte (aller, retour, étapes intermédiaires) en intégrant les marges de transit réalistes (30 min pour TGV, 120 min pour vols).
- **Règle budgétaire** : Différencie automatiquement les transports facturés au passager (train, avion, métro) des véhicules collectifs (voiture de location, taxi).

### 3. Accommodation Research (`accommodation-researcher`)
- **Rôle** : Sélectionner des hébergements bien situés, favorisant les quartiers résidentiels calmes plutôt que les artères hyper-touristiques bruyantes.
- **Contrôle** : Couvre rigoureusement 100% des nuitées du séjour.

### 4. Activity Curation (`activity-curator`)
- **Rôle** : Sélectionner les visites et monuments en modélisant 26 dimensions clés (anecdotes, accessibilité PMR, créneaux d'ouverture, billetteries officielles et stratégies pour éviter les files d'attente).
- **Anti-foule** : Ciblage des ouvertures matinales (08h30-09h30) ou des fins d'après-midi.

### 5. Local Discovery (`local-discovery-agent`)
- **Rôle** : Dénicher des adresses culinaires authentiques (marchés couverts, bistrots de quartier).
- **Transparence** : Ces adresses sont obligatoirement étiquetées `community_recommended` ou `social_discovery_only` pour alerter le voyageur sur la nécessité de vérifier les jours d'ouverture.

### 6. Travel Preparation (`travel-preparation-agent`)
- **Rôle** : Construire la trousse de préparation administrative et médicale (validité des passeports, assurances, cartes hors-ligne).
- **Notice légale** : Les informations dépendantes de la nationalité portent la mention *« Requires official source verification. »*.

### 7. Budget Analysis (`budget-analyst`)
- **Rôle** : Calculer le montant prévisionnel consolidé en intégrant une réserve de sécurité (+10% à +12% pour un city-trip, +15% pour un road-trip).
- **Alertes** : Détection automatique des dépassements du plafond fixé par l'utilisateur.

### 8. Itinerary Optimization (`itinerary-optimizer`)
- **Rôle** : Répartir les activités sur chaque journée en évitant les allers-retours inutiles dans la ville (groupement géographique par corridor de marche).
- **Pacing** : Limitation à 2-3 visites majeures par jour en rythme équilibré, et 1 seule en rythme détendu, avec temps de déjeuner Sanctuarisé (60 à 75 minutes).

### 9. Quality Control (`quality-controller` & `mcp-skill-auditor`)
- **Contrôle de cohérence** : Vérification des dates, des liaisons référentielles et du respect des règles de sécurité.
- **Audit de sécurité** : Vérification de chaque URL de billetterie pour éliminer les liens suspects ou réducteurs d'URL opaques.
- **Garantie zéro achat** : Vérification qu'aucun mécanisme de paiement automatique n'est actif.

---

## 3. Génération des Plans B et de la Trousse de Préparation

En complément de l'itinéraire nominal, le système synthétise automatiquement :
1. **La checklist avant départ** (échéances à J-30, J-15, J-7, J-2).
2. **La checklist des réservations obligatoires** avec les liens directs des opérateurs.
3. **La liste des documents d'identité et sanitaires à vérifier**.
4. **Le plan B météo** identifiant une alternative couverte pour chaque visite en plein air.
5. **Le plan B en cas de fermeture** imprévue d'un site touristique majeur.
6. **La liste des points critiques à confirmer avant de payer** (annulation gratuite, franchise bagage, caution par carte de crédit).
7. **La fiche d'urgence générique** rappelant les procédures de crise sans jamais inventer de coordonnées médicales ou diplomatiques fictives.
