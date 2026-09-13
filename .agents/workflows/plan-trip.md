# Workflow : Plan Trip (`plan-trip.md`)

Ce workflow orchestre le cycle complet de planification d'un voyage à travers les 5 vagues multi-agents du système.

---

## Entrées Requises
- Profil du voyageur (`traveler_profile`)
- Destination souhaitée (`destination`)
- Dates de séjour (`start_date`, `end_date`)
- Plafond budgétaire indicatif (`budget_cap`, optionnel)

---

## Étapes d'Exécution

```
[Brief Utilisateur]
       │
       ▼
[VAGUE 1 : Exploration Parallèle]
├── destination-researcher -> Climat, saisons idéales, anecdotes
├── transport-planner      -> Liaisons train/vol, temps porte-à-porte, liens officiels
├── accommodation-researcher -> Quartiers calmes, hébergements par nuitée
├── activity-curator       -> Visites phares, créneaux calmes, météo de secours
├── local-discovery-agent  -> Adresses culinaires (marquées unverified/social)
└── travel-prep-agent      -> Checklist administrative, CEAM, contacts urgence
       │
       ▼
[VAGUE 2 : Consolidation Budgétaire]
└── budget-analyst         -> Somme itemisée, réserve de 10-15%, alerte plafond
       │
       ▼
[VAGUE 3 : Ordonnancement Chronologique]
└── itinerary-optimizer    -> Planning jour par jour, clustering géographique
       │
       ▼
[VAGUE 4 : Contrôle Qualité et Sécurité]
├── quality-controller     -> Cohérence nuitées/dates, faisabilité des temps
└── mcp-skill-auditor      -> Audit liste blanche des URLs, anti-injection
       │
       ▼
[VAGUE 5 : Synthèse & Dossier Final]
└── travel-orchestrator    -> Compilation du dossier de voyage Markdown/JSON
```

---

## Sorties Produites
- Fichier `trip.json` validé
- Rapport complet de voyage en Markdown
- Synthèse des niveaux de vérification et actions réservées à l'humain
