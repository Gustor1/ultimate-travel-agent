# Audit Complet de Nettoyage du Dépôt Public — `ultimate-travel-agent`

Date : 2026-09-13
Dépôt concerné : `https://github.com/Gustor1/ultimate-travel-agent` (public)
Statut de l'audit : Pré-nettoyage et purge des composants externes

---

## 1. Contexte et Problématique

Lors des phases initiales de recherche et d'expérimentation (Phases 0 et 0-bis), de nombreux composants tiers (compétences *skills*, sous-agents, frameworks et scripts issus notamment de Swarms, cc-system, Vooster et Agentic-Awesome-Skills) ont été téléchargés localement pour analyse comparative.

Par inadvertance, ces éléments externes ont été introduits dans :
1. `.agents/skills/` (39 skills externes tierces non spécifiques au voyage).
2. `research/external-candidates/` (141 fichiers de code source, scripts shell/python et prompts de dépôts tiers).

Ces fichiers ont été committés et poussés sur le dépôt public GitHub. Le présent audit détaille l'état exact du dépôt, catégorise chaque élément entre ce qui est légitime au projet `ultimate-travel-agent` et ce qui doit être supprimé, et définit la stratégie de purge locale et d'assainissement de l'historique distant.

---

## 2. Inventaire Détaillé des Fichiers Suivis par Git (360 fichiers)

### 2.1 `.agents/skills/` (45 dossiers, 106 fichiers)
Seules **6 skills** ont été conçues spécifiquement pour le moteur de voyage `ultimate-travel-agent` :
- `budget-validation/` : Validation financière, devises et marges de sécurité.
- `mcp-skill-auditing/` : Contrôle de sécurité, filtrage anti-injection et validation des URLs de billetterie.
- `multi-agent-orchestration/` : Ordonnancement déterministe en 5 vagues et gestion des dépendances par DAG.
- `source-verification/` : Hiérarchisation des 6 niveaux de preuve et recoupement de fiabilité.
- `travel-planning/` : Pacing, clustering géographique, réalisme porte-à-porte, plans pluie et "moins de personne".
- `travel-safety/` : Formalités consulaires, alertes sanitaires et numéros d'urgence.

**39 skills externes à purger impérativement :**
1. `accesslint-audit` (Audit accessibilité web externe)
2. `accesslint-scan` (Scan WCAG externe)
3. `activecampaign-automation` (Marketing/CRM externe)
4. `agent-creator` (Génération d'agents externe)
5. `agent-evaluation` (Framework de métrologie externe)
6. `agent-orchestration-improve-agent` (Optimisation d'agents externe)
7. `agent-orchestration-multi-agent-optimize` (Optimisation AAS externe)
8. `agent-orchestrator` (Méta-orchestrateur AAS externe)
9. `agentflow` (Pipeline Kanban Claude Code externe)
10. `agentic-actions-auditor` (Audit GitHub Actions externe)
11. `agents-generator` (Générateur AGENTS.md externe)
12. `agents-md` (Audit AGENTS.md externe)
13. `ai-agents-architect` (Guide architectural externe)
14. `antigravity-agent-manager` (Gestionnaire CLI externe)
15. `antigravity-design-expert` (UI/UX GSAP externe)
16. `antigravity-maintainer-batch-release` (Scripts release AAS externe)
17. `antigravity-skill-orchestrator` (Sélection de skills externe)
18. `antigravity-workflows` (Patrons de workflows externe)
19. `api-documenter` (OpenAPI docs externe)
20. `appium-skill` (Automatisation mobile externe)
21. `apple-container` (Conteneurs macOS externe)
22. `apple-notes-search` (Recherche Apple Notes externe)
23. `auto-research` (Recherche web externe)
24. `autonomous-agents` (Guide générique externe)
25. `cc-usage-audit` (Analyse prompts Claude Code externe)
26. `co-design` (Délégation frontend externe)
27. `commit` (Génération de commits externe)
28. `ideation` (Cadrage produit cc-system externe)
29. `parallel-task` (Orchestration Swarms externe)
30. `parallel-task-spark` (Swarms spark externe)
31. `parallel-task-tmux` (Swarms tmux externe)
32. `persuasion-review` (Simulation clients cc-system externe)
33. `plan-and-build` (Workflow dev cc-system externe)
34. `skill-creator` (Guide création skills externe)
35. `subagent-creator` (Créateur sous-agents externe)
36. `super-swarm` (Swarms agressif externe)
37. `super-swarm-spark` (Swarms spark externe)
38. `swarm-planner` (Planificateur Swarms externe)
39. `viral-generator-builder` (Outils viraux marketing externe)

### 2.2 `research/external-candidates/` (141 fichiers)
Contient l'intégralité des dépôts sources, scripts (`run-server.py`, `run-phases.py`, scripts tmux, harnais de simulation FCG) et prompts tiers téléchargés pour audit.
- **Action requise :** **Suppression intégrale** du dépôt Git. Les conclusions d'audit et les enseignements architecturaux sont d'ores et déjà synthétisés dans les rapports textuels de `research/`.

### 2.3 `.agents/agents/` (11 fichiers)
- `accommodation-researcher/agent.md`
- `activity-curator/agent.md`
- `budget-analyst/agent.md`
- `destination-researcher/agent.md`
- `itinerary-optimizer/agent.md`
- `local-discovery-agent/agent.md`
- `mcp-skill-auditor/agent.md`
- `quality-controller/agent.md`
- `transport-planner/agent.md`
- `travel-orchestrator/agent.md`
- `travel-preparation-agent/agent.md`
- **Action requise :** **Conserver à 100%**. Ce sont les 11 agents spécialisés du moteur de voyage.

### 2.4 `.agents/workflows/` (4 fichiers)
- `audit-external-component.md`
- `plan-trip.md`
- `research-destination.md`
- `validate-itinerary.md`
- **Action requise :** **Conserver à 100%**.

### 2.5 `research/` (Documents d'analyse du projet)
- `agent-architecture.md`
- `architecture-v1.md`
- `candidate-mcps.md`
- `candidate-skills.md`
- `external-components-audit.md` (Rapport textuel de synthèse, aucun code exécutable tiers)
- `multi-agent-orchestration-audit.md`
- `multi-agent-patterns.md` (Spécification d'architecture propre)
- `raw-notes.md` (Note brute utilisateur)
- `requirements.md`
- `risks-and-open-questions.md`
- `roadmap.md`
- `source-matrix.md`
- **Action requise :** **Conserver à 100%**. Ce sont des documents de cadrage originaux rédigés pour le projet.

### 2.6 Composants Applicatifs Cœur (`src/`, `tests/`, `examples/`, `docs/`, `data/`, configuration racine)
- **`src/` (35 fichiers)** : Modèles Pydantic v2, moteur d'orchestration 5 vagues, serveur MCP stdio, 10 adaptateurs de voyage, CLI et reporter.
- **`tests/` (6 fichiers)** : 41 tests unitaires et d'intégration validés.
- **`examples/` (6 fichiers)** : Scénarios City-Trip Barcelone et Road-Trip Islande, démo autonome.
- **`data/` (13 fichiers)** : 11 schémas JSON officiels et 2 exemples de voyage.
- **`docs/` (16 fichiers)** : Documentation complète d'architecture, guide de démarrage, format de données, sécurité, licences et checklist.
- **Racine** : `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `pyproject.toml`, `.gitignore`, `.env.example`, `.github/workflows/ci.yml`.
- **Action requise :** **Conserver à 100%**.

---

## 3. Matrice de Décision de Nettoyage

| Emplacement | Contenu | Action | Justification |
| :--- | :--- | :---: | :--- |
| `.agents/skills/[39 skills tierces]` | Outils dev, mobile, marketing, etc. | **Supprimer** | Hors périmètre du projet de voyage `ultimate-travel-agent`. |
| `.agents/skills/[6 skills voyage]` | Skills voyage, budget, sécurité, transport | **Conserver** | Cœur des compétences de voyage du système. |
| `.agents/agents/*` | 11 agents de voyage | **Conserver** | Définition des sous-agents du système. |
| `.agents/workflows/*` | 4 workflows de voyage | **Conserver** | Protocoles opératoires du système. |
| `research/external-candidates/` | 141 fichiers de code source tiers | **Supprimer** | Copies de dépôts externes inutiles sur le dépôt public. |
| `research/*.md` | 12 rapports d'audit et d'architecture | **Conserver** | Documentation de recherche originale du projet. |
| `src/`, `tests/`, `examples/`, `data/` | Code applicatif, tests, exemples | **Conserver** | Cœur du logiciel open-source. |
| `docs/*.md` | Documentation officielle du projet | **Conserver** | Guides et documentation utilisateur. |

---

## 4. Stratégie d'Assainissement et Réécriture Git

Pour que le dépôt public GitHub `Gustor1/ultimate-travel-agent` soit rigoureusement propre :
1. **Suppression locale** des 39 dossiers de skills externes dans `.agents/skills/`.
2. **Suppression locale** de l'arborescence `research/external-candidates/`.
3. **Mise à jour de `.gitignore`** pour empêcher tout ajout accidentel futur de répertoires de recherche de composants externes non désirés.
4. **Réécriture propre de l'historique Git** :
   - Plutôt que de conserver des commits massifs contenant des dizaines de milliers de lignes tierces désormais orphelines dans l'historique Git, réinitialiser la branche `main` sur une base saine et professionnelle contenant exclusivement les fichiers du projet.
5. **Vérification de la suite de tests** (`pytest`) pour s'assurer que le retrait de ces dossiers externes n'a aucun impact sur le code applicatif (100% autonome).
6. **Force-push sécurisé** sur `origin/main` vers `https://github.com/Gustor1/ultimate-travel-agent`.
7. **Contrôle post-déploiement** via l'API GitHub (vérification de la liste des fichiers et relance de la CI).
