# Ultimate Travel Agent

[![M8ven Score](https://m8ven.ai/badge/mcp/gustor1-ultimate-travel-agent-dboc4d?v=67c79fb9bddeb27e2f85b347c35535cb)](https://m8ven.ai/mcp/gustor1-ultimate-travel-agent-dboc4d)

Pack portable de skills pour planifier des voyages réalistes, vérifiables et adaptés aux contraintes réelles. Ultimate Travel Agent combine des instructions d’orchestration pour agents IA, des outils Python déterministes et un serveur MCP optionnel.

> [!IMPORTANT]
> Le projet prépare et contrôle des décisions de voyage ; il n’achète aucun billet, ne réserve aucun hébergement et ne remplace pas la vérification finale auprès des sources officielles.

## Ce que le projet apporte

- Recherche spécialisée pour les destinations, transports, hébergements, activités, spécialités culinaires et spots photo ; comparaison détaillée des vols quand elle est demandée ou détermine le trajet.
- Itinéraires construits à partir de fenêtres d’ouverture, temps de trajet, énergie, météo et contraintes de budget.
- Preuves sourcées, règles de fraîcheur et contrôles de couverture pour limiter les recommandations invérifiables.
- Calculs locaux pour les coûts porte-à-porte, la mobilité, les perturbations, les variantes de journée et les décisions de groupe.
- Handoffs compacts `compact-handoff/v2` et dossier structuré `TravelDossier v1` pour coordonner plusieurs spécialistes sans recopier tout le contexte.
- Installation du pack dans un autre projet, avec validation et désinstallation bornée.

## Architecture

`.agents/` est la source de vérité unique du pack :

| Répertoire | Contenu |
| --- | --- |
| `.agents/skills/` | 14 skills de voyage |
| `.agents/agents/` | 12 définitions de spécialistes |
| `.agents/workflows/` | 9 workflows prêts à suivre |
| `.agents/shared/` | Protocoles, schémas, cache et références conditionnelles |
| `src/ultimate_travel_agent/` | CLI, contrats, validateurs et calculs déterministes |
| `src/ultimate_travel_agent/mcp/` | Adaptateur MCP stdio optionnel |

Le wheel Python embarque les assets `.agents/`, ce qui permet d’installer le pack sans dépendre d’un checkout Git. Le serveur MCP est une fine couche stdio : il valide les enveloppes, applique les limites de fichiers et appelle directement les fonctions Python existantes.

## Démarrage rapide

Prérequis : Python 3.10 ou plus récent.

```bash
git clone https://github.com/Gustor1/ultimate-travel-agent.git
cd ultimate-travel-agent
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell : .venv\Scripts\Activate.ps1
python -m pip install -e .
```

Pour utiliser le projet comme environnement de développement :

```bash
python -m pip install -e ".[dev,mcp]"
pytest -q
```

Dans Codex, Claude ou un autre agent compatible, ouvrez ensuite le dossier et donnez votre brief de voyage. `AGENTS.md` et `.agents/` orientent automatiquement l’agent vers le workflow et les références nécessaires.

## Installer le pack dans un autre projet

```bash
python -m pip install ultimate-travel-agent
ultimate-travel-agent install-skills \
  --target /chemin/du/projet \
  --include-agents \
  --include-workflows
```

La désinstallation respecte les fichiers modifiés par l’utilisateur :

```bash
ultimate-travel-agent uninstall-skills --target /chemin/du/projet
```

## CLI

```bash
ultimate-travel-agent list-skills
ultimate-travel-agent validate-skills
ultimate-travel-agent validate-dossier dossier.yaml
ultimate-travel-agent validate-handoff handoff.yaml
ultimate-travel-agent prompt-audit
```

La CLI inclut également des plans de recherche et de revalidation, la comparaison d’hôtels et de coûts totaux, l’optimisation d’itinéraire, la gestion des perturbations, la préparation d’un handoff de réservation et des connecteurs JSON bornés.

Afficher toutes les commandes :

```bash
ultimate-travel-agent --help
```

## Serveur MCP

Le serveur MCP est optionnel et n’est pas installé avec les dépendances de base :

```bash
python -m pip install "ultimate-travel-agent[mcp]"
ultimate-travel-agent-mcp
```

Par défaut, les opérations fichier MCP restent limitées au répertoire courant. Pour choisir explicitement une autre racine locale, définissez `ULTIMATE_TRAVEL_AGENT_MCP_ROOT`.

Les outils sensibles sont annotés et bornés : aucun achat ni aucune réservation n’est exécuté. Les secrets proviennent uniquement des variables d’environnement et ne sont ni renvoyés dans les résultats ni journalisés.

## Les 14 skills

**Recherche** : `travel-web-research`, `flight-search`, `transport-research`, `accommodation-research`, `activity-curator`, `local-discovery`.

**Construction** : `itinerary-builder`, `budget-and-booking-checker`, `travel-safety`.

**Contrôle** : `source-verification`, `travel-quality-control`.

**Coordination** : `travel-orchestrator`, `multi-agent-orchestration`, `mcp-skill-auditing`.

Le workflow complet suit généralement cette séquence : brief et contraintes → dates et étapes provisoires → activités et découvertes locales sourcées → transports utiles et hébergement → budget disponible ou explicitement non coté → itinéraire → contrôle qualité → `TravelDossier v1`.

## Documentation

- [Guide de démarrage](docs/getting-started.md)
- [Workflow de voyage](docs/travel-workflow.md)
- [Architecture](docs/architecture.md)
- [Catalogue des skills](docs/skills-catalog.md) · [version française](docs/skills-catalog.fr.md)
- [Efficacité des tokens](docs/token-efficiency.md)
- [Politique de vérification des sources](docs/source-verification.md)
- [TravelDossier v1](docs/travel-dossier-v1.md)
- [Modèles de brief](examples/)

## Développement

```bash
python -m pip install -e ".[dev,mcp]"
pytest -q
ruff check src tests
mypy src/ultimate_travel_agent
python -m evals.run_skill_evals
```

Les tests et le code Python servent à vérifier les contrats, la sécurité, la couverture et la précision du pack ; ils ne sont pas injectés dans les prompts de voyage.
