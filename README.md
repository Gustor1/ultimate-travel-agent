# Ultimate Travel Agent

[![M8ven Score](https://m8ven.ai/badge/mcp/gustor1-ultimate-travel-agent-dboc4d?v=67c79fb9bddeb27e2f85b347c35535cb)](https://m8ven.ai/mcp/gustor1-ultimate-travel-agent-dboc4d)

Ultimate Travel Agent est un pack portable de **14 skills de voyage**, accompagné
d'une CLI déterministe et d'un serveur MCP optionnel. Le serveur expose les mêmes
validateurs, calculs et connecteurs bornés ; il ne constitue ni une interface web ni
un moteur de réservation. Les prix, horaires, formalités et disponibilités doivent
toujours être vérifiés sur des sources officielles avant toute décision.

## Où se trouve le produit

| Chemin | Rôle |
|---|---|
| [`.agents/skills/`](.agents/skills/) | Les 14 skills canoniques |
| [`.agents/shared/`](.agents/shared/) | Contrats communs, preuves, cache et handoffs compacts |
| [`.agents/agents/`](.agents/agents/) | Définitions optionnelles des spécialistes |
| [`.agents/workflows/`](.agents/workflows/) | Workflows optionnels de bout en bout |
| [`src/ultimate_travel_agent/`](src/ultimate_travel_agent/) | Outils déterministes optionnels : validation, calculs et installation |
| [`src/ultimate_travel_agent/mcp/`](src/ultimate_travel_agent/mcp/) | Adaptateur MCP stdio optionnel, schémas et dispatch sécurisé |
| [`evals/`](evals/) | Evals déterministes de déclenchement des skills |
| [`tests/`](tests/) | Tests de développement ; ils ne sont jamais chargés pendant un planning |

`.agents/` est l'unique source de vérité. Il n'existe plus de copie miroir du pack.

## Économie de tokens sans perte de recherche

- Un spécialiste ne charge que son `SKILL.md` et les références communes explicitement liées.
- Les recherches restent exhaustives grâce à des matrices de couverture et des états `searched`, `unavailable` ou `skipped`.
- Les preuves complètes sont écrites une seule fois dans des artefacts ; les agents échangent ensuite des IDs et des deltas via `compact-handoff/v2`.
- Les URLs sont normalisées et les sources identiques dédupliquées sans supprimer les preuves indépendantes.
- Les calculs, contrôles de couverture et validations sont confiés aux outils locaux au lieu d'être régénérés en texte par le modèle.
- Le cache est réutilisé selon une durée de validité adaptée à chaque type de donnée ; les faits volatils sont revérifiés.

Voir [la méthode détaillée](docs/token-efficiency.md).

## Utilisation rapide

Dans Codex Desktop, ouvrez ce dossier puis demandez un planning. Les fichiers `AGENTS.md` et `.agents/` orientent l'agent vers le minimum de contexte nécessaire.

Pour installer le pack dans un autre projet :

```bash
python -m pip install -e .
ultimate-travel-agent install-skills --target /chemin/du/projet --include-agents --include-workflows
```

Installation publiée, sans dépendances MCP :

```bash
python -m pip install ultimate-travel-agent
```

Installation avec le SDK et lancement du serveur MCP stdio :

```bash
python -m pip install "ultimate-travel-agent[mcp]"
ultimate-travel-agent-mcp
```

Par défaut, les opérations fichier MCP sont limitées au répertoire courant. Définissez
`ULTIMATE_TRAVEL_AGENT_MCP_ROOT` sur un répertoire local explicite pour choisir une
autre racine. La suite automatisée vérifie réellement `initialize`, `tools/list` et
`tools/call` avec un client MCP stdio.

L'hôte cible doit relier les capacités déclarées par les skills à ses propres outils de recherche et à son modèle de permissions. Les mêmes fichiers restent utilisables avec Claude, Codex et d'autres agents ; seule cette couche d'adaptation dépend de la plateforme.

Commandes utiles :

```bash
ultimate-travel-agent list-skills
ultimate-travel-agent validate-skills
ultimate-travel-agent validate-handoff handoff.yaml
ultimate-travel-agent validate-dossier dossier.yaml
ultimate-travel-agent prompt-audit
```

La désinstallation est non destructive pour les fichiers modifiés par l'utilisateur :

```bash
ultimate-travel-agent uninstall-skills --target /chemin/du/projet
```

Guides : [installation](docs/install-in-any-project.md), [installation en français](docs/install-in-any-project.fr.md), [catalogue](docs/skills-catalog.md), [catalogue en français](docs/skills-catalog.fr.md).

## Skills

- Recherche : `travel-web-research`, `flight-search`, `transport-research`, `accommodation-research`, `activity-curator`, `local-discovery`.
- Construction : `itinerary-builder`, `budget-and-booking-checker`, `travel-safety`.
- Contrôle : `source-verification`, `travel-quality-control`.
- Coordination : `travel-orchestrator`, `multi-agent-orchestration`, `mcp-skill-auditing`.

## Documentation essentielle

- [Architecture](docs/architecture.md)
- [Workflow de voyage](docs/travel-workflow.md)
- [Politique de sources](docs/source-verification.md)
- [TravelDossier v1](docs/travel-dossier-v1.md)
- [Sécurité](docs/security-model.md)
- [Limites connues](docs/known-limitations.md)

Les modèles de brief français et anglais sont dans [`examples/`](examples/). Les autres fichiers de ce dossier sont uniquement des fixtures de validation des outils déterministes.

## Développement

```bash
python -m pip install -e ".[dev,mcp]"
pytest -q
ruff check src tests
mypy src/ultimate_travel_agent
python -m evals.run_skill_evals
```

## Effets et confidentialité

- Les calculs et validations restent locaux et read-only.
- `profile-save`, `export-dossier`, les générateurs de plans avec `output_path` et les
  commandes d'installation écrivent uniquement sous la racine MCP configurée.
- `uninstall-skills` est le seul tool destructif ; il reste borné par son manifeste.
- `connector-read` utilise uniquement GET. `connector-fetch` conserve GET/POST pour
  compatibilité et est donc annoncé comme potentiellement mutatif à distance.
- `notify-webhook` envoie un POST signé. Aucun tool n'effectue d'achat ou de réservation.
- Les secrets proviennent exclusivement de variables d'environnement et ne sont ni
  inclus dans les résultats ni journalisés.

Le tableau complet des 30 tools et de leurs annotations est dans
[la documentation MCP](docs/mcp-tool-annotations.md).

Les tests et le code Python ne sont pas injectés dans les prompts de voyage. Ils servent à empêcher les régressions de précision, de sécurité et de couverture.

Licence [MIT](LICENSE).
