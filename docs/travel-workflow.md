# Flux de travail multi-agents

Le planificateur utilise un graphe dynamique fondé sur les dépendances du voyage. Les domaines non applicables sont marqués `skipped` avec une raison ; ils ne déclenchent pas un agent inutile.

```text
Brief minimal
  └─► graphe de dépendances + propriétaires des claims + registre des sources demandées
       ├─► destination ───────────────┐
       ├─► transport / flight-search ├─► dates et zones viables
       ├─► activités générales ──────┘          │
       └─► sécurité si applicable               ├─► hébergement
                                                ├─► découverte locale
                                                └─► activités datées
                                                        │
                      vérification ciblée ◄──────────────┘
                               │
                          budget → itinéraire → contrôle qualité
                                                   │
                                      une synthèse TravelDossier v1
```

## Contrats d’exécution

- Chaque famille de claims possède un seul spécialiste responsable.
- Chaque agent reçoit uniquement son fragment de brief, ses obligations, les IDs nécessaires et son propre shard d’artefacts.
- Les recherches complètes restent dans `.travel-agent/runs/<run_id>/`; les messages utilisent `compact-handoff/v2`.
- Plusieurs consommateurs réutilisent le même `source_id` actuel au lieu de rouvrir la page.
- Une reprise n’exécute que les cellules `pending`, expirées, contredites ou invalidées.
- `validate-handoff` contrôle chaque transition et `validate-dossier` contrôle le résultat final.

## Portes de décision

Les quatre portes sont indépendantes :

1. `coverage_complete` : toutes les cellules requises ont un état terminal.
2. `evidence_sufficient` : les candidats et preuves qualifiées sont suffisants.
3. `recommendation_ready` : les alternatives sont comparables et les conflits matériels résolus.
4. `booking_ready` : tous les claims critiques sont actuels, primaires et sans bloqueur.

`pending: 0` ne suffit donc jamais à rendre un dossier réservable.

## Responsabilités

- Destination : géographie, climat, événements, affluence, normes et contexte régional.
- Transport : matrices de vols, rail, bus, ferry, conduite, correspondances et coûts porte-à-porte.
- Hébergement : quartiers, mobilité vers les vrais points d’intérêt, chambre/tarif comparable, coût final et annulation.
- Activités : couverture thématique, créneaux, accessibilité, files, réservation et plans B compatibles.
- Découverte locale : candidats de quartier, recherches multilingues, récence, provenance et existence.
- Sécurité : applicabilité par nationalité/résidence/juridiction/date, exigences, recommandations, risques et revalidation.
- Budget : coûts atomiques, exposition remboursable, scénarios corrélés et réserve fondée sur le risque.
- Itinéraire : contraintes temporelles, trajets sourcés, charge, marge, variantes et récupération.
- Vérification : claims critiques, périmés, manquants ou contradictoires uniquement.
- Contrôle qualité : structure, calcul, faisabilité, preuve et red-team des défaillances plausibles.

L’auditeur MCP n’intervient que lorsqu’un composant externe est proposé. Il ne fait pas partie d’un planning de voyage ordinaire.
