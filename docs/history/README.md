# Archives Historiques et Documents Pré-Pivot — `ultimate-travel-agent`

Ce dossier regroupe les documents de recherche initiale, les modèles de données legacy et les spécifications techniques antérieures au **Pivot Skills-First (Phase 11)**.

## Contexte
Au cours des premières phases de développement (Phases 0 à 10), le projet a exploré différentes architectures :
- Un moteur local en Python avec adaptateurs de providers mock/live (`integrations/`) ;
- Un serveur MCP distant avec distribution HTTP, conteneurisation Docker et déploiements cloud ;
- Des schémas de données stricts JSON Schema v7 (`data/schemas/`) pour manipuler des fichiers `trip.json`.

À compter de la **Phase 11**, le projet s'est recentré exclusivement sur un **Travel Skills Pack** autonome, local-first et sans dépendance API obligatoire (`.agents/skills`, `.agents/agents`, `.agents/workflows` et `packages/travel-skills`).

Les documents contenus ici sont conservés strictement à titre de référence historique, méthodologique et architecturale :
- **`research/`** : Travaux préparatoires de la Phase 0 (exigences, matrice de sources, audit de compétences externes, patterns d'orchestration multi-agents).
- **`data/`** : Schémas JSON Schema v7 et anciens jeux de données d'exemples pré-pivot.
- **Documents d'audit et de configuration pré-pivot** : Audits des phases 9 et 10, spécifications des adaptateurs providers, documentation de déploiement cloud et interface web expérimentale.
