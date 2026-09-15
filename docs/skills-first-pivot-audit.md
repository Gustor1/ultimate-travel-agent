# Skills-First Pivot Audit

## Éléments à conserver sur main
- `.agents/` (skills, agents, workflows)
- `packages/travel-skills/`
- `examples/`
- `docs/`
- `research/`
- `data/` (schémas et exemples utiles)
- `src/` (seulement si nécessaire au pack/installateur)
- `tests/`
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`

## Éléments à améliorer
- Révision des 11 sous-agents pour ne plus utiliser d'APIs internes mais les skills.
- Standardisation de toutes les skills (frontmatter, structure, repli sans web_search, politique de sécurité).
- Refonte des workflows pour un parcours purement "agent autonome" sans dépendances externes.
- Création de nouveaux briefs utilisateurs.

## Éléments à archiver et retirer de la branche principale
- Serveur MCP HTTP distant et authentification.
- Fichiers Docker, docker-compose.yml.
- Déploiements (Railway, Render, Fly.io, Cloud Run).
- Provider Hub (adaptateurs commerciaux, API de vols, hôtels, activités, etc.).
- Web UI (FastAPI).

## Expérimentation MCP/API
- Tout ce qui concerne la fourniture de données via API et hébergement complexe restera sur la branche `archive/mcp-api-prototype-v1.2` en tant qu'expérimentation historique.
- L'audit des MCP (`mcp-skill-auditor`) reste une skill locale facultative.

## Fonctionnalités sans navigateur
- Construction et optimisation de l'itinéraire.
- Vérification du budget (estimations).
- Génération de checklist et préparation.
- Contrôle qualité et validation.

## Fonctionnalités nécessitant impérativement web/navigateur
- Recherche de vols, transports, hôtels et activités avec tarifs réels.
- Vérification des heures d'ouverture, règles d'entrée, statuts en direct.
- Toute donnée exigeant une source Tier 1 / Tier 2 à jour.
